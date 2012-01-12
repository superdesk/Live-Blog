'''
Created on Jun 9, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides implementations that provide general behavior or functionality.
'''

from inspect import isclass
from threading import currentThread
import sys

# --------------------------------------------------------------------

# Flag indicating that the python version is 3k or more.
IS_PY3K = int(sys.version[:1]) >= 3

# --------------------------------------------------------------------

class Uninstantiable:
    '''
    Extending this class will not allow for the creation of any instance of the class.
    This has to be the first class inherited in order to properly work.
    '''
    
    def __new__(cls, *args, **keyargs):
        '''
        Does not allow you to create an instance.
        '''
        raise Exception('Cannot create an instance of %r class' % cls.__name__)

# --------------------------------------------------------------------

class Singletone:
    '''
    Extending this class will always return the same instance.
    '''
    
    def __new__(cls):
        '''
        Will always return the same instance.
        '''
        if not hasattr(cls, '_UTIL_singletone'):
            cls._UTIL_singletone = super().__new__(cls)
        return cls._UTIL_singletone

# --------------------------------------------------------------------

_attrNameIds = {}
# Used by the attribute to assign a unique id to a name.

attrIdForName = lambda name: str(_attrNameIds.setdefault(name, len(_attrNameIds)))
# Provides the name id.

class Attribute:
    '''
    Class used for creating attributes for python objects. The purpose of this is not to directly use the the __dict__
    or getattr in order to store values in order to avoid name clashes.
    '''
    
    def __init__(self, group, name, valueType=None):
        '''
        Creates a new attribute.
        
        @param group: string
            The group name for the attribute, this is usually the module name where is created, it helps to distinguish
            between same names but with other purposes.
        @param name: string
            The name of the attribute.
        @param valueType: type
            The type to check for the set and get values.
        '''
        assert isinstance(group, str), 'Invalid group name %s' % group
        assert isinstance(name, str), 'Invalid name %s' % name
        assert not valueType or isclass(valueType), 'Invalid value type %s' % valueType
        self.__group = group
        self.__name = name
        self.__type = valueType
        if __debug__: self.__id = group + '.' + name
        else:
            self.__id = attrIdForName(group) + '_' + attrIdForName(name)
    
    def has(self, obj):
        '''
        Checks if there is a value for the provided object.
        
        @param obj: object
            The object to check for value.
        @return: boolean
            true if there is a value, False otherwise.
        '''
        assert obj is not None, 'An object is required'
        return hasattr(obj, self.__id)
    
    def get(self, obj, *default):
        '''
        Get the value from the provided object.
        
        @param obj: object
            The object to get the value from.
        @param default: argument
            If provided will return the default if no argument value is available.
        @return: object
            The value.
        '''
        assert obj is not None, 'An object is required'
        value = getattr(obj, self.__id, *default)
        assert not(self.__type and value is not None) or isinstance(value, self.__type), 'Invalid value %s to get for ' \
        'required type %s, for attribute %s.%s' % (value, self.__type, self.__group, self.__name)
        return value
    
    def set(self, obj, value):
        '''
        Sets the value to the provided object.
        
        @param obj: object
            The object to set the value to.
        @param value: object
            The value to set.
        @return: object
            The provided value.
        '''
        assert obj is not None, 'An object is required'
        assert not(self.__type and value is not None) or isinstance(value, self.__type), 'Invalid value %s to set for ' \
        'required type %s, for attribute %s.%s' % (value, self.__type, self.__group, self.__name)
        setattr(obj, self.__id, value)
        return value
        
    def delete(self, obj):
        '''
        Deletes the value from the provided object.
        
        @param obj: object
            The object to delete the value from.
        '''
        assert obj is not None, 'An object is required'
        delattr(obj, self.__id)
        
    def hasOwn(self, obj):
        '''
        Checks if there is a value for the provided object by using __dict__.
        
        @param obj: object
            The object to check for value.
        @return: boolean
            true if there is a value, False otherwise.
        '''
        assert obj is not None, 'An object is required'
        return self.__id in obj.__dict__
    
    def getOwn(self, obj, *default):
        '''
        Get the value from the provided object by using __dict__.
        
        @param obj: object
            The object to get the value from.
        @param default: argument
            If provided will return the default if no argument value is available.
        @return: object
            The value.
        '''
        assert obj is not None, 'An object is required'
        value = obj.__dict__.get(self.__id, *default)
        assert not(self.__type and value is not None) or isinstance(value, self.__type), 'Invalid value %s to get for ' \
        'required type %s, for attribute %s.%s' % (value, self.__type, self.__group, self.__name)
        return value
    
    def setOwn(self, obj, value):
        '''
        Sets the value to the provided object by using __dict__.
        
        @param obj: object
            The object to set the value to.
        @param value: object
            The value to set.
        @return: object
            The provided value.
        '''
        assert obj is not None, 'An object is required'
        assert not(self.__type and value is not None) or isinstance(value, self.__type), 'Invalid value %s to set for ' \
        'required type %s, for attribute %s.%s' % (value, self.__type, self.__group, self.__name)
        obj.__dict__[self.__id] = value
        return value
        
    def deleteOwn(self, obj):
        '''
        Deletes the value from the provided object by using __dict__.
        
        @param obj: object
            The object to delete the value from.
        '''
        assert obj is not None, 'An object is required'
        del obj.__dict__[self.__id]
        
    def hasDict(self, map):
        '''
        Checks if there is a value for the provided map dictionary.
        
        @param map: dictionary
            The map dictionary to check for value.
        @return: boolean
            true if there is a value, False otherwise.
        '''
        assert isinstance(map, dict), 'Invalid map %s' % map
        return self.__id in map
    
    def getDict(self, map, *default):
        '''
        Get the value from the provided map dictionary.
        
        @param map: dictionary
            The map dictionary to get the value from.
        @param default: argument
            If provided will return the default if no argument value is available.
        @return: object
            The value.
        '''
        assert isinstance(map, dict), 'Invalid map %s' % map
        value = map.get(self.__id, *default)
        assert not(self.__type and value is not None) or isinstance(value, self.__type), 'Invalid value %s to get for ' \
        'required type %s, for attribute %s.%s' % (value, self.__type, self.__group, self.__name)
        return value
    
    def setDict(self, map, value):
        '''
        Sets the value to the provided map dictionary.
        
        @param map: dictionary
            The map dictionary to set the value to.
        @param value: object
            The value to set.
        @return: object
            The provided value.
        '''
        assert isinstance(map, dict), 'Invalid map %s' % map
        assert not(self.__type and value is not None) or isinstance(value, self.__type), 'Invalid value %s to set for ' \
        'required type %s, for attribute %s.%s' % (value, self.__type, self.__group, self.__name)
        map[self.__id] = value
        return value
        
    def deleteDict(self, map):
        '''
        Deletes the value from the provided map dictionary.
        
        @param map: dictionary
            The map dictionary to delete the value from.
        '''
        assert isinstance(map, dict), 'Invalid map %s' % map
        del map[self.__id]

