'''
Created on Jan 3, 2012
@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides utility functions for creating and managing proxies.
'''

from ..support.util import Attribute
from _abcoll import Callable
from collections import deque
from functools import update_wrapper
from inspect import isclass, isfunction
import abc
import re

# --------------------------------------------------------------------

ATTR_PROXY = Attribute(__name__, 'proxy')
# The attribute used for storing the proxy.
ATTR_HANDLERS = Attribute(__name__, 'handlers', list)
# The attribute used for storing the proxy handlers.
ATTR_CALLS = Attribute(__name__, 'calls', dict)
# The attribute used for storing the proxy calls.

PREFIX_HIDDEN_METHOD = '_'
# Provides the prefix for hidden methods (that will not have a proxy method created for)
REGEX_SPECIAL = re.compile('__[\w]+__$')
# Provides the regex that detects special methods

# --------------------------------------------------------------------

class ProxyError(Exception):
    '''
    Exception thrown when there is a proxy problem.
    '''

# --------------------------------------------------------------------

def createProxy(clazz):
    '''
    Create a proxy class for the provided clazz. The proxy class will override the functionality of all methods defined
    in the provided class and the super classes. Attention a proxy will not expose any entity attributes or descriptors 
    only the methods are exposed so the proxy must be used on API type classes. The class attributes will be exposed since
    the proxy will actually inherit the class.
    
    I haven't created an actual Proxy class to have this __init__ because if that class had any attributes it might lead
    to name overlapping, so this way there is no Proxy class just proxy attributes that are much safer.
    
    @param clazz: class
        The class to create a proxy for.
    '''
    assert isclass(clazz), 'Invalid class %s' % clazz
    if isProxyClass(clazz): return clazz
    if ATTR_PROXY.has(clazz): return ATTR_PROXY.get(clazz)
    
    methods, classes = {'__init__': _proxy__init__}, deque()
    classes.append(clazz)
    while classes:
        cls = classes.popleft()
        for name, function in cls.__dict__.items():
            if isfunction(function):
                if name not in methods:
                    methods[name] = update_wrapper(ProxyMethod(name), function)
        classes.extend(base for base in cls.__bases__ if base != object)
    proxy = type(clazz.__name__ + '$Proxy', (clazz,), methods)
    proxy.__module__ = clazz.__module__
    return ATTR_PROXY.set(clazz, proxy)

def createProxyOfImpl(clazz):
    '''
    @see: createProxy
    Create a proxy class for the provided implementation clazz. Since the proxy is created for an API implementation
    the proxy will inherit all super classes of the provided class, but not the actual class. All methods that start
    with _ that are not special methods will not have a proxy created for.
    
    @param clazz: class
        The implementation class to create a proxy for.
    '''
    assert isclass(clazz), 'Invalid class %s' % clazz
    if isProxyClass(clazz): return clazz
    if ATTR_PROXY.has(clazz): return ATTR_PROXY.get(clazz)
    
    methods, classes = {'__init__': _proxy__init__}, deque()
    classes.append(clazz)
    while classes:
        cls = classes.popleft()
        if cls == object: continue
        for name, function in cls.__dict__.items():
            if isfunction(function):
                if name not in methods and (not name.startswith(PREFIX_HIDDEN_METHOD) or REGEX_SPECIAL.match(name)):
                    methods[name] = update_wrapper(ProxyMethod(name), function)
        classes.extend(cls.__bases__)
    proxy = type(clazz.__name__ + '$Proxy', (clazz,), methods)
    proxy.__module__ = clazz.__module__
    return ATTR_PROXY.set(clazz, proxy)

def proxyWrapForImpl(impl):
    '''
    Creates a proxy that will wrap the provided implementation.
    
    @param impl: object
        The object to create a proxy wrap for.
    @return: Proxy object
        The proxy instance that is wrapping the provided implementation.
    '''
    assert impl is not None, 'A impl object is required'
    proxy = createProxyOfImpl(impl.__class__)
    return proxy(ProxyWrapper(impl))

def isProxyClass(clazz):
    '''
    Checks if the provided class is a proxy class.
    
    @param clazz: class
        The class to check if is a proxy class.
    '''
    assert isclass(clazz), 'Invalid class %s' % clazz
    return clazz.__name__.endswith('$Proxy')

