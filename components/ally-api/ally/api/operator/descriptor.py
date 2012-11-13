'''
Created on Mar 13, 2012

@package: ally api
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the operator descriptors for the APIs.
'''

from ..type import typeFor, Type, TypeSupport
from .type import TypeContainer, TypeCriteriaEntry, TypeProperty, TypeQuery
from abc import ABCMeta
from ally.api.operator.container import Query, Container
from ally.api.operator.type import TypeCriteria
from ally.exception import DevelError
from ally.support.util_spec import IGet, IContained, ISet, IDelete
from ally.support.util_sys import getAttrAndClass
import logging

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

class Reference(TypeSupport):
    '''
    Provides the property reference that is provided by the property descriptor.
    '''

    __slots__ = ('_ally_ref_parent',)

    def __init__(self, type, parent=None):
        '''
        Constructs the container property descriptor.
        
        @param type: TypeProperty
            The property type represented by the property.
        '''
        assert isinstance(type, TypeProperty), 'Invalid property type %s' % type
        assert parent is None or isinstance(parent, TypeSupport), \
        'Invalid parent %s, needs to be a type support' % parent
        TypeSupport.__init__(self, type)

        self._ally_ref_parent = parent

    def __getattr__(self, name):
        '''
        Provides the contained container properties.
        
        @param name: string
            The property to get from the contained container.
        '''
        assert isinstance(name, str), 'Invalid name %s' % name
        typ = self._ally_type.type
        if isinstance(typ, TypeContainer):
            assert isinstance(typ, TypeContainer)
            return Reference(typ.childTypeFor(name), self)
        raise AttributeError('\'%s\' object has no attribute \'%s\'' % (self.__class__.__name__, name))

    def __hash__(self):
        return hash(self._ally_type)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self._ally_type == other._ally_type
        return False

    def __repr__(self):
        r = []
        if self._ally_ref_parent:
            r.append(str(self._ally_ref_parent))
            r.append('->')
        r.append(str(self._ally_type))
        r.append('(')
        r.append(str(self._ally_type.type))
        r.append(')')
        return ''.join(r)

class Property(IGet, IContained, ISet, IDelete):
    '''
    Provides the descriptor for the model properties. It contains the operation that need to be applied on a model
    object that relate to this property. The property also has a reference that will be returned whenever the property
    is used only with the model class.
    '''
    __slots__ = ('type',)

    def __init__(self, type):
        '''
        Constructs the model property descriptor.
        
        @param type: TypeProperty
            The property type represented by the property.
        '''
        assert isinstance(type, TypeProperty), 'Invalid property type %s' % type

        self.type = type

    def __get__(self, obj, clazz=None):
        '''
        @see: IGet.__get__
        '''
        if obj is None:
            assert self.type.parent.isOf(clazz), 'Illegal class %s, expected %s' % (clazz, self.type.parent)
            assert issubclass(clazz, ContainerSupport), 'Invalid container class %s' % clazz
            return clazz._ally_reference.get(self.type.property)
        else:
            assert isinstance(obj, ContainerSupport), 'Invalid container object %s' % obj
            assert self.type.parent.isValid(obj), 'Invalid container object %s, expected %s' % (obj, self.type.parent)
            return obj._ally_values.get(self.type.property)

    def __contained__(self, obj):
        '''
        @see: IContained.__contained__
        '''
        assert isinstance(obj, ContainerSupport), 'Invalid container object %s' % obj
        assert self.type.parent.isValid(obj), 'Invalid container object %s, expected %s' % (obj, self.type.parent)
        return self.type.property in obj._ally_values

    def __set__(self, obj, value):
        '''
        @see: ISet.__set__
        '''
        assert isinstance(obj, ContainerSupport), 'Invalid container object %s' % obj
        assert self.type.parent.isValid(obj), 'Invalid container object %s, expected %s' % (obj, self.type.parent)
        obj._ally_values[self.type.property] = value
        assert log.debug('Success on setting value (%s) for %s', value, self) or True

    def __delete__(self, obj):
        '''
        @see: IDelete.__delete__
        '''
        assert isinstance(obj, ContainerSupport), 'Invalid container object %s' % obj
        assert self.type.parent.isValid(obj), 'Invalid container object %s, expected %s' % (obj, self.type.parent)
        if self.type.property in obj._ally_values:
            del obj._ally_values[self.type.property]
            assert log.debug('Success on removing value for %s', self) or True

    def __hash__(self):
        return hash(self.type)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.type == other.type
        return False

    def __str__(self):
        return str(self.type)

# --------------------------------------------------------------------

