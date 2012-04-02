'''
Created on Jan 17, 2012

@author: chupy
'''

from functools import partial
from inspect import stack
from types import MethodType
import weakref
from weakref import WeakSet, WeakKeyDictionary, ref

# --------------------------------------------------------------------

def immutable(cls):
    locked = WeakKeyDictionary()

    original__init__ = cls.__init__
    def __init__(obj, *args, **keyargs):
        ref(obj)
        original__init__(obj, *args, **keyargs)
        locked[obj] = None
    cls.__init__ = __init__

    original__setattr__ = cls.__setattr__
    def __setattr__(obj, key, value):
        if obj in locked: raise AttributeError('Immutable object cannot set attribute %s' % key)
        original__setattr__(obj, key, value)
    cls.__setattr__ = __setattr__

    return cls

class A:

    mucu = 20

    def __init__(self):
        self.a = 10

    def bbb(self):
        print(self)

class B:

    def __init__(self):
        self.b = 20

    def ppp(self):
        print(self)

if __name__ == '__main__':
    a = A()
    b = B()
    p = partial(getattr, name='bbb')
    p(b)