def isProxy(obj):
    '''
    Checks if the provided object is a proxy instance.
    
    @param obj: object
        The object to check if is a proxy.
    '''
    assert obj, 'Invalid object %s' % obj
    return obj.__class__.__name__.endswith('$Proxy')

def analyzeProxy(proxy):
    '''
    Analyzes the provided proxy.
    
    @param proxy: object|ProxyCall
        The proxy can be either a proxy or a proxy call.
    @return: tuple(object, string)
        A tuple having on the first position the proxy object and on the second if is the case the name of the method.
    @raise ProxyError: if no proxy could be obtained.
    '''
    if isinstance(proxy, ProxyCall):
        assert isinstance(proxy, ProxyCall)
        return proxy.proxy, proxy.proxyMethod.name
    else:
        if not isProxy(proxy): raise ProxyError('The provided object %r is not a proxy' % proxy)
        return proxy, None

def registerProxyHandler(proxyHandler, proxy):
    '''
    Register the proxy handler to the provided proxy object. The last registered proxy handler will be the first used.
    
    @param proxyHandler: IProxyHandler
        The proxy handler to be registered to the provided proxy object.
    @param proxy: @see: analyzeProxy
        If the registration is done on a proxy call than the proxy handler will be used only for that call method.
    '''
    assert isinstance(proxyHandler, IProxyHandler), 'Invalid proxy handler %s' % proxyHandler
    proxy, method = analyzeProxy(proxy)
    if method: proxyHandler = ProxyFilter(proxyHandler, method)
    ATTR_HANDLERS.getOwn(proxy).insert(0, proxyHandler)

def hasProxyHandler(proxyHandler, proxy):
    '''
    Checks if the provided proxy has the specified proxy handler, the check is done by using equality.
    
    @param proxyHandler: IProxyHandler
        The proxy handler to be searched in the provided proxy object.
    @param proxy: @see: analyzeProxy
        The proxy object to search in.
    '''
    assert isinstance(proxyHandler, IProxyHandler), 'Invalid proxy handler %s' % proxyHandler
    proxy, _method = analyzeProxy(proxy)
    return proxyHandler in ATTR_HANDLERS.getOwn(proxy)
    
# --------------------------------------------------------------------

class Execution:
    '''
    Provides the container for the execution of the proxied method.
    '''
    
    __slots__ = ['proxyCall', 'handlers', 'args', 'keyargs']
    
    def __init__(self, proxyCall, handlers, args, keyargs):
        '''
        Construct the execution chain.
        
        @param proxyCall: ProxyCall
            The proxy call of the execution.
        @param handlers: deque[IProxyHandler]
            The proxy handlers to use in the execution.
        @param args: list[object]
            The arguments used in the proxied method call.
        @param keyargs: dictionary{string, object}
            The key arguments used in the proxied method call.
        '''
        assert isinstance(proxyCall, ProxyCall), 'Invalid proxy call %s' % proxyCall
        assert isinstance(handlers, deque), 'Invalid handlers queue %s' % handlers
        assert handlers, 'Invalid handlers %s, expected at least one handler' % handlers
        if isinstance(args, tuple): args = list(args)
        assert isinstance(args, list), 'Invalid arguments %s' % args
        assert isinstance(keyargs, dict), 'Invalid key arguments %s' % keyargs
        if __debug__:
            for handler in handlers: assert isinstance(handler, IProxyHandler), 'Invalid handler %s' % handler
            for key in keyargs: assert isinstance(key, str), 'Invalid key %s' % key
        self.proxyCall = proxyCall
        self.handlers = handlers
        self.args = args
        self.keyargs = keyargs
        
    def invoke(self):
        '''
        Continues with the invoking of the execution.
        
        @return: object
            The invoke result.
        '''
        try: handler = self.handlers.popleft()
        except IndexError:
            raise AttributeError('No proxy handler resolves method %r' % self.methodName)
        assert isinstance(handler, IProxyHandler), 'Invalid handler %s' % handler
        return handler.handle(self)

