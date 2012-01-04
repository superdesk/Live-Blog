'''
Created on Jun 8, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Nistor Gabriel

Provides the types used for APIs.
'''

from .. import type_legacy as numbers
from ..type_legacy import Iterable, Sized, Iterator
from ..util import Uninstantiable, Singletone, Attribute
from datetime import datetime, date, time
from inspect import isclass
import logging

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

_TYPES = {}
FORMATTED = []
# The FORMATTED Uninstantiable classes

# --------------------------------------------------------------------

class Type:
    '''
    The class that represents the API types used for mapping data.
    '''
    
    def __init__(self, isPrimitive):
        '''
        Initializes the type setting the primitive aspect of the type.
        
        @param isPrimitive: boolean
            If true than this type is considered of a primitive nature, meaning that is an boolean, integer,
            string, float ... .
        '''
        self.isPrimitive = isPrimitive
        
    def forClass(self):
        '''
        Provides the basic class representation of the type.
        
        @return: class|None
            The class represented by the type, None if not available.
        '''
        raise NotImplementedError
        
    def isOf(self, typ):
        '''
        Checks if the provided type is compatible with this type.
        
        @param typ: Type|class 
        '''
        raise NotImplementedError

    def isValid(self, obj):
        '''
        Checks if the provided object instance is represented by this API type.
        
        @param obj: object
                The object instance to check.
        '''
        raise NotImplementedError

class TypeNone(Singletone, Type):
    '''
    Provides the type that matches None.
    '''
    def __init__(self):
        '''
        @see: Type.__init__
        '''
        Type.__init__(self, True)

    def forClass(self):
        '''
        @see: Type.forClass
        '''
        return None

    def isOf(self, typ):
        '''
        @see: Type.isOf
        '''
        return self == typ or typ == None
    
    def isValid(self, obj):
        '''
        @see: Type.isValid
        '''
        return obj is None
    
    def __eq__(self, other):
        return isinstance(other, TypeNone)
    
    def __str__(self):
        return 'None'

class TypeClass(Type):
    '''
    Provides type class validating based on the provided class.
    '''
    
    def __init__(self, forClass, isPrimitive=False):
        '''
        Initializes the type for the provided type class.
        @see: Type.__init__
        
        @param forClass:class
            The class to be checked if valid.
        '''
        assert isclass(forClass), 'Invalid class %s.' % forClass
        self._forClass = forClass
        Type.__init__(self, isPrimitive)

    def forClass(self):
        '''
        @see: Type.forClass
        '''
        return self._forClass

    def isOf(self, typ):
        '''
        @see: Type.isOf
        '''
        b = self._isOf(typ)
        if not b:
            typFor = typeFor(typ)
            if typFor:
                b = self == typFor
                if not b and isinstance(typFor, self.__class__):
                    b = typFor._isOf(self)
        return b
    
    def isValid(self, obj):
        '''
        @see: Type.isValid
        '''
        return isinstance(obj, self._forClass)
    
    def _isOf(self, typ):
        return self == typ or (isclass(typ) and issubclass(typ, self._forClass))
    
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self._forClass == other._forClass
        return False
    
    def __str__(self):
        return self._forClass.__name__

class TypePercentage(Singletone, TypeClass):
    '''
    Provides the type for percentage values.
    '''
    
    def __init__(self):
        '''
        Constructs the percentage type.
        @see: TypeClass.__init__
        '''
        TypeClass.__init__(self, float, True)
        
# --------------------------------------------------------------------
# Id types

class TypeId(TypeClass):
    '''
    Provides the type for the id. This type has to be a primitive type always.
    '''
    
    def __init__(self, forClass):
        '''
        Constructs the id type for the provided class.
        @see: TypeClass.__init__
        
        @param forClass: class
            The class that this type id is constructed on.
        '''
        TypeClass.__init__(self, forClass, True)

# --------------------------------------------------------------------
# Specific types tagging creating known value that extend normal types
        
class TypeFrontLanguage(Singletone, TypeClass):
    '''
    Provides the type representing the user requested language for presentation.
    '''
    
    def __init__(self):
        '''
        Constructs the percentage type.
        @see: TypeClass.__init__
        '''
        TypeClass.__init__(self, str, True)

# --------------------------------------------------------------------

class Iter(Type):
    '''
    Maps an iterator of values.
    You need also to specify in the constructor what elements this iterator will contain.
    Since the values in an iterator can only be retrieved once than this type when validating the iterator it will
    not be able to validate also the elements.
    '''
    
    def __init__(self, type):
        '''
        Constructs the iterator type for the provided type.
        @see: Type.__init__
        
        @param type: Type|class
            The type of the iterator.
        '''
        assert not isinstance(type, Iter), 'Invalid item type %s because is another iterable' % type
        self.itemType = typeFor(type)
        Type.__init__(self, False)
    
    def forClass(self):
        '''
        @see: Type.forClass
        '''
        return self.itemType.forClass()
    
    def isOf(self, typ):
        '''
        @see: Type.isOf
        '''
        return self == typ or self.itemType.isOf(typ)

    def isValid(self, list):
        '''
        @see: Type.isValid
        '''
        if isinstance(list, Iterator) or isinstance(list, Iterable):
            return True
        return False
    
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.itemType == other.itemType
        return False
    
    def __str__(self):
        return '%s(%s)' % (self.__class__.__name__, self.itemType)
    
