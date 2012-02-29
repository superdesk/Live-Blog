'''
Created on Jun 8, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Nistor Gabriel

Provides the types used for APIs.
'''

from .. import type_legacy as numbers
from ..support.util import Uninstantiable, Singletone, Attribute, immutable
from ..type_legacy import Iterable, Sized, Iterator
from datetime import datetime, date, time
from inspect import isclass
import logging

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

_classType = {}
# Dictionary having as a key the class and as a value the type of that class.
formattedType = []
# The types that require formatting Uninstantiable classes

# --------------------------------------------------------------------

@immutable
class Type:
    '''
    The class that represents the API types used for mapping data.
    '''
    
    __slots__ = __immutable__ = ('forClass', 'isPrimitive', 'isContainable')
    
    def __init__(self, forClass, isPrimitive=False, isContainable=True):
        '''
        Initializes the type setting the primitive aspect of the type.
        
        @param isPrimitive: boolean
            If true than this type is considered of a primitive nature, meaning that is an boolean, integer,
            string, float ... .
        @param isContainable: boolean
            If true than this type is containable in types like List and Count.
        '''
        assert isclass(forClass), 'Invalid class %s' % forClass
        assert isinstance(isPrimitive, bool), 'Invalid is primitive flag %s' % isPrimitive
        assert isinstance(isContainable, bool), 'Invalid is containable flag %s' % isContainable
        self.forClass = forClass
        self.isPrimitive = isPrimitive
        self.isContainable = isContainable
        
    def isOf(self, type):
        '''
        Checks if the provided type is compatible with this type.
        
        @param typ: Type|class 
            The type to check.
        @return: boolean
            True if the type is of this type, False otherwise.
        '''
        if self == type: return True
        if isclass(type) and issubclass(type, self.forClass): return True
        if self == typeFor(type): return True
        return False

    def isValid(self, obj):
        '''
        Checks if the provided object instance is represented by this API type.
        
        @param obj: object
                The object instance to check.
        '''
        return isinstance(obj, self.forClass)
    
    def __hash__(self): return hash(self.forClass)
    
    def __eq__(self, other):
        if isinstance(other, self.__class__): return self.forClass == other.forClass
        return False
    
    def __str__(self): return self.forClass.__name__

class TypeNone(Singletone, Type):
    '''
    Provides the type that matches None.
    '''
    
    __slots__ = Type.__slots__
    
    def __init__(self):
        '''
        @see: Type.__init__
        '''
        self.isPrimitive = True
        self.forClass = None

    def isOf(self, type):
        '''
        @see: Type.isOf
        '''
        return self is type or type == None
    
    def isValid(self, obj):
        '''
        @see: Type.isValid
        '''
        return obj is None
    
    def __eq__(self, other):
        return other is self
    
    def __str__(self):
        return 'None'

class TypePercentage(Singletone, Type):
    '''
    Provides the type for percentage values.
    '''
    
    __slots__ = Type.__slots__
    
    def __init__(self):
        '''
        Constructs the percentage type.
        @see: Type.__init__
        '''
        Type.__init__(self, float, True)
        
# --------------------------------------------------------------------
# Id types

class TypeId(Type):
    '''
    Provides the type for the id. This type has to be a primitive type always.
    '''
    
    __slots__ = Type.__slots__
    
    def __init__(self, forClass):
        '''
        Constructs the id type for the provided class.
        @see: Type.__init__
        
        @param forClass: class
            The class that this type id is constructed on.
        '''
        Type.__init__(self, forClass, True)

# --------------------------------------------------------------------
# Specific types tagging creating known value that extend normal types
        
class TypeFrontLanguage(Singletone, Type):
    '''
    Provides the type representing the user requested language for presentation.
    '''
    
    __slots__ = Type.__slots__
    
    def __init__(self):
        '''
        Constructs the front language type.
        @see: Type.__init__
        '''
        Type.__init__(self, str, True)

# --------------------------------------------------------------------

class Iter(Type):
    '''
    Maps an iterator of values.
    You need also to specify in the constructor what elements this iterator will contain.
    Since the values in an iterator can only be retrieved once than this type when validating the iterator it will
    not be able to validate also the elements.
    '''
    
    __slots__ = __immutable__ = Type.__immutable__ + ('itemType',)
    
    def __init__(self, itemType):
        '''
        Constructs the iterator type for the provided item type.
        @see: Type.__init__
        
        @param itemType: Type|class
            The item type of the iterator.
        '''
        itemType = typeFor(itemType)
        assert isinstance(itemType, Type), 'Invalid item type %s' % itemType
        assert itemType.isContainable, 'Invalid item type %s because is not containable' % itemType
        self.itemType = itemType
        Type.__init__(self, itemType.forClass, itemType.isPrimitive, False)
    
    def isOf(self, type):
        '''
        @see: Type.isOf
        '''
        return self == type or self.itemType.isOf(type)

    def isValid(self, list):
        '''
        @see: Type.isValid
        '''
        return isinstance(list, Iterator) or isinstance(list, Iterable)
    
    def __hash__(self): return hash(self.itemType)
    
    def __eq__(self, other):
        if isinstance(other, self.__class__): return self.itemType == other.itemType
        return False
    
    def __str__(self): return '%s(%s)' % (self.__class__.__name__, self.itemType)
    