class ProxyMethod(Callable):
    '''
    Handles the proxy method calls.
    '''
    
    def __init__(self, name):
        '''
        Construct the proxy method.
        
        @param name: string
            The method name represented by this proxy method.
        '''
        assert isinstance(name, str), 'Invalid name %s' % name
        self.name = name
    
    def __call__(self, proxy, *args, **keyargs):
        '''
        @see: Callable.__call__
        '''
        return self.__get__(proxy).__call__(*args, **keyargs)
    
    def __get__(self, proxy, owner=None):
        '''
        @see: http://docs.python.org/reference/datamodel.html
        '''
        if proxy is not None:
            calls = ATTR_CALLS.getOwn(proxy, None)
            if not calls: calls = ATTR_CALLS.setOwn(proxy, {})
            call = calls.get(self.name)
            if not call: call = calls[self.name] = update_wrapper(ProxyCall(proxy, self), self)
            return call
        return self

class ProxyCall:
    '''
    Handles the proxy calls.
    '''
    
    def __init__(self, proxy, proxyMethod):
        '''
        Construct the proxy call.
        
        @param proxy: object
            The proxy that made the call.
        @param proxyMethod: ProxyMethod
            The proxy method of the call.
        '''
        assert isProxy(proxy), 'Invalid proxy %s' % proxy
        assert isinstance(proxyMethod, ProxyMethod), 'Invalid proxy method %s' % proxyMethod
        self.proxy = proxy
        self.proxyMethod = proxyMethod
        
    def __call__(self, *args, **keyargs):
        '''
        @see: Callable.__call__
        '''
        return Execution(self, deque(ATTR_HANDLERS.getOwn(self.proxy)), args, keyargs).invoke()

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

class ProxyWrapper(IProxyHandler):
    '''
    Provides a @see: IProxyHandler implementation that just delegates the functionality to a wrapped object.
    '''
    
    def __init__(self, wrapped):
        '''
        Construct the wrapper proxy.
        
        @param wrapped: object
            The wrapped instance.
        '''
        assert wrapped, 'A wrapped object is required'
        self._wrapped = wrapped
        
    def handle(self, execution):
        '''
        @see: IProxyHandler.handle
        '''
        assert isinstance(execution, Execution), 'Invalid execution %s' % execution
        assert isinstance(execution.proxyCall, ProxyCall)
        method = getattr(self._wrapped, execution.proxyCall.proxyMethod.name, None)
        if not method:
            raise AttributeError('The proxy wrapped %s has no method %r' % (self._wrapped, execution.methodName))
        return method(*execution.args, **execution.keyargs)

class ProxyFilter(IProxyHandler):
    '''
    Provides a @see: IProxyHandler implementation that filters the execution based on the method name and delivers the
    execution to proxy handlers assigned to that method name.
    '''
    
    def __init__(self, proxyHandler, *methodNames):
        '''
        Construct the filter proxy.
        
        @param proxyHandler: IProxyHandler
            The proxy handler to be called if the method name is in the provided method names.
        @param methodNames: arguments(string)
            The methods names to filter the proxy by.
        '''
        assert isinstance(proxyHandler, IProxyHandler), 'Invalid proxy handler %s' % proxyHandler
        assert methodNames, 'At least a method name is required'
        if __debug__:
            for name in methodNames: assert isinstance(name, str), 'Invalid method name %s' % name
        self._proxyHandler = proxyHandler
        self._methodNames = methodNames
        
    def handle(self, execution):
        '''
        @see: IProxyHandler.handle
        '''
        assert isinstance(execution, Execution), 'Invalid execution %s' % execution
        assert isinstance(execution.proxyCall, ProxyCall)
        if execution.proxyCall.proxyMethod.name in self._methodNames:
            assert isinstance(execution.handlers, deque)
            execution.handlers.appendleft(self._proxyHandler)
        return execution.invoke()

# --------------------------------------------------------------------

def _proxy__init__(proxy, *handlers):
    '''
    FOR INTERNAL USE ONLY!
    Initialize the proxy with the provided handlers.
    
    @param handlers: arguments[IProxyHandler]
        The handlers to construct the proxy based on.
    '''
    assert handlers, 'At least on handler is required to construct the proxy'
    if __debug__:
        for handler in handlers: assert isinstance(handler, IProxyHandler), 'Invalid handler %s' % handler
    ATTR_HANDLERS.setOwn(proxy, list(handlers))

