'''
Created on Feb 11, 2013

@package: ally base
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the attributes support.
'''

from .spec import IAttribute, AttrError, IResolver, Resolvers, ResolverError, \
    ContextMetaClass
from ally.support.util_spec import IGet, ISet
from ally.support.util_sys import locationStack
from collections import Iterable
from inspect import isclass
import logging

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

def defines(*types, doc=None):
    '''
    Construct a defining attribute for the context. The defines attribute means that the context can provide a value
    for the attribute, but is not mandatory also whenever managing an attribute if this type is a good idea to check
    if there aren't already values provided.
    
    @param types: arguments[class]
        The types of the defined attribute.
    @param doc: string|None
        The documentation associated with the attribute.
    '''
    return Attribute(DEFINED, types, doc=doc)

def definesIf(*types, doc=None):
    '''
    Construct a defining attribute for the context. The defines attribute means that the context can provide a value
    for the attribute, but is not mandatory also whenever managing an attribute if this type is a good idea to check
    if there aren't already values provided. Whenever using this type of attributes always check if the context has them since
    if they are optional they might not event be populated if there is no definition for them, so always to a check like:
        MyContext.myAttribute in myInstance
    , otherwise you might get attribute error.
    
    @param types: arguments[class]
        The types of the defined attribute.
    @param doc: string|None
        The documentation associated with the attribute.
    '''
    return Attribute(DEFINED | OPTIONAL, types, doc=doc)

def optional(*types, doc=None):
    '''
    Construct an optional attribute for the context. The optional attribute means that the context is valid even if
    there is no value for the attribute. Whenever using this type of attributes always check if the context has them since
    if they are optional they might not event be populated if there is no definition for them, so always to a check like:
        MyContext.myAttribute in myInstance
    , otherwise you might get attribute error.
    
    @param types: arguments[class]
        The types of the optional attribute, the attribute value can be any one of the provided attributes.
    @param doc: string|None
        The documentation associated with the attribute.
    '''
    return Attribute(OPTIONAL, types, doc)

def requires(*types, doc=None):
    '''
    Construct a required attribute for the context. The requires attribute means that the context is valid only if
    there is a value for the attribute.
    
    @param types: arguments[class]
        The types of the required attribute, the attribute value can be any one of the provided attributes.
    @param doc: string|None
        The documentation associated with the attribute.
    '''
    return Attribute(REQUIRED, types, doc=doc)

# --------------------------------------------------------------------

class Definition:
    '''
    Descriptor used just to provide the definition.
    '''
    __slots__ = ('__objclass__', '__name__')

    def __init__(self, clazz, name, types):
        '''
        Construct the definition.
        
        @param clazz: class
            The class of the definition.
        @param name: string
            The name of the attribute definition.
        '''
        assert isinstance(clazz, ContextMetaClass), 'Invalid class %s' % clazz
        assert isinstance(name, str), 'Invalid name %s' % name
        self.__objclass__ = clazz
        self.__name__ = name

    def __get__(self, obj, owner=None):
        '''
        Descriptor get.
        '''
        if obj is not None: raise TypeError('Operation not allowed')
        assert owner is None or owner == self.__objclass__, 'Invalid owner class %s expected %s' % (owner, self.__objclass__) 
        return self

    def __set__(self, obj, value):
        '''
        Descriptor set.
        '''
        raise TypeError('Operation not allowed')
        
class Descriptor:
    '''
    Descriptor used by the attribute in order to validate values.
    '''
    __slots__ = ('descriptor', 'types')

    def __init__(self, clazz, name, types):
        '''
        Construct the property.
        
        @param clazz: class
            The class of the descriptor.
        @param name: string
            The name of the attribute descriptor.
        @param types: tuple(class)
            The types to validate the values for.
        '''
        assert isclass(clazz), 'Invalid class %s' % clazz
        assert hasattr(clazz, name), 'Invalid class %s has no descriptor for %s' % (clazz, name)
        assert isinstance(types, tuple), 'Invalid types %s' % types
        assert types, 'At least a type is required'
        if __debug__:
            for typeClazz in types: assert isclass(typeClazz), 'Invalid type class %s' % typeClazz

        self.types = types
        self.descriptor = getattr(clazz, name)
        assert isinstance(self.descriptor, IGet), 'Invalid descriptor %s' % self.descriptor
        assert isinstance(self.descriptor, ISet), 'Invalid descriptor %s' % self.descriptor

    def __get__(self, obj, owner=None):
        '''
        Descriptor get.
        '''
        if obj is None: return self
        try: return self.descriptor.__get__(obj, owner)
        except AttributeError: return None

    def __set__(self, obj, value):
        '''
        Descriptor set.
        '''
        assert value is None or isinstance(value, self.types), 'Invalid value \'%s\' for %s' % (value, self.types)
        self.descriptor.__set__(obj, value)

# --------------------------------------------------------------------

DEFINED = 1 << 1
# Status flag for defined attributes.
REQUIRED = 1 << 2
# Status flag for required attributes.
OPTIONAL = 1 << 3
# Status flag for optional attributes.