class CriteriaEntry(TypeSupport):
    '''
    Descriptor used for defining criteria entries in a query object.
    '''
    __slots__ = ()

    def __init__(self, type):
        '''
        Construct the criteria entry descriptor.
        
        @param type: TypeCriteriaEntry
            The criteria entry type represented by the criteria entry descriptor.
        '''
        assert isinstance(type, TypeCriteriaEntry), 'Invalid criteria entry type %s' % type
        TypeSupport.__init__(self, type)

    def __get__(self, obj, clazz=None):
        '''
        Provides the value represented by this criteria entry for the provided query object.
        
        @param obj: object
            The query object to provide the value for, None provides the criteria entry.
        @param clazz: class
            The query class from which the criteria originates from, can be None if the object is provided.
        @return: object
            The value of the criteria or the criteria entry if used only with the class.
        '''
        if obj is None:
            assert self._ally_type.parent.isOf(clazz), \
            'Illegal class %s, expected %s' % (clazz, self._ally_type.parent)
            return self
        else:
            assert isinstance(obj, QuerySupport), 'Invalid query object %s' % obj
            assert self._ally_type.parent.isValid(obj), \
            'Invalid container object %s, expected %s' % (obj, self._ally_type.parent)
            objCrit = obj._ally_values.get(self._ally_type.name)
            if objCrit is None:
                objCrit = self._ally_type.clazz(queryObj=obj, criteriaName=self._ally_type.name)
                obj._ally_values[self._ally_type.name] = objCrit
                assert log.debug('Created criteria object for %s', self) or True
            return objCrit

    def __contained__(self, obj):
        '''
        Checks if the entry is contained in the provided object. This is an artifact from the __contains__ method 
        that is found on the actual model object.
        
        @param obj: object
            The object to check if the entry is contained in.
        @return: boolean
            True if the entry is contained in the object, false otherwise.
        '''
        assert isinstance(obj, QuerySupport), 'Invalid container object %s' % obj
        assert self._ally_type.parent.isValid(obj), 'Invalid query object %s, expected %s' % (obj, self._ally_type.parent)
        return self._ally_type.name in obj._ally_values

    def __set__(self, obj, value):
        '''
        Set the value on the main criteria property, if the represented criteria does not expose a main property that this
        set method will fail.
        
        @param obj: object
            The query object to set the value to.
        @param value: object
            The value to set, needs to be valid for the main property.
        '''
        assert isinstance(obj, QuerySupport), 'Invalid query object %s' % obj
        assert self._ally_type.parent.isValid(obj), \
        'Invalid container object %s, expected %s' % (obj, self._ally_type.parent)
        main = self._ally_type.criteria.main
        if not main:
            raise ValueError('Cannot set value for %s because the criteria %s has no main property' % 
                             (self, self._ally_type.criteria))
        obj = self.__get__(obj)
        for prop in main: setattr(obj, prop, value)

    def __delete__(self, obj):
        '''
        Remove the criteria represented by this criteria entry from the provided query object.
        
        @param obj: object
            The query object to remove the value from.
        '''
        assert isinstance(obj, QuerySupport), 'Invalid query object %s' % obj
        assert self._ally_type.parent.isValid(obj), \
        'Invalid container object %s, expected %s' % (obj, self._ally_type.parent)
        if self._ally_type.name in obj._ally_values:
            del obj._ally_values[self._ally_type.name]
            assert log.debug('Success on removing value for %s', self) or True

    def __getattr__(self, name):
        '''
        Provides the contained criteria properties.
        
        @param name: string
            The property to get from the contained criteria.
        '''
        return Reference(self._ally_type.childTypeFor(name), self)

    def __hash__(self):
        return hash(self._ally_type)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self._ally_type == other._ally_type
        return False

    def __str__(self):
        return str(self._ally_type)

# --------------------------------------------------------------------

ABCMeta = ABCMeta  # Just to get rid of the pydev warning of not used

class ContainerSupport(metaclass=ABCMeta):
    '''
    Support class for containers.
    '''
    _ally_type = TypeContainer  # Contains the type that represents the container
    _ally_reference = {}  # Provides the references for the property descriptors.

    def __new__(cls, *args, **keyargs):
        '''
        Construct the instance of the container.
        '''
        assert isinstance(cls._ally_type, TypeContainer), \
        'Bad container support class %s, no type assigned' % cls._ally_type
        assert cls._ally_type.isOf(cls), 'Illegal class %s, expected %s' % (cls, cls._ally_type)
        self = object.__new__(cls)
        self._ally_values = self.__dict__

        return self

    def __contains__(self, ref):
        '''
        Checks if the object contains a value for the property even if that value is None.
        
        @param ref: TypeProperty reference
            The type property to check.
        @return: boolean
            True if a value for the reference is present, false otherwise.
        '''
        typ = typeFor(ref)
        if not isinstance(typ, TypeProperty): return False
        assert isinstance(typ, TypeProperty)
        if typ.parent.isValid(self):
            descriptor, _clazz = getAttrAndClass(self.__class__, typ.property)
            if isinstance(descriptor, IContained):
                assert isinstance(descriptor, IContained)
                return descriptor.__contained__(self)
        return False

    def __str__(self):
        container = self._ally_type.container
        assert isinstance(container, Container), 'Invalid container %s' % container
        clazz = self.__class__
        s = [clazz.__name__, '[']
        for prop in container.properties:
            if self.__contains__(getattr(clazz, prop)):
                s.append(prop)
                s.append('=')
                s.append(str(getattr(self, prop)))
                s.append(',')
        if s[-1] == ',': del s[-1]  # Just remove the last comma
        s.append(']')
        return ''.join(s)

    @classmethod
    def __subclasshook__(cls, C):
        if cls is ContainerSupport:
            return isinstance(typeFor(C), TypeContainer)
        return NotImplemented

