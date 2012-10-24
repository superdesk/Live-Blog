'''
Created on Jun 12, 2012

@package: utilities
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the context support.
'''

from abc import ABCMeta
from ally.support.util import immut
from inspect import isclass

# --------------------------------------------------------------------

def defines(*types, doc=None):
    '''
    Construct a defining attribute for the context. The defines attribute means that the context can provide a value
    for the attribute, but is not mandatory also whenever managing an attribute if this type is a good idea to check
    if there aren't already values provided.
    
    @param types: arguments[class]
        The types of the defined attribute.
    @keyword doc: string
        The documentation associated with the attribute.
    '''
    return Attribute(DEFINED, types, doc)

def optional(*types, doc=None):
    '''
    Construct an optional attribute for the context. The optional attribute means that the context is valid even if
    there is no value for the attribute.
    
    @param types: arguments[class]
        The types of the optional attribute, the attribute value can be any one of the provided attributes.
    @keyword doc: string
        The documentation associated with the attribute.
    '''
    return Attribute(OPTIONAL, types, doc)

def requires(*types, doc=None):
    '''
    Construct a required attribute for the context. The requires attribute means that the context is valid only if
    there is a value for the attribute.
    
    @param types: arguments[class]
        The types of the required attribute, the attribute value can be any one of the provided attributes.
    @param doc: string
        The documentation associated with the attribute.
    '''
    return Attribute(REQUIRED, types, doc)

# --------------------------------------------------------------------

DEFINED = 1 << 1
# Status flag for defined attributes.
REQUIRED = 1 << 2
# Status flag for required attributes.
OPTIONAL = 1 << 3
# Status flag for optional attributes.

class Attribute:
    '''
    Defines a context attribute.
    '''
    __slots__ = ('locked', 'status', 'types', 'doc', 'name', 'clazz', 'descriptor')

    def __init__(self, status, types, doc=None):
        '''
        Construct the property.
        
        @param status: integer
            The status of the property.
        @param types: tuple(class)
            The type for the property.
        '''
        assert isinstance(status, int), 'Invalid status %s' % status
        assert isinstance(types, tuple), 'Invalid types %s' % types
        assert types, 'At least a type is required'
        if __debug__:
            for clazz in types: assert isclass(clazz), 'Invalid class %s' % clazz
        assert doc is None or isinstance(doc, str), 'Invalid documentation %s' % doc

        self.locked = False
        self.status = status
        self.types = types
        self.doc = doc

        self.name = None
        self.clazz = None
        self.descriptor = None

    def __setattr__(self, key, value):
        try: locked = self.locked
        except AttributeError: locked = False

        if not locked: object.__setattr__(self, key, value)
        else: raise AttributeError('Immutable attribute')

    # ----------------------------------------------------------------

    def __get__(self, obj, owner=None):
        '''
        Descriptor get.
        '''
        if obj is None: return self
        assert self.descriptor is not None, 'No descriptor available %s' % self.descriptor
        try: return self.descriptor.__get__(obj, owner)
        except AttributeError: return None

    def __set__(self, obj, value):
        '''
        Descriptor set.
        '''
        assert self.descriptor is not None, 'No descriptor available %s' % self.descriptor
        assert value is None or isinstance(value, self.types), 'Invalid value \'%s\' for %s' % (value, self.types)
        self.descriptor.__set__(obj, value)

    def __str__(self):
        status = []
        if self.status & DEFINED: status.append('DEFINES')
        if self.status & REQUIRED: status.append('REQUIRED')
        if self.status & OPTIONAL: status.append('OPTIONAL')

        return ''.join((self.__class__.__name__, '(', ':'.join(status), '=' , self.name or '', ':',
                        ','.join(type.__name__ for type in self.types), ')'))

ALLOWED = {'__module__', '__doc__', '__locals__'}
# The allowed attributes in a context class.
class ContextMetaClass(ABCMeta):
    '''
    Used for the context objects to behave like a data container only.
    The context can be checked against any object that has the specified attributes with values of the specified 
    classes instance.
    '''

    def __new__(cls, name, bases, namespace):
        if not bases: return super().__new__(cls, name, bases, namespace)

        attributes = {}
        for key, value in namespace.items():
            if key in ALLOWED: continue
            if not isinstance(value, Attribute):
                raise TypeError('Invalid attribute \'%s\' for name \'%s\'' % (value, key))
            attributes[key] = value

        namespace = {key:value for key, value in namespace.items() if key not in attributes}
        namespace['__slots__'] = tuple(attributes)

        self = super().__new__(cls, name, bases, namespace)

        for key, attribute in attributes.items():
            assert isinstance(attribute, Attribute)
            attribute.name = key
            attribute.clazz = self
            attribute.descriptor = getattr(self, key)
            attribute.locked = True
            setattr(self, key, attribute)

        # Adding also the parent attributes.
        for base in bases:
            if base is Context: continue
            if not isinstance(base, ContextMetaClass):
                raise TypeError('A context class can only inherit other context classes, invalid class %s' % base)
            assert isinstance(base, ContextMetaClass)
            attributes.update(base.__attributes__)

        self.__attributes__ = immut(attributes)

        return self

class Context(metaclass=ContextMetaClass):
    '''
    The base context class, this class needs to be inherited by all classes that need to behave like a data context.
    '''
    
    @classmethod
    def __subclasshook__(cls, C):
        if cls is Context: return Context in C.__mro__
        if isinstance(C, ContextMetaClass):
            assert isinstance(C, ContextMetaClass)

            for name, attr in cls.__attributes__.items():
                assert isinstance(attr, Attribute)

                if attr.status & DEFINED: continue
                oattr = C.__attributes__.get(name)
                if oattr is None:
                    if attr.status & REQUIRED: return False
                    continue

                assert isinstance(oattr, Attribute)

                for typ in attr.types:
                    if typ in oattr.types: break
                else: return False

            return True

        return NotImplemented

    def __init__(self, **keyargs):
        for name, value in keyargs.items(): setattr(self, name, value)

    def __contains__(self, attribute):
        if not isinstance(attribute, Attribute): return False
        assert isinstance(attribute, Attribute)
        owned = self.__attributes__.get(attribute.name)
        if owned is None: return False

        try: return isinstance(owned.descriptor.__get__(self), attribute.types)
        except AttributeError: return False

# --------------------------------------------------------------------

def asData(context, *classes):
    '''
    Provides the data that is represented in the provided context classes.
    
    @param context: object
        The context object to get the data from.
    @param classes: arguments[ContextMetaClass]
        The context classes to construct the data based on.
    '''
    assert isinstance(context, Context), 'Invalid context %s' % context

    data = {}
    for clazz in classes:
        assert isinstance(clazz, ContextMetaClass), 'Invalid context class %s' % clazz

        for name in clazz.__attributes__:
            attribute = context.__attributes__.get(name)
            if attribute in context: data[name] = attribute.__get__(context)

    return data