class Attribute(IAttribute):
    '''
    Implementation for a @see: IAttribute that manages a attributes by status.
    '''
    __slots__ = ('status', 'types', 'doc', 'factory', '_clazz', '_name')

    def __init__(self, status, types, doc=None, factory=Definition):
        '''
        Construct the attribute.
        
        @param status: integer
            The status of the attribute.
        @param types: tuple(class)
            The type(s) for the attribute.
        @param doc: string|None
            The documentation associated with the attribute.
        @param factory: callable(class, string, tuple(class)) -> object
            The descriptor factory to use in creating the descriptors for the place command.
            The factory receives the class the attribute name and the types.
        '''
        assert isinstance(status, int), 'Invalid status %s' % status
        assert isinstance(types, tuple), 'Invalid types %s' % types
        assert types, 'At least a type is required'
        assert callable(factory), 'Invalid descriptor factory %s' % factory
        if __debug__:
            for clazz in types: assert isclass(clazz), 'Invalid class %s' % clazz
        
        self.status = status
        self.types = types
        self.doc = doc
        self.factory = factory
        self._clazz = None
        self._name = None
    
    def place(self, clazz, name):
        '''
        @see: IAttribute.place
        '''
        if self._clazz is None:
            assert isinstance(clazz, ContextMetaClass), 'Invalid class %s' % clazz
            assert isinstance(name, str), 'Invalid name %s' % name
            
            setattr(clazz, name, self.factory(clazz, name, self.types))
            self._clazz, self._name = clazz, name
        elif not issubclass(clazz, self._clazz):
            raise AttrError('%s\n, is already placed in %s' % (self, self._clazz))
        
    def push(self, name, resolvers):
        '''
        @see: IAttribute.push
        '''
        if self._clazz is None: raise AttrError('Attribute is not placed, so no definition class is available')
        resolver = Resolver(name, self._name, self.status, self.types, self.doc)
        resolver.usedIn[(self._clazz, self._name)] = self.status
        resolver.push(resolvers)
        
    def isValid(self, clazz):
        '''
        @see: IAttribute.isValid
        '''
        if self._clazz is None: return False
        assert isclass(clazz), 'Invalid class %s' % clazz
        
        if not isinstance(clazz, ContextMetaClass): return False
        assert isinstance(clazz, ContextMetaClass)
        
        other = clazz.__attributes__.get(self._name)
        if other is None:
            if self.status != REQUIRED: return True
            return False
        
        if not isinstance(other, Attribute): return False
        assert isinstance(other, Attribute)
        
        for typ in self.types:
            if typ in other.types: break
        else: return False
        
        return True
    
    def isIn(self, clazz):
        '''
        @see: IAttribute.isIn
        '''
        if self._clazz is None: return False
        assert isclass(clazz), 'Invalid class %s' % clazz
        
        if not isinstance(clazz, ContextMetaClass): return False
        assert isinstance(clazz, ContextMetaClass)
        
        other = clazz.__attributes__.get(self._name)
        if other is None: return False
        
        if not isinstance(other, Attribute): return False
        assert isinstance(other, Attribute)
        
        for typ in self.types:
            if typ in other.types: break
        else: return False
        
        return True
    
    def __str__(self):
        status = []
        if self.status & DEFINED: status.append('DEFINES')
        if self.status & REQUIRED: status.append('REQUIRED')
        if self.status & OPTIONAL: status.append('OPTIONAL')
        st = ''.join(('|'.join(status), '[', ','.join(t.__name__ for t in self.types), ']'))
        st = ''.join((self.__class__.__name__, ' having ', st))
        
        if self._clazz:
            return ''.join((st, ' in:', locationStack(self._clazz), ' as attribute ', self._name))
        return ''.join((st, ' unplaced'))

