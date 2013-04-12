'''
Created on Sep 4, 2012

@package: ally base
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides specifications for classes describing general behavior.
'''

import abc

# --------------------------------------------------------------------

class IContained(metaclass=abc.ABCMeta):
    '''
    Provides the contained descriptor specification. This needs to be handled.
    '''

    @abc.abstractclassmethod
    def __contained__(self, obj):
        '''
        Checks if the descriptor is contained in the provided object. This is an artifact from the __contains__ method 
        that is found on the actual model object.
        
        @param obj: object
            The object to check if the descriptor is contained in.
        @return: boolean
            True if the descriptor is contained in the object, False otherwise.
        '''

    @classmethod
    def __subclasshook__(cls, C):
        if cls is IContained:
            if any('__contained__' in B.__dict__ for B in C.__mro__): return True
        return NotImplemented

class IGet(metaclass=abc.ABCMeta):
    '''
    Provides the get descriptor specification. This is automatically handled by the python language.
    '''

    @abc.abstractclassmethod
    def __get__(self, obj, clazz=None):
        '''
        Provides the value represented by this descriptor for the provided object.
        
        @param obj: object
            The object to provide the value for, None in case the descriptor is used with the class.
        @param clazz: class|None
            The object class from which the descriptor originates from, can be None if the object is provided.
        @return: object
            The value of the descriptor.
        '''

    @classmethod
    def __subclasshook__(cls, C):
        if cls is IGet:
            if any('__get__' in B.__dict__ for B in C.__mro__): return True
        return NotImplemented

class ISet(metaclass=abc.ABCMeta):
    '''
    Provides the set descriptor specification. This is automatically handled by the python language.
    '''

    @abc.abstractclassmethod
    def __set__(self, obj, value):
        '''
        Set the value represented by this descriptor for the provided object.
        
        @param obj: object
            The object to set the value to.
        @param value: object
            The value to set, needs to be valid for this descriptor.
        '''

    @classmethod
    def __subclasshook__(cls, C):
        if cls is ISet:
            if any('__set__' in B.__dict__ for B in C.__mro__): return True
        return NotImplemented

class IDelete(metaclass=abc.ABCMeta):
    '''
    Provides the delete descriptor specification. This is automatically handled by the python language.
    '''

    @abc.abstractclassmethod
    def __delete__(self, obj):
        '''
        Remove the value represented by this descriptor from the provided object.
        
        @param obj: object
            The object to remove the value from.
        '''

    @classmethod
    def __subclasshook__(cls, C):
        if cls is IDelete:
            if any('__delete__' in B.__dict__ for B in C.__mro__): return True
        return NotImplemented