class List(Iter):
    '''
    Maps lists of values.
    You need also to specify in the constructor what elements this list will contain.
    Unlike the iterator type the list type also validates the contained elements.
    '''
    
    __slots__ = Iter.__slots__
    
    def __init__(self, itemType):
        '''
        Constructs the list type for the provided type.
        @see: Iter.__init__
        '''
        Iter.__init__(self, itemType)

    def isValid(self, list):
        '''
        @see: Type.isValid
        '''
        if Iter.isValid(self, list) and isinstance(list, Sized):
            return all(map(self.itemType.isValid, list))
        return False

# --------------------------------------------------------------------

class TypeModel(Type):
    '''
    Provides the type for the model.
    '''
    
    __slots__ = __immutable__ = Type.__immutable__ + ('model',)
    
    def __init__(self, model):
        '''
        Constructs the model type for the provided model.
        @see: Type.__init__
        
        @param model: Model
            The model that this type is constructed on.
        @param acceptPartial: boolean
            Flag indicating that partial forms of the represented model should be accepted.
        '''
        from .operator import Model
        assert isinstance(model, Model), 'Invalid model provided %s' % model
        self.model = model
        Type.__init__(self, model.modelClass)

class TypeQuery(Type):
    '''
    Provides the type for the query.
    '''
    
    __slots__ = __immutable__ = Type.__immutable__ + ('query',)
    
    def __init__(self, query):
        '''
        Constructs the query type for the provided query.
        @see: Type.__init__
        
        @param query: Query
            The query that this type is constructed on.
        '''
        from .operator import Query
        assert isinstance(query, Query), 'Invalid query provided %s' % query
        self.query = query
        Type.__init__(self, query.queryClass)

class TypeProperty(Type):
    '''
    This type is used to wrap model property as types. So whenever a type is provided based on a Model property
    this type will be used. Contains the type that is reflected based on the property type also contains the 
    Property and the Model that is constructed on. This type behaves as the type assigned to the property 
    and also contains the references to the property and model class.
    '''
    
    __slots__ = __immutable__ = Type.__immutable__ + ('model', 'property')
    
    def __init__(self, model, property):
        '''
        Constructs the property type for the provided property and model.
        @see: Type.__init__
        
        @param model: Model
            The model of the type.
        @param property: Property
            The property that this type is constructed on.
        '''
        from .operator import Property, Model
        assert isinstance(model, Model), 'Invalid model %s' % model
        assert isinstance(property, Property), 'Invalid property %s' % property
        self.model = model
        self.property = property
        Type.__init__(self, property.type.forClass, property.type.isPrimitive)
    
    def isOf(self, type):
        '''
        @see: Type.isOf
        '''
        return self == type or self.property.type.isOf(type)
    
    def isValid(self, obj):
        '''
        Checks if the provided object instance is represented by this API type.
        
        @param obj: object
                The object instance to check.
        '''
        return self.property.type.isValid(obj)
    
    def __hash__(self): return hash((self.model, self.property))
    
    def __eq__(self, other):
        if isinstance(other, self.__class__): return self.model == other.model and self.property == other.property
        return False

    def __str__(self): return '%s.%s' % (self.model.name, self.property.name)
    
class TypeCriteriaEntry(Type):
    '''
    This type is used to wrap query criteria as types. So whenever a type is provided based on a Query criteria
    this type will be used. Contains the type that is reflected based on the criteria entry type also contains the 
    CriteriaEntry and the Query that is constructed on. 
    '''
    
    __slots__ = __immutable__ = Type.__immutable__ + ('query', 'criteriaEntry')
    
    def __init__(self, query, criteriaEntry):
        '''
        Constructs the criteria entry type for the provided criteria entry and query.
        @see: Type.__init__
        
        @param query: Query
            The query of the type.
        @param criteriaEntry: CriteriaEntry
            The criteria entry that this type is constructed on.
        '''
        from .operator import CriteriaEntry, Query
        assert isinstance(query, Query), 'Invalid query %s' % query
        assert isinstance(criteriaEntry, CriteriaEntry), 'Invalid criteria entry %s' % criteriaEntry
        self.query = query
        self.criteriaEntry = criteriaEntry
        Type.__init__(self, criteriaEntry.type.forClass, criteriaEntry.type.isPrimitive)
    
    def isOf(self, type):
        '''
        @see: Type.isOf
        '''
        return self == type or self.criteriaEntry.type.isOf(type)
    
    def isValid(self, obj):
        '''
        Checks if the provided object instance is represented by this API type.
        
        @param obj: object
                The object instance to check.
        '''
        return self.criteriaEntry.type.isValid(obj)
    
    def __hash__(self): return hash((self.query, self.criteriaEntry))
    
    def __eq__(self, other):
        if isinstance(other, self.__class__): return self.query == other.query and \
        self.criteriaEntry == other.criteriaEntry
        return False

    def __str__(self): return '%s.%s' % (self.query.queryClass.__name__, self.criteriaEntry.name)

