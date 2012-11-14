'''
Created on Jun 8, 2011

@package: ally api
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the types used for APIs.
'''

from .. import type_legacy as numbers
from ..support.util import Uninstantiable, Singletone
from ..type_legacy import Iterable
from .model import Content
from datetime import datetime, date, time
from inspect import isclass
from abc import ABCMeta
import abc

# --------------------------------------------------------------------

_classType = {}
# Dictionary having as a key the class and as a value the type of that class.

# --------------------------------------------------------------------

class Type(metaclass=abc.ABCMeta):
    '''
    The class that represents the API types used for mapping data.
    '''

    __slots__ = ('__weakref__', 'isPrimitive', 'isContainable')

    def __init__(self, isPrimitive=False, isContainable=True):
        '''
        Initializes the type setting the primitive aspect of the type.
        
        @param isPrimitive: boolean
            If true than this type is considered of a primitive nature, meaning that is an boolean, integer,
            string, float ... .
        @param isContainable: boolean
            If true than this type is containable in types like List and Count.
        '''
        assert isinstance(isPrimitive, bool), 'Invalid is primitive flag %s' % isPrimitive
        assert isinstance(isContainable, bool), 'Invalid is containable flag %s' % isContainable
        self.isPrimitive = isPrimitive
        self.isContainable = isContainable

    @abc.abstractclassmethod
    def isOf(self, type):
        '''
        Checks if the provided type is compatible with this type.
        
        @param typ: Type|class 
            The type to check.
        @return: boolean
            True if the type is of this type, False otherwise.
        '''

    @abc.abstractclassmethod
    def isValid(self, obj):
        '''
        Checks if the provided object instance is represented by this API type.
        
        @param obj: object
            The object instance to check.
        '''

    @abc.abstractclassmethod
    def __hash__(self):
        '''
        Provides the hash code for the type.
        '''

    @abc.abstractclassmethod
    def __eq__(self, other):
        '''
        Equality check.
        '''

    @abc.abstractclassmethod
    def __str__(self):
        '''
        The string representation.
        '''

class TypeNone(Singletone, Type):
    '''
    Provides the type that matches None.
    '''

    __slots__ = ()

    def __init__(self):
        '''
        @see: Type.__init__
        '''
        Type.__init__(self, False, False)

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

    def __hash__(self):
        '''
        @see: Type.__hash__
        '''
        return hash(None)

    def __eq__(self, other):
        '''
        @see: Type.__eq__
        '''
        return other is self

    def __str__(self):
        '''
        @see: Type.__str__
        '''
        return 'None'

class TypeClass(Type):
    '''
    The class that represents the API types used for mapping data.
    '''

    __slots__ = ('clazz',)

    def __init__(self, clazz, isPrimitive=False, isContainable=True):
        '''
        Initializes the type setting the primitive aspect of the type.
        @see: Type.__init__
        
        @param clazz: class
            The class represented by the type.
        '''
        assert isclass(clazz), 'Invalid class %s' % clazz
        Type.__init__(self, isPrimitive, isContainable)

        self.clazz = clazz

    def isOf(self, type):
        '''
        Checks if the provided type is compatible with this type.
        
        @param type: Type|class 
            The type to check.
        @return: boolean
            True if the type is of this type, False otherwise.
        '''
        if isclass(type) and issubclass(type, self.clazz): return True
        if self == typeFor(type): return True
        return False

    def isValid(self, obj):
        '''
        Checks if the provided object instance is represented by this API type.
        
        @param obj: object
                The object instance to check.
        '''
        return isinstance(obj, self.clazz)

    def __hash__(self):
        '''
        @see: Type.__hash__
        '''
        return hash(self.clazz)

    def __eq__(self, other):
        '''
        @see: Type.__eq__
        '''
        if isinstance(other, self.__class__): return self.clazz == other.clazz
        return False

    def __str__(self):
        '''
        @see: Type.__str__
        '''
        return '%s' % self.clazz.__name__

