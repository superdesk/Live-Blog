'''
Created on Aug 24, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides implementations for easy binding of listeners to any objects also provides the means of integrating with proxies.
'''

from ..container.proxy import IProxyHandler, Execution, ProxyCall, analyzeProxy, \
    registerProxyHandler, hasProxyHandler
from ..support.util import Attribute

# --------------------------------------------------------------------

ATTR_LISTENERS = Attribute(__name__, 'listeners', dict)
# The attribute used to store the listeners.

def bindListener(to, key, listener, index= -1):
    '''
    Binds the listener to the provided to object.
    
    @param to: object
        The object to bind the listeners to.
    @param key: object immutable|tuple(object immutable)
        The key to associate with the listener, this key will be used to associate the listener to a group that
        will be used in different situations.
    @param listener: Callable|tuple(Callable)
        A Callable that is called as listener.
    @param index: integer
        The index at which to position the listener, -1 means at the end of the list.
    '''
    assert to, 'Provide a to object'
    _listeners = ATTR_LISTENERS.getOwn(to, None)
    if not _listeners: _listeners = ATTR_LISTENERS.setOwn(to, {}) 
    if isinstance(key, tuple):_keys = key
    else: _keys = [key]
    addlist = list(listener) if isinstance(listener, tuple) else [listener]
    assert addlist, 'At least one listener is required'
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
    Calls the listeners having the specified key. If one of the listeners will return False it will stop all the 
    listeners executions for the provided key.
    
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

EVENT_BEFORE_CALL = 'before'
EVENT_AFTER_CALL = 'after'
EVENT_EXCEPTION_CALL = 'exception'

def bindBeforeListener(to, listener, index= -1):
    '''
    @see: bindListener
    The listener has to accept a parameter with the list of arguments and a parameter with the dictionary of
    key arguments. The listeners can alter the structure of the arguments and will be reflected into the
    actual call of the method. If a listener will return False than the invoking will not take place and 
    neither the after call listeners will not be invoked.
    '''
    bindListener(to, EVENT_BEFORE_CALL, listener, index)
    
def bindAfterListener(to, listener, index= -1):
    '''
    @see: bindListener
    The listener has to accept a parameter containing the return value. If a listener will return False it 
    will block the call to the rest of the exception listeners.
    '''
    bindListener(to, EVENT_AFTER_CALL, listener, index)
    
def bindExceptionListener(to, listener, index= -1):
    '''
    @see: bindListener
    The listener has to accept a parameter containing the exception. If a listener will return False it will block
    the call to the rest of the exception listeners.
    '''
    bindListener(to, EVENT_EXCEPTION_CALL, listener, index)

# --------------------------------------------------------------------

def registerProxyBinder(proxy):
    '''
    Register the proxy handler to the provided proxy object. The last registered proxy handler will be the first used.
    
    @param proxyHandler: IProxyHandler
        The proxy handler to be registered to the provided proxy object.
    @param proxy: @see: analyzeProxy
        If the registration is done on a proxy call than the proxy handler will be used only for that call method.
    '''
    proxy, _method = analyzeProxy(proxy)
    if not hasProxyHandler(PROXY_BINDER, proxy): registerProxyHandler(PROXY_BINDER, proxy)

class ProxyBinder(IProxyHandler):
    '''
    Provides a @see: IProxyHandler implementation in order to execute binded listeners. 
    '''
    
    def handle(self, execution):
        '''
        @see: IProxyHandler.handle
        '''
        assert isinstance(execution, Execution), 'Invalid execution %s' % execution
        proxyCall = execution.proxyCall
        assert isinstance(proxyCall, ProxyCall)
        proxy = proxyCall.proxy
        
        if callListeners(proxy, EVENT_BEFORE_CALL, execution.args, execution.keyargs):
            if callListeners(proxyCall, EVENT_BEFORE_CALL, execution.args, execution.keyargs):
                try:
                    value = execution.invoke()
                except Exception as e:
                    if callListeners(proxy, EVENT_EXCEPTION_CALL, e):
                        callListeners(proxyCall, EVENT_EXCEPTION_CALL, e)
                    raise
                if callListeners(proxy, EVENT_AFTER_CALL, value):
                    callListeners(proxyCall, EVENT_AFTER_CALL, value)
                return value

PROXY_BINDER = ProxyBinder()
# The single proxy binder handler that solver the listener calls.
# This implementation is state less so it has to be considered a singletone.

# --------------------------------------------------------------------
    
def bindLock(proxy, lock):
    '''
    Binds to the provided proxy the provided lock. Basically all proxies binded to the same lock will execute synchronous
    regardless of the execution thread.
    
    @param proxy: @see: registerProxyBinder
        The proxy to bind the lock to.
    @param lock: RLock
        The lock object.
    '''
    assert hasattr(lock, 'acquire') and hasattr(lock, 'release'), 'Invalid lock %s' % lock
    registerProxyBinder(proxy)
    
    bindBeforeListener(proxy, lambda * args: lock.acquire(), index=0)
    bindAfterListener(proxy, lambda * args: lock.release(), index=1001)
    bindExceptionListener(proxy, lambda * args: lock.release(), index=1001)