class CriteriaSupport(ContainerSupport):
    '''
    Support class for criterias.
    '''

    def __new__(cls, *args, queryObj, criteriaName, **keyargs):
        if queryObj is None or criteriaName is None:
            raise ValueError('The criteria can be created only within a query object')
        assert isinstance(criteriaName, str), 'Invalid criteria name %s' % criteriaName

        self = ContainerSupport.__new__(cls, *args, **keyargs)
        self._ally_query = queryObj
        self._ally_criteria = criteriaName

        return self

    @classmethod
    def __subclasshook__(cls, C):
        if cls is CriteriaSupport:
            return isinstance(typeFor(C), TypeCriteria)
        return NotImplemented

class QuerySupport(metaclass=ABCMeta):
    '''
    Support class for queries.
    '''
    _ally_type = TypeQuery  # Contains the type that represents the query

    def __new__(cls, *args, **keyargs):
        '''
        Construct the instance of the container.
        '''
        assert isinstance(cls._ally_type, TypeQuery), \
        'Bad query support class %s, no type assigned' % cls._ally_type
        assert cls._ally_type.isOf(cls), 'Illegal class %s, expected %s' % (cls, cls._ally_type)
        query = cls._ally_type.query
        assert isinstance(query, Query)

        self = object.__new__(cls)
        self._ally_values = {}

        for name, value in keyargs.items():
            if name not in query.criterias:
                raise DevelError('Invalid criteria name %r for %r' % (name, self))
            setattr(self, name, value)

        return self

    def __contains__(self, ref):
        '''
        Checks if the object contains a value for the property even if that value is None.
        
        @param ref: TypeCriteriaEntry|TypeProperty reference
            The type property to check.
        @return: boolean
            True if a value for the reference is present, false otherwise.
        '''
        typ = typeFor(ref)
        if isinstance(typ, TypeCriteriaEntry):
            assert isinstance(typ, TypeCriteriaEntry)
            if typ.parent.isValid(self):
                descriptor, _clazz = getAttrAndClass(self.__class__, typ.name)
                if isinstance(descriptor, IContained):
                    assert isinstance(descriptor, IContained)
                    return descriptor.__contained__(self)
        elif isinstance(typ, TypeProperty):
            # We do not need to make any recursive checking here since the criteria will only contain primitive properties
            # so there will not be the case of AQuery.ACriteria.AModel.AProperty the maximum is AQuery.ACriteria.AProperty
            try: typCrt = typeFor(ref._ally_ref_parent)
            except AttributeError: pass
            else:
                if isinstance(typCrt, TypeCriteriaEntry):
                    if typCrt.parent.isValid(self):
                        descriptor, _clazz = getAttrAndClass(self.__class__, typCrt.name)
                        if isinstance(descriptor, IContained) and isinstance(descriptor, IGet):
                            assert isinstance(descriptor, IContained)
                            assert isinstance(descriptor, IGet)
                            if descriptor.__contained__(self): return typ in descriptor.__get__(self)
        return False

    def __str__(self):
        query = self._ally_type.query
        assert isinstance(query, Query), 'Invalid query %s' % query
        clazz = self.__class__
        s = [clazz.__name__, '[']
        for crt in query.criterias:
            if self.__contains__(getattr(clazz, crt)):
                s.append(crt)
                s.append('=')
                s.append(str(getattr(self, crt)))
                s.append(',')
        if s[-1] == ',': del s[-1]  # Just remove the last comma
        s.append(']')
        return ''.join(s)

    @classmethod
    def __subclasshook__(cls, C):
        if cls is QuerySupport:
            return isinstance(typeFor(C), TypeQuery)
        return NotImplemented

# --------------------------------------------------------------------

def typesFor(ref):
    '''
    Provides the types of the provided references. This function provides a list of types that represent the references.
    
    ex:
        @model
        class Entity:
            Name = Integer
        
        @model
        class EntityContainer1:
            Entity = Entity
            
        @model
        class EntityContainer2:
            EntityContainer = EntityContainer1 
            
        typesOf(EntityContainer2.EntityContainer.Entity.Name) will return:
        [EntityContainer2.EntityContainer, EntityContainer1.Entity, Entity.Name]
    
    @param ref: object
        The reference object to provide the types for.
    @return: list[Type]
        The list of types of the reference.
    '''
    assert ref is not None, 'None is not a valid reference'
    types = []
    while ref:
        typ = typeFor(ref)
        assert isinstance(typ, Type), 'Invalid reference %s, has no type' % ref
        types.insert(0, typ)
        try: ref = ref._ally_ref_parent
        except AttributeError: ref = None
    return types