class TypePercentage(Singletone, TypeClass):
    '''
    Provides the type for percentage values.
    '''

    __slots__ = ()

    def __init__(self):
        '''
        Constructs the percentage type.
        @see: TypeClass.__init__
        '''
        TypeClass.__init__(self, float, True)

# --------------------------------------------------------------------
# Specific types tagging creating known value that extend normal types

#TODO: check if needed for automatic translation or not.
class TypeTranslated(Singletone, TypeClass):
    '''
    Provides the string type that contains as a value a message that should be translated.
    '''

    __slots__ = ()

    def __init__(self):
        '''
        Constructs the translated type.
        @see: TypeClass.__init__
        '''
        TypeClass.__init__(self, str, True, True)

class TypeReference(Singletone, TypeClass):
    '''
    Provides the type representing a reference path.
    '''

    __slots__ = ()

    def __init__(self):
        '''
        Constructs the reference path type.
        @see: TypeClass.__init__
        '''
        TypeClass.__init__(self, str, True, True)

class TypeLocale(Singletone, TypeClass):
    '''
    Provides the type representing the user requested language for presentation.
    '''

    __slots__ = ()

    def __init__(self):
        '''
        Constructs the front language type.
        @see: TypeClass.__init__
        '''
        TypeClass.__init__(self, str, False, True)

class TypeScheme(Singletone, TypeClass):
    '''
    Provides the type representing the used scheme.
    '''

    __slots__ = ()

    def __init__(self):
        '''
        Constructs the schema type.
        @see: TypeClass.__init__
        '''
        TypeClass.__init__(self, str, False, False)

# --------------------------------------------------------------------

class Iter(TypeClass):
    '''
    Maps an iterator of values.
    You need also to specify in the constructor what elements this iterator will contain.
    Since the values in an iterator can only be retrieved once than this type when validating the iterator it will
    not be able to validate also the elements.
    '''

    __slots__ = ('itemType',)

    def __init__(self, itemType):
        '''
        Constructs the iterator type for the provided item type.
        @see: TypeClass.__init__
        
        @param itemType: Type|class
            The item type of the iterator.
        '''
        itemType = typeFor(itemType)
        assert isinstance(itemType, Type), 'Invalid item type %s' % itemType
        assert itemType.isContainable, 'Invalid item type %s because is not containable' % itemType
        self.itemType = itemType
        TypeClass.__init__(self, Iterable, False, False)

    def isOf(self, type):
        '''
        @see: Type.isOf
        '''
        if super().isOf(type): return True
        return self.itemType.isOf(type)

    def __hash__(self):
        '''
        @see: Type.__hash__
        '''
        return hash(self.itemType)

    def __eq__(self, other):
        '''
        @see: Type.__eq__
        '''
        if isinstance(other, self.__class__): return self.itemType == other.itemType
        return False

    def __str__(self):
        '''
        @see: Type.__str__
        '''
        return '%s[%s]' % (self.__class__.__name__, self.itemType)

class List(Iter):
    '''
    Maps lists of values.
    You need also to specify in the constructor what elements this list will contain.
    Unlike the iterator type the list type also validates the contained elements.
    '''

    __slots__ = ()

    def __init__(self, itemType):
        '''
        Constructs the list type for the provided type.
        @see: Iter.__init__
        '''
        Iter.__init__(self, itemType)
        self.clazz = list
        self.isPrimitive = self.itemType.isPrimitive

    def isValid(self, obj):
        '''
        @see: Type.isValid
        '''
        if isinstance(obj, (tuple, list)): return all(map(self.itemType.isValid, obj))
        return False

# --------------------------------------------------------------------

class Input:
    '''
    Provides an input entry for a call, this is used for keeping the name and also the type of a call parameter.
    '''

    __slots__ = ('name', 'type', 'hasDefault', 'default')

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

    def __hash__(self):
        return hash((self.name, self.type))

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.name == other.name and self.type == other.type
        return False

    def __str__(self):
        return '%s=%s[%s:%s]' % (self.name, self.type, self.hasDefault, self.default)

# --------------------------------------------------------------------

class Non(Uninstantiable):
    '''
    Maps the None type.
    '''