# --------------------------------------------------------------------

@immutable
class Input:
    '''
    Provides an input entry for a call, this is used for keeping the name and also the type of a call parameter.
    '''
    
    __slots__ = __immutable__ = ('name', 'type', 'hasDefault', 'default')
    
    def __init__(self, name, type, hasDefault=False, default=None):
        '''
        Construct the input.
        
        @param name: string
            The name of the input.
        @param type: Type
            The type of the input.
        @param hasDefault: boolean
            A flag indicating that this input has a default value.
        @param default: object
            The default value.
        '''
        assert isinstance(name, str), 'Invalid name %s' % name
        assert isinstance(type, Type), 'Invalid type %s' % type
        self.name = name
        self.type = type
        self.hasDefault = hasDefault
        self.default = default
        
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.name == other.name and self.type == other.type
        return False

    def __str__(self):
        return '%s=%s[%s:%s]' % (self.name, self.type, self.hasDefault, self.default)

# --------------------------------------------------------------------

ATTR_TYPE = Attribute(__name__, 'type', Type)
# Provides attribute for type.

def typeFor(obj, type=None):
    '''
    If the type is provided it will be associate with the obj, if the type is not provided than this function
    will try to provide if it exists the type associated with the obj, or check if the obj is not a type itself and
    provide that.
    
    @param obj: object
        The class to associate or extract the model.
    @param type: Type
        The type to associate with the obj.
    @return: Type|None
        If the type has been associate then the return will be none, if the type is being extracted it can return
        either the Type or None if is not found.
    '''
    if type is None:
        if obj is None: return ATTR_TYPE.get(Non)
        type = ATTR_TYPE.get(obj, None)
        if type is None:
            if isclass(obj):
                typ = _classType.get(obj)
                if typ is not None: return typ
            if isinstance(obj, Type): return obj
        return type
    assert not ATTR_TYPE.hasOwn(obj), 'Already has a type %s' % obj
    return ATTR_TYPE.set(obj, type)

# --------------------------------------------------------------------

class Non(Uninstantiable):
    '''
    Maps the None type.
    '''
typeFor(Non, TypeNone())

class Boolean(Uninstantiable):
    '''
    Maps the boolean values.
    Only used as a class, do not create an instance.
    '''
typeFor(Boolean, Type(bool, True))
_classType[bool] = typeFor(Boolean)


class Integer(Uninstantiable):
    '''
    Maps the integer values.
    Only used as a class, do not create an instance.
    '''
typeFor(Integer, Type(int, True))
_classType[int] = typeFor(Integer)

class Number(Uninstantiable):
    '''
    Maps the numbers, this includes integer and float.
    Only used as a class, do not create an instance.
    '''
typeFor(Number, Type(numbers.Number, True))
_classType[float] = typeFor(Number)
_classType[numbers.Number] = typeFor(Number)
formattedType.append(Number)

class Percentage(Uninstantiable):
    '''
    Maps the percentage numbers.
    Only used as a class, do not create an instance.
    '''
typeFor(Percentage, TypePercentage())
formattedType.append(Percentage)

class String(Uninstantiable):
    '''
    Maps the string values.
    Only used as a class, do not create an instance.
    '''
typeFor(String, Type(str, True))
_classType[str] = typeFor(String)

class Date(Uninstantiable):
    '''
    Maps the date time values.
    Only used as a class, do not create an instance.
    '''
typeFor(Date, Type(date, True))
_classType[date] = typeFor(Date)
formattedType.append(Date)

class Time(Uninstantiable):
    '''
    Maps the date time values.
    Only used as a class, do not create an instance.
    '''
typeFor(Time, Type(time, True))
_classType[time] = typeFor(Time)
formattedType.append(Time)

class DateTime(Uninstantiable):
    '''
    Maps the date time values.
    Only used as a class, do not create an instance.
    '''
typeFor(DateTime, Type(datetime, True))
_classType[datetime] = typeFor(DateTime)
formattedType.append(DateTime)

# --------------------------------------------------------------------
# Id types

class Id(Uninstantiable, int):
    '''
    Maps the integer id values.
    Only used as a class, do not create an instance.
    '''
typeFor(Id, TypeId(int))

class IdString(Uninstantiable):
    '''
    Maps the string id values.
    Only used as a class, do not create an instance.
    '''
typeFor(IdString, TypeId(str))

# --------------------------------------------------------------------
# Specific types tagging creating known value that extend normal types
    
class FrontLanguage(Uninstantiable):
    '''
    Maps the type representing the user requested language for presentation.
    Only used as a class, do not create an instance.
    '''
typeFor(FrontLanguage, TypeFrontLanguage())