class List(Iter):
    '''
    Maps lists of values.
    You need also to specify in the constructor what elements this list will contain.
    Unlike the iterator type the list type also validates the contained elements.
    '''
    
    def __init__(self, type):
        '''
        Constructs the list type for the provided type.
        @see: Iter.__init__
        '''
        Iter.__init__(self, type)
        

    def isValid(self, list):
        '''
        @see: Type.isValid
        '''
        if Iter.isValid(self, list) and isinstance(list, Sized):
            for obj in list:
                if not self.itemType.isValid(obj):
                    return False
            return True
        return False

# --------------------------------------------------------------------

class TypeModel(TypeClass):
    '''
    Provides the type for the model.
    '''
    
    def __init__(self, model):
        '''
        Constructs the model type for the provided model.
        @see: TypeClass.__init__
        
        @param model: Model
            The model that this type is constructed on.
        @param acceptPartial: boolean
            Flag indicating that partial forms of the represented model should be accepted.
        '''
        from .operator import Model
        assert isinstance(model, Model), 'Invalid model provided %s' % model
        self.model = model
        TypeClass.__init__(self, model.modelClass, False)

class TypeQuery(TypeClass):
    '''
    Provides the type for the query.
    '''
    
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
        TypeClass.__init__(self, query.queryClass, False)

class TypeProperty(Type):
    '''
    This type is used to wrap model property as types. So whenever a type is provided based on a Model property
    this type will be used. Contains the type that is reflected based on the property type also contains the 
    Property and the Model that is constructed on. This type behaves as the type assigned to the property 
    and also contains the references to the property and model class.
    '''
    
    def __init__(self, model, property):
        '''
        Constructs the model type for the provided property and model.
        @see: Type.__init__
        
        @param model: Model
            The model of the type.
        @param property: Property
            The property that this type is constructed on.
        '''
        from .operator import Property, Model
        assert isinstance(model, Model), 'Invalid model %s' % model
        assert isinstance(property, Property), 'Invalid property %s' % property
        assert isinstance(property.type, Type), 'Invalid property type %s' % type
        self.model = model
        self.property = property
        Type.__init__(self, property.type.isPrimitive)
    
    def forClass(self):
        '''
        @see: Type.forClass
        '''
        return self.property.type.forClass()
    
    def isOf(self, typ):
        '''
        @see: Type.isOf
        '''
        return self == typ or self.property.type.isOf(typ)
    
    def isValid(self, obj):
        '''
        Checks if the provided object instance is represented by this API type.
        
        @param obj: object
                The object instance to check.
        '''
        return self.property.type.isValid(obj)
        
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.model == other.model and self.property == other.property
        return False

    def __str__(self):
        return '%s.%s' % (self.model.name, self.property.name)

# --------------------------------------------------------------------

class Input:
    '''
    Provides an input entry for a call, this is used for keeping the name and also the type of a call parameter.
    '''
    
    def __init__(self, name, type):
        '''
        Construct the input.
        
        @param name: string
            The name of the input.
        @param type: Type
            The type of the input.
        '''
        assert isinstance(name, str), 'Invalid name %s' % name
        assert isinstance(type, Type), 'Invalid type %s' % type
        self.name = name
        self.type = type
        
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.name == other.name and self.type == other.type
        return False

    def __str__(self):
        return '%s=%s' % (self.name, self.type)

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
                typ = _TYPES.get(obj)
                if typ is not None: return typ
            if isinstance(obj, Type): type = obj
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
typeFor(Boolean, TypeClass(bool, True))
_TYPES[bool] = typeFor(Boolean)


class Integer(Uninstantiable):
    '''
    Maps the integer values.
    Only used as a class, do not create an instance.
    '''
typeFor(Integer, TypeClass(int, True))
_TYPES[int] = typeFor(Integer)

class Number(Uninstantiable):
    '''
    Maps the numbers, this includes integer and float.
    Only used as a class, do not create an instance.
    '''
typeFor(Number, TypeClass(numbers.Number, True))
_TYPES[float] = typeFor(Number)
_TYPES[numbers.Number] = typeFor(Number)
FORMATTED.append(Number)

class Percentage(Uninstantiable):
    '''
    Maps the percentage numbers.
    Only used as a class, do not create an instance.
    '''
typeFor(Percentage, TypePercentage())
FORMATTED.append(Percentage)

class String(Uninstantiable):
    '''
    Maps the string values.
    Only used as a class, do not create an instance.
    '''
typeFor(String, TypeClass(str, True))
_TYPES[str] = typeFor(String)

class Date(Uninstantiable):
    '''
    Maps the date time values.
    Only used as a class, do not create an instance.
    '''
typeFor(Date, TypeClass(date, True))
_TYPES[date] = typeFor(Date)
FORMATTED.append(Date)

class Time(Uninstantiable):
    '''
    Maps the date time values.
    Only used as a class, do not create an instance.
    '''
typeFor(Time, TypeClass(time, True))
_TYPES[time] = typeFor(Time)
FORMATTED.append(Time)

class DateTime(Uninstantiable):
    '''
    Maps the date time values.
    Only used as a class, do not create an instance.
    '''
typeFor(DateTime, TypeClass(datetime, True))
_TYPES[datetime] = typeFor(DateTime)
FORMATTED.append(DateTime)

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
