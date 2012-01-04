'''
Created on Jan 3, 2012
@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides utility functions for creating and managing proxies.
'''

from inspect import isclass, isfunction
from collections import deque
import abc
from .util import Attribute
from functools import partial, update_wrapper

# --------------------------------------------------------------------

def createProxy(clazz):
    '''
    Create a proxy class for the provided clazz. The proxy class will override the functionality of all methods defined
    in the provided class and the super classes. Attention a proxy will not expose any entity attributes or descriptors 
    only the methods are exposed so the proxy must be used on API type classes. The class attributes will be exposed since
    the proxy will actually inherit the class.
    
    @param clazz: class
        The class to create a proxy for.
    '''
    assert isclass(clazz), 'Invalid class %s' % clazz
    if ATTR_PROXY.has(clazz): return ATTR_PROXY.get(clazz)
    
    #TODO: see if a Proxy class is required and continue.
    def __init__(self, *handlers):
        '''
        Initialize the proxy with the provided handlers.
        
        @param handlers: arguments[IProxyHandler]
            The handlers to construct the proxy based on.
        '''
        assert not handlers, 'At least on handler is required to construct the proxy'
        if __debug__:
            for handler in handlers: assert isinstance(handler, IProxyHandler), 'Invalid handler %s' % handler
        self.__handlers = list(handlers)
    
    def invoke(self, *args, **keyargs): return Execution(deque(self.__handlers), args, keyargs).invoke()
    
    methods, classes = {'__init__': __init__}, deque()
    classes.append(clazz)
    while classes:
        cls = classes.popleft()
        for name, function in cls.__dict__.items():
            if isfunction(function):
                if name not in methods:
                    methods[name] = update_wrapper(partial(function), function)
        classes.extend(base for base in cls.__bases__ if base != object)
    return ATTR_PROXY.set(clazz, type(clazz.__name__ + '$Proxy', (clazz,), methods))

# --------------------------------------------------------------------

ATTR_PROXY = Attribute(__name__, 'proxy')
# The attribute used for storing the proxy.

class Execution:
    '''
    Provides the container for the execution of the proxied method.
    '''
    
    __slots__ = ['handlers', 'args', 'keyargs']
    
    def __init__(self, handlers, args, keyargs):
        '''
        Construct the execution chain.
        
        @param handlers: deque[IProxyHandler]
            The proxy handlers to use in the execution.
        @param args: list[object]
            The arguments used in the proxied method call.
        @param keyargs: dictionary{string, object}
            The key arguments used in the proxied method call.
        '''
        assert isinstance(handlers, deque), 'Invalid handlers queue %s' % handlers
        assert not handlers, 'Invalid handlers %s, expected at least one handler' % handlers
        assert isinstance(args, list), 'Invalid arguments %s' % args
        assert isinstance(keyargs, dict), 'Invalid key arguments %s' % keyargs
        if __debug__:
            for handler in handlers: assert isinstance(handler, IProxyHandler), 'Invalid handler %s' % handler
            for key in keyargs: assert isinstance(key, str), 'Invalid key %s' % key
        self.handlers = handlers
        self.args = args
        self.keyargs = keyargs
        
    def invoke(self):
        '''
        Continues with the invoking of the execution.
        
        @return: object
            The invoke result.
        '''
        handler = self.handlers.popleft()
        assert isinstance(handler, IProxyHandler), 'Invalid handler %s' % handler
        return handler.handle(self)

class IProxyHandler(metaclass=abc.ABCMeta):
    '''
    API class that provides the proxy handling.
    '''
    
    @abc.abstractclassmethod
    def handle(self, execution):
        '''
        Method called for all method executions that are proxied.
        
        @param execution: Execution
            The execution chain of the proxies.
        @return: object
            The return value for the execution.
        '''
