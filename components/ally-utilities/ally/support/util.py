'''
Created on Jun 9, 2011

@package: ally utilities
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides implementations that provide general behavior or functionality.
'''

from collections import Iterator
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
        raise Exception('Cannot create an instance of \'%s\' class' % cls.__name__)

# --------------------------------------------------------------------

class Singletone:
    '''
    Extending this class will always return the same instance.
    '''

    def __new__(cls):
        '''
        Will always return the same instance.
        '''
        try: return cls._ally_singletone
        except AttributeError: cls._ally_singletone = super().__new__(cls)
        return cls._ally_singletone

# --------------------------------------------------------------------

class MetaClassUnextendable(type):
    '''
    Provides a meta class that doesn't allow for any class extension.
    '''

    def __new__(cls, name, bases, namespace):
        raise TypeError('Cannot extend class in %s' % bases)

# --------------------------------------------------------------------

class immut(dict):
    '''The immutable dictionary class'''

    __slots__ = ('__hash__value')

    def __new__(cls, *args, **keyargs):
        if not (args or keyargs):
            try: return cls.__empty__
            except AttributeError: cls.__empty__ = dict.__new__(cls)
            return cls.__empty__
        return dict.__new__(cls, *args, **keyargs)

    def update(self, *args, **keyargs): raise AttributeError('Operation not allowed on immutable dictionary')
    __setitem__ = __delitem__ = setdefault = pop = popitem = clear = update

    def __hash__(self):
        '''
        Provides the hash code for a immutable dictionary.
        '''
        try: return self.__hash__value
        except AttributeError: self.__hash__value = hash(tuple(p for p in self.items()))
        return self.__hash__value

def firstOf(coll):
    '''
    Provides the first element from the provided collection.
    
    @param coll: list|tuple|iterable
        The collection to provide the first item.
    '''
    if isinstance(coll, (list, tuple)): return coll[0]
    coll = iter(coll)
    return next(coll)

def lastCheck(iterator):
    '''
    Checks the last element from the provided iterator. It will return a tuple containing as the first value a boolean
    with False if the element is not the last element in the provided iterator and True if is the last one. On the last
    position of the tuple it will return the actual value provided by the iterator.
    
    @param iterator: Iterator
        The iterator to wrap for the last element check.
    '''
    if not isinstance(iterator, Iterator): iterator = iter(iterator)

    item, stop = next(iterator), False
    while True:
        try:
            itemNext = next(iterator)
            yield False, item
            item = itemNext
        except StopIteration:
            if stop: raise
            stop = True
            yield True, item
