'''
Created on Aug 24, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides implementations for easy attachment of listeners.
'''

from .util import Attribute
from _abcoll import Callable
import builtins
import functools

# --------------------------------------------------------------------

class Proxy:
    '''
    Class describing a proxy to a wrapped instance, basically this allows to override the functionality of a
    instance rather than a class.
    '''
    
    def __init__(self, wrapped):
        '''
        Constructs the proxy for the wrapped object.
        
        @param wrapped: object
            The object being wrapped by this proxy.
        '''
        assert wrapped, 'Invalid wrapped instance %s' % wrapped
        self.__dict__['_UTIL_wrapped'] = wrapped
        _overrideIsinstance()

    def __setattr__(self, name, value):
        return setattr(self.__dict__['_UTIL_wrapped'], name, value)

    def __getattr__(self, name):
        return getattr(self.__dict__['_UTIL_wrapped'], name)
    
    def __str__(self):
        return str(self.__dict__['_UTIL_wrapped'])


def _overrideIsinstance():
    '''
    FOR INTERNAL USE.
    Overrides the isinstance in order to acknowledge proxies.
    '''
    #TODO: find a different way of handling this
    # We need to change the isinstance behavior in order to convince that the proxies are just like the 
    # represented instances.
    global isinstance
    if getattr(isinstance, '_UTIL_isinstance', False): return
    __isinstance = isinstance
    def isinstance(obj, classes):
        if not __isinstance(obj, classes):
            if __isinstance(obj, Proxy):
                return __isinstance(obj.__dict__['_UTIL_wrapped'], classes)
            return False
        return True
    setattr(isinstance, '_UTIL_isinstance', True)
    setattr(builtins, 'isinstance', isinstance)
    
# --------------------------------------------------------------------

ATTR_LISTENERS = Attribute(__name__, 'listeners', dict)
# The listeners attribute.

def addListener(to, key, listener, index=1):
    '''
    Adds the listener to the provided to object.
    
    @param to: object
        The object to assign the listeners to.
    @param key: object immutable|tuple(object immutable)
        The key to associate with the listener, this key will be used to associate the listener to a group that
        will be used in different situations.
    @param listener: Callable|tuple(Callable)
        A callable that is called as listener.
    @param index: integer
        The index at which to position the listener, -1 means at the end of the list.
    '''
    assert to, 'Provide a to object'
    _listeners = ATTR_LISTENERS.getOwn(to, None)
    if not _listeners: _listeners = ATTR_LISTENERS.setOwn(to, {}) 
    if isinstance(key, tuple):_keys = key
    else: _keys = [key]
    addlist = list(listener) if isinstance(listener, tuple) else [listener]
    for key in _keys:
        listeners = _listeners.get(key)
        if listeners:
            l = listeners.get(index)
            if not l:
                l = addlist
                listeners[index] = l
            else:
                l.extend(addlist)
        else:
            _listeners[key] = {index:addlist}
    
def callListeners(to, key, *args):
    '''
    Calls the listeners having the specified key. If one of the listeners will return false it will stop the all
    the listeners executions for the provided key.
    
    @param key: object immutable
        The key of the listeners to be invoked, if the key has no listeners nothing will happen.
    @param args: arguments
        Arguments used in invoking the listeners.
    @return: boolean
        True if and only if all the listeners have returned a none False value, if one of the listeners returns False
        the listeners execution is stopped and False value is returned.
    @raise Exception: Will raise exceptions for different situations dictated by the listeners. 
    '''
    assert to, 'Provide a to object'
    _listeners = ATTR_LISTENERS.getOwn(to, None)
    if _listeners:
        listeners = _listeners.get(key)
        if listeners:
            indexes = list(listeners.keys())
            indexes.sort()
            for index in indexes:
                for listener in listeners[index]:
                    if listener(*args) == False:
                        return False
    return True

# --------------------------------------------------------------------

EVENT_BEFORE_CALL = 'before_call'
EVENT_AFTER_CALL = 'after_call'
EVENT_EXCEPTION_CALL = 'exception_call'

class ProxyListener:
    '''
    Class describing the proxy listeners.
    '''
        
    def addBeforeListener(self, listener, index= -1):
        '''
        @see: addListener
        The listener has to accept a parameter with the list of arguments and a parameter with the dictionary of
        key arguments. The listeners can alter the structure of the arguments and will be reflected into the
        actual call of the method. If a listener will return False than the invoking will not take place and 
        neither the after call listeners will not be invoked.
        '''
        addListener(self, EVENT_BEFORE_CALL, listener, index)
        
    def addAfterListener(self, listener, index= -1):
        '''
        @see: addListener
        The listener has to accept a parameter containing the return value. If a listener will return False it 
        will block the call to the rest of the exception listeners.
        '''
        addListener(self, EVENT_AFTER_CALL, listener, index)
        
    def addExceptionListener(self, listener, index= -1):
        '''
        @see: addListener
        The listener has to accept a parameter containing the exception. If a listener will return False it will block
        the call to the rest of the exception listeners.
        '''
        addListener(self, EVENT_EXCEPTION_CALL, listener, index)
    
class ProxyWrapper(Proxy, ProxyListener):
    '''
    Class describing a proxy to a wrapped class, before invoking designated methods it will first call
    listeners.
    '''

class ProxyCall(Callable, ProxyListener):
    '''
    Provides the call wrapping for the proxy.
    '''
    
    def __init__(self, instance, method):
        self.__instance = instance
        self.__method = method
        functools.update_wrapper(self, method)

    def __call__(self, *args, **kwds):
        args = list(args)
        if callListeners(self, EVENT_BEFORE_CALL, args, kwds):
            if callListeners(self.__instance, EVENT_BEFORE_CALL, args, kwds):
                try:
                    value = self.__method(*args, **kwds)
                except Exception as e:
                    if callListeners(self, EVENT_EXCEPTION_CALL, e):
                        callListeners(self.__instance, EVENT_EXCEPTION_CALL, e)
                    raise
                if callListeners(self, EVENT_AFTER_CALL, value):
                    callListeners(self.__instance, EVENT_AFTER_CALL, value)
                return value

# --------------------------------------------------------------------

def wrapInstance(instance):
    '''
    Wraps the provided class into a proxy class wrapper, this will allow for manipulating calls towards the
    instance. 
    
    @param instance: object
        The instance to be wrapped.
    @return: ProxyWrapper
        The wrapped instance.
    '''
    assert instance, 'Invalid instance %s' % instance
    clazz = instance.__class__
    if isinstance(clazz, ProxyWrapper):
        # Already wrapped.
        proxy = instance
    else:
        proxy = ProxyWrapper(instance)
    return proxy

def wrapMethod(instance, method):
    '''
    Wraps the provided method into a proxy call wrapper, this will allow for manipulating the calls towards the
    method. 
    
    @param instance: object
        The instance having the method to be wrapped, attention this is not mandatory a proxy wrapper class.
    @param methods: string
        The method name to be wrapped.
    @return: ProxyClass
        The proxy call.
    '''
    assert isinstance(method, str), 'Invalid method %s' % method
    m = getattr(instance, method)
    if isinstance(m, ProxyCall):
        proxy = m
    else:
        proxy = ProxyCall(instance, m)
        instance.__dict__[method] = proxy
    return proxy