class AttributeOnThread:
    '''
    Class used for creating attributes for python threads.
    '''
    
    def __init__(self, group, name, valueType=None):
        '''
        Creates a new attribute.
        
        @param group: string
            The group name for the attribute, this is usually the module name where is created, it helps to distinguish
            between same names but with other purposes.
        @param name: string
            The name of the attribute.
        @param valueType: type
            The type to check for the set and get values.
        '''
        assert isinstance(group, str), 'Invalid group name %s' % group
        assert isinstance(name, str), 'Invalid name %s' % name
        assert not valueType or isclass(valueType), 'Invalid value type %s' % valueType
        self.__group = group
        self.__name = name
        self.__type = valueType
        if __debug__: self.__id = group + '.' + name
        else:
            self.__id = attrIdForName(group) + '_' + attrIdForName(name)
    
    def has(self):
        '''
        Checks if there is a value for the current thread.
        
        @return: boolean
            True if there is a value, False otherwise.
        '''
        return hasattr(currentThread(), self.__id)
    
    def get(self, *default):
        '''
        Get the value from the current thread.
        
        @param default: argument
            If provided will return the default if no argument value is available.
        @return: object
            The value.
        '''
        value = getattr(currentThread(), self.__id, *default)
        assert not(self.__type and value is not None) or isinstance(value, self.__type), 'Invalid value %s to get for ' \
        'required type %s, for attribute %s.%s' % (value, self.__type, self.__group, self.__name)
        return value
    
    def set(self, value):
        '''
        Sets the value to the current thread.
        
        @param value: object
            The value to set.
        @return: object
            The provided value.
        '''
        assert not(self.__type and value is not None) or isinstance(value, self.__type), 'Invalid value %s to set for ' \
        'required type %s, for attribute %s.%s' % (value, self.__type, self.__group, self.__name)
        setattr(currentThread(), self.__id, value)
        return value
    
    def delete(self):
        '''
        Deletes the value from the provided object.
        '''
        delattr(currentThread(), self.__id)
        
    def clear(self):
        '''
        Deletes the value from the current thread if is present.
        '''
        thread = currentThread()
        if hasattr(thread, self.__id): delattr(thread, self.__id)

# --------------------------------------------------------------------

ATTR_BEAN = Attribute(__name__, 'bean', dict)
# Provides the bean properties.

def bean(clazz):
    '''
    Used for describing bean classes, this type of classes are just containers.
    '''
    properties = {}
    for name, value in clazz.__dict__.items():
        if isclass(value): properties[name] = value
    for name in properties.keys(): delattr(clazz, name)
    inherited = ATTR_BEAN.get(clazz, None)    
    if inherited: properties.update(inherited)
    
    ATTR_BEAN.set(clazz, properties)
    setattr(clazz, '__getattr__', _getattr_bean)
    setattr(clazz, '__setattr__', _setattr_bean)
    return clazz

def _getattr_bean(self, name):
    '''
    FOR INTERNAL USE.
    Used to get attributes for bean defined classes.
    '''
    if name not in ATTR_BEAN.get(self.__class__): raise AttributeError
    return None

def _setattr_bean(self, name, value):
    '''
    FOR INTERNAL USE.
    Used to get attributes for bean defined classes.
    '''
    properties = ATTR_BEAN.get(self.__class__)
    clazz = properties.get(name, None)
    if clazz:
        assert value is None or isinstance(value, clazz), \
        'Invalid value %s for name %r, expected %r' % (value, name, clazz.__name__)
    object.__setattr__(self, name, value)