_classType[Non] = TypeNone()

class Boolean(Uninstantiable):
    '''
    Maps the boolean values.
    Only used as a class, do not create an instance.
    '''
_classType[Boolean] = _classType[bool] = TypeClass(bool, True)

class Integer(Uninstantiable, int):
    '''
    Maps the integer values.
    Only used as a class, do not create an instance.
    '''
_classType[Integer] = _classType[int] = TypeClass(int, True)

class Number(Uninstantiable, float):
    '''
    Maps the numbers, this includes integer and float.
    Only used as a class, do not create an instance.
    '''
_classType[Number] = _classType[numbers.Number] = _classType[float] = TypeClass(numbers.Number, True)

class Percentage(Uninstantiable, float):
    '''
    Maps the percentage numbers.
    Only used as a class, do not create an instance.
    '''
_classType[Percentage] = TypePercentage()

class String(Uninstantiable, str):
    '''
    Maps the string values.
    Only used as a class, do not create an instance.
    '''
_classType[String] = _classType[str] = TypeClass(str, True)

class Date(Uninstantiable, date):
    '''
    Maps the date time values.
    Only used as a class, do not create an instance.
    '''
_classType[Date] = _classType[date] = TypeClass(date, True)

class Time(Uninstantiable, time):
    '''
    Maps the date time values.
    Only used as a class, do not create an instance.
    '''
_classType[Time] = _classType[time] = TypeClass(time, True)

class DateTime(Uninstantiable, datetime):
    '''
    Maps the date time values.
    Only used as a class, do not create an instance.
    '''
_classType[DateTime] = _classType[datetime] = TypeClass(datetime, True)

# --------------------------------------------------------------------
# Specific types tagging creating known value that extend normal types

#TODO: check if needed for automatic translation or not.
class Translated(Uninstantiable, str):
    '''
    Maps the type representing the translated messages.
    Only used as a class, do not create an instance.
    '''
_classType[Translated] = TypeTranslated()

class Reference(Uninstantiable, str):
    '''
    Maps the type representing the reference path.
    Only used as a class, do not create an instance.
    '''
_classType[Reference] = TypeReference()

# Provides the request raw content type.
_classType[Content] = TypeClass(Content, False, False)

class Locale(Uninstantiable, str):
    '''
    Maps the type representing the user requested locale for presentation.
    Only used as a class, do not create an instance.
    '''
_classType[Locale] = TypeLocale()

class Scheme(Uninstantiable, str):
    '''
    Maps the type representing the scheme.
    Only used as a class, do not create an instance.
    '''
_classType[Scheme] = TypeScheme()

# --------------------------------------------------------------------

class TypeSupportMeta(ABCMeta):
    '''
    Meta class for type support that allows for instance check base on the '_ally_type' attribute.
    '''

    def __instancecheck__(self, instance):
        '''
        @see: ABCMeta.__instancecheck__
        '''
        if ABCMeta.__instancecheck__(self, instance): return True
        if self is not TypeSupport: return False
        return isinstance(getattr(instance, '_ally_type', None), Type)

class TypeSupport(metaclass=TypeSupportMeta):
    '''
    Class that provides the support for containing types.
    '''
    __slots__ = ('_ally_type',)

    def __init__(self, type):
        '''
        Construct the type support with the provided type.
        
        @param type: Type
            The type of the support.
        '''
        assert isinstance(type, Type), 'Invalid type %s' % type
        self._ally_type = type # This specified the detected type by using 'typeFor'

def typeFor(obj):
    '''
    Provides the type of the object. The type extraction is performed as follow:
        - if the object is a class then search in the _classType for the associated type, return None if not found.
        - in case is not a class then check if the _ally_type attribute exists and provide the type, None otherwise.
    
    @param obj: object|class
        The class or object to extract the type.
    @return: Type|None
        The obtained type or None if there is not type.
    '''
    if isinstance(obj, Type): return obj
    if obj is not None:
        try: return obj._ally_type
        except AttributeError: pass

        try:
            return _classType.get(obj)
        except TypeError:
            return None