class Resolver(IResolver):
    '''
    Implementation for a @see: IResolver that manages a attributes by status.
    '''
    __slots__ = ('status', 'types', 'nameContext', 'nameAttribute', 'doc', 'defined', 'usedIn')

    def __init__(self, nameContext, nameAttribute, status, types, doc, defined=None):
        '''
        Construct the attribute resolver.
        
        @param name: string
            The context name for the resolver.
         @param status: integer
            The status of the resolver.
        @param types: tuple(class)
            The type for the resolver.
        @param doc: string|None
            The documentation associated with the resolver.
        @param defined: Iterable(class)|None
            The defined classes.
        '''
        assert isinstance(nameContext, str), 'Invalid context name %s' % nameContext
        assert isinstance(nameAttribute, str), 'Invalid attribute name %s' % nameAttribute
        assert isinstance(status, int), 'Invalid status %s' % status
        assert isinstance(types, tuple), 'Invalid types %s' % types
        assert types, 'At least a type is required'
        if __debug__:
            for clazz in types: assert isclass(clazz), 'Invalid class %s' % clazz
        
        if defined is None:
            if status & DEFINED: defined = types
            else: defined = ()
        else: assert isinstance(defined, Iterable), 'Invalid defined classes %s' % defined

        self.nameContext = nameContext
        self.nameAttribute = nameAttribute
        self.status = status
        self.types = types
        self.doc = doc
        self.defined = frozenset(defined)
        self.usedIn = {}
        
    def push(self, resolvers):
        '''
        @see: IResolver.push
        '''
        assert isinstance(resolvers, Resolvers), 'Invalid resolvers %s' % resolvers
        resolvers.add(self.nameContext, self.nameAttribute, self)
            
    def merge(self, other, isFirst=True):
        '''
        @see: IResolver.merge
        '''
        assert isinstance(other, IResolver), 'Invalid other resolver %s' % other
        assert isinstance(isFirst, bool), 'Invalid is first flag %s' % isFirst
        
        if self is other: return self
        
        if not isinstance(other, Resolver):
            if isFirst: return other.merge(self, False)
            raise ResolverError('Cannot merge %s with %s' % (self, other))
        assert isFirst, 'Is required to be first for merging'
        assert isinstance(other, Resolver)
        if self.nameContext != other.nameContext or self.nameAttribute != other.nameAttribute:
            raise ResolverError('Cannot merge %s with %s' % (self, other))
        
        if self.status == REQUIRED:
            if isFirst and other.status & DEFINED:
                raise AttrError('Improper order for %s, it should be before %s' % (other, self))
            status = REQUIRED
            types = set(self.types)
            types.intersection_update(other.types)
            if not types: raise AttrError('Incompatible required types of %s, with required types of %s' % (self, other))
                
        elif self.status == OPTIONAL:
            if other.status & DEFINED:
                status = DEFINED
                types = set(self.types)
            else:
                status = other.status
                types = set(self.types)
                types.intersection_update(other.types)
                if not types: raise AttrError('Incompatible required types of %s, with required types of %s' % (self, other))
            
        elif self.status & DEFINED:
            status = DEFINED
            if other.status & DEFINED: 
                types = set(self.types)
                types.update(other.types)
                # In case both definitions are optional we need to relate that to the merged attribute
                if self.status & OPTIONAL and other.status & OPTIONAL: status |= OPTIONAL
            else:
                types = set(other.types)
                
        defined = set(self.defined)
        defined.update(other.defined)
        if defined != types and not types.issuperset(defined):
            raise ResolverError('Invalid types %s and defined types %s, they cannot be joined, for %s, and %s' % 
                                (', '.join('\'%s\'' % typ.__name__ for typ in types),
                                 ', '.join('\'%s\'' % typ.__name__ for typ in defined), self, other))
        
        docs = []
        if self.doc is not None: docs.append(self.doc)
        if other.doc is not None: docs.append(other.doc)
        doc = '\n'.join(docs) if docs else None
        resolver = Resolver(self.nameContext, self.nameAttribute, status, tuple(types), doc, defined)
        resolver.usedIn.update(self.usedIn)
        resolver.usedIn.update(other.usedIn)
        
        return resolver
    
    def solve(self, other):
        '''
        @see: IResolver.solve
        '''
        assert isinstance(other, Resolver), 'Invalid other resolver %s' % other
        
        if self is other: return self
        
        if self.status & DEFINED: resolver = self.merge(other, True)
        else: resolver = other.merge(self, True)
            
        return resolver
    
    def isAvailable(self):
        '''
        @see: IResolver.isAvailable
        '''
        return self.status != REQUIRED
    
    def isUsed(self):
        '''
        @see: IResolver.isUsed
        '''
        if self.status & OPTIONAL: return True
        if len(self.usedIn) <= 1: return False
        for status in self.usedIn.values():
            if not status & DEFINED: return True
        return False
    
    def create(self, attributes):
        '''
        @see: IResolver.create
        '''
        assert isinstance(attributes, dict), 'Invalid attributes %s' % attributes
        if self.status == REQUIRED: raise AttrError('Resolver %s\n, cannot generate attribute' % self)
        if self.status & OPTIONAL: return  # If is optional then no need to create it
        if self.nameAttribute in attributes: return  # There is already an attribute
        attributes[self.nameAttribute] = Attribute(self.status, self.types, self.doc, Descriptor)
        
    def createDefinition(self, attributes):
        '''
        @see: IResolver.createDefinition
        '''
        assert isinstance(attributes, dict), 'Invalid attributes %s' % attributes
        if self.nameAttribute in attributes: return  # There is already an attribute
        attributes[self.nameAttribute] = Attribute(self.status, self.types, self.doc, Definition)

    def __str__(self):
        status = []
        if self.status & DEFINED: status.append('DEFINES')
        if self.status & REQUIRED: status.append('REQUIRED')
        if self.status & OPTIONAL: status.append('OPTIONAL')
        st = ''.join(('|'.join(status), '[', ','.join(t.__name__ for t in self.types), ']'))
        st = ''.join((self.__class__.__name__, ' having ', st))
        
        if self.usedIn:
            used = (clazzName for clazzName, status in self.usedIn.items() if status == self.status)
            used = ['%s as attribute \'%s\'' % (locationStack(clazz), name) for clazz, name in used]
            return ''.join((st, ' used in:', ''.join(used), '\n'))
        return ''.join((st, ' unused'))
