'''
Created on Jun 9, 2011

@package: utilities
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
        if not hasattr(cls, '_singletone'):
            cls._singletone = super().__new__(cls)
        return cls._singletone

# --------------------------------------------------------------------

class UnextendableMeta(type):
    '''
    Provides a meta class that doesn't allow for any class extension.
    '''

    def __new__(cls, name, bases, namespace):
        raise TypeError('Cannot extend class in %s' % bases)

# --------------------------------------------------------------------

def _immut_raise(*args, **keyargs):
    '''
    FOR INTERNAL USE.
    Used by @see: immut to raise exception in case of value change
    '''
    raise AttributeError('Operation not allowed on immutable dictionary')

def _immut_hash(self):
    '''
    FOR INTERNAL USE.
    Provides the hash code for a immutable dictionary.
    '''
    return hash(tuple(p for p in self.items()))

_immut_attributes = dict.fromkeys(
                ('__setitem__', '__delitem__', 'setdefault', 'pop', 'popitem', 'clear', 'update'), _immut_raise)
_immut_attributes['__hash__'] = _immut_hash
_immut_attributes['__slots__'] = ()
# The immutable dictionary attributes
immut = type('immut', (dict,), _immut_attributes)
# The immutable dictionary class

# --------------------------------------------------------------------

_attrNameIds = {}
# Used by the attribute to assign a unique id to a name.

attrIdForName = lambda name: str(_attrNameIds.setdefault(name, len(_attrNameIds)))
# Provides the name id.

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
