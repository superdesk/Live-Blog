'''
Created on Jan 3, 2012
@package: ally utilities
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides utility functions for creating and managing proxies.
'''

from ally.support.util import MetaClassUnextendable
from collections import deque
from functools import update_wrapper
from inspect import isclass, isfunction
import abc
import re
from abc import ABCMeta

# --------------------------------------------------------------------

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
    
    @param clazz: class
        The class to create a proxy for.
    '''
    assert isclass(clazz), 'Invalid class %s' % clazz
    if issubclass(clazz, Proxy): return clazz
    try: return clazz._ally_proxy
    except AttributeError: pass

    attributes, classes = {}, deque()
    classes.append(clazz)
    while classes:
        cls = classes.popleft()
        for name, function in cls.__dict__.items():
            if name not in ('__init__',) and isfunction(function):
                if name not in attributes:
                    if name.startswith(PREFIX_HIDDEN_METHOD) and not REGEX_SPECIAL.match(name):
                        attributes[name] = update_wrapper(ProxyMethodInvalid(), function)
                    else:
                        attributes[name] = update_wrapper(ProxyMethod(name), function)
        classes.extend(base for base in cls.__bases__ if base != object)

    attributes['__module__'] = clazz.__module__
    attributes['__slots__'] = ('_proxy_handlers', '_proxy_calls')
    proxy = type.__new__(ProxyMeta, clazz.__name__ + '$Proxy', (Proxy, clazz), attributes)

    proxy._ally_proxied = clazz
    clazz._ally_proxy = proxy
    return proxy

def proxyWrapFor(obj):
    '''
    Creates a proxy that will wrap the provided implementation.
    
    @param impl: object
        The object to create a proxy wrap for.
    @return: Proxy object
        The proxy instance that is wrapping the provided implementation.
    '''
    assert obj is not None, 'An object is required'
    if isinstance(obj, Proxy): proxy = obj.__class__
    else: proxy = createProxy(obj.__class__)
    return proxy(ProxyWrapper(obj))

def proxiedClass(clazz):
    '''
    Provides the proxied class of a proxy class.
    
    @param clazz: class
        The proxy class to provided the proxied class for.
    @return: class
        The proxied class or the provided clazz if is not a proxy.
    '''
    assert isclass(clazz), 'Invalid class %s' % clazz
    if issubclass(clazz, Proxy): return clazz.__bases__[1]
    return clazz

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
    elif isinstance(proxy, Proxy):
        return proxy, None
    else:
        raise ProxyError('The provided object %r is not a proxy' % proxy)

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
    assert isinstance(proxy, Proxy)
    proxy._proxy_handlers.insert(0, proxyHandler)

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
    assert isinstance(proxy, Proxy)
    return proxyHandler in proxy._proxy_handlers

# --------------------------------------------------------------------

class Execution:
    '''
    Provides the container for the execution of the proxied method.
    '''

    __slots__ = ('proxyCall', 'handlers', 'args', 'keyargs')

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

class ProxyMeta(MetaClassUnextendable, ABCMeta):
    '''
    Meta describing an unextedable class that also contains abstract base class metas.
    '''

class Proxy:
    '''
    Provides the base class for proxy classes.
    '''

    def __init__(self, *handlers):
        '''
        Initialize the proxy with the provided handlers.
        
        @param handlers: arguments[IProxyHandler]
            The handlers to construct the proxy based on.
        '''
        assert handlers, 'At least on handler is required to construct the proxy'
        if __debug__:
            for handler in handlers: assert isinstance(handler, IProxyHandler), 'Invalid handler %s' % handler
        self._proxy_handlers = list(handlers)
        self._proxy_calls = {}

        self._ally_listeners = {} # This will allow the proxy class to be binded with listeners

class ProxyCall:
    '''
    Handles the proxy calls.
    '''

    def __init__(self, proxy, proxyMethod):
        '''
        Construct the proxy call.
        
        @param proxy: Proxy
            The proxy that made the call.
        @param proxyMethod: ProxyMethod
            The proxy method of the call.
        '''
        assert isinstance(proxy, Proxy), 'Invalid proxy %s' % proxy
        assert isinstance(proxyMethod, ProxyMethod), 'Invalid proxy method %s' % proxyMethod
        self.proxy = proxy
        self.proxyMethod = proxyMethod

        self._ally_listeners = {} # This will allow the proxy method to be binded with listeners

    def __call__(self, *args, **keyargs):
        '''
        @see: Callable.__call__
        '''
        return Execution(self, deque(self.proxy._proxy_handlers), args, keyargs).invoke()

class ProxyMethod:
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
            assert isinstance(proxy, Proxy), 'Invalid proxy %s' % proxy
            call = proxy._proxy_calls.get(self.name)
            if not call: call = proxy._proxy_calls[self.name] = update_wrapper(ProxyCall(proxy, self), self)
            return call
        return self

class ProxyMethodInvalid:
    '''
    Raises an exception whenever an attempt is made to retrieve the call method.
    '''

    def __get__(self, proxy, owner=None):
        '''
        @see: http://docs.python.org/reference/datamodel.html
        '''
        raise AttributeError('Method not available for proxy')

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

