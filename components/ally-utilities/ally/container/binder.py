'''
Created on Aug 24, 2011

@package: ally utilities
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides implementations for easy binding of listeners to any objects also provides the means of integrating with proxies.
'''

from .proxy import IProxyHandler, Execution, ProxyCall, analyzeProxy, \
    registerProxyHandler, hasProxyHandler
from abc import ABCMeta

# --------------------------------------------------------------------

INDEX_DEFAULT = 'default'
# The default index where listeners that have not specified a index are added.
INDEX_LOCK_BEGIN = 'lock_begin'
# The begin lock index.
INDEX_LOCK_END = 'lock_end'
# The end lock index.

EVENT_BEFORE_CALL = 'before'
# Listener key that is triggered before a proxy method call is made.
EVENT_AFTER_CALL = 'after'
# Listener key that is triggered after a proxy method call is made.
EVENT_EXCEPTION_CALL = 'exception'
# Listener key that is triggered if a proxy method raises an exception.

indexes = [INDEX_LOCK_BEGIN, INDEX_DEFAULT, INDEX_LOCK_END]
# The list of known indexes in their priority order.

# --------------------------------------------------------------------

class BindableSupportMeta(ABCMeta):
    '''
    Meta class for bindable support that allows for instance check base on the '_ally_listeners' attribute.
    '''

    def __instancecheck__(self, instance):
        '''
        @see: ABCMeta.__instancecheck__
        '''
        if super().__instancecheck__(instance): return True
        return isinstance(getattr(instance, '_ally_listeners', None), dict)

class BindableSupport(metaclass=BindableSupportMeta):
    '''
    Class that provides the support for bindable objects.
    '''
    __slots__ = ('_ally_listeners',)

    def __init__(self):
        '''
        Construct the bineable class with empty listeners.
        '''
        self._ally_listeners = {} # This will allow the model class to be binded with listeners

# --------------------------------------------------------------------

def indexAfter(index, after):
    '''
    Register the index as being after the specified after index.
    
    @param index: string
        The index to register.
    @param after: string
        The index to register after.
    @return: string
        The index.
    '''
    assert isinstance(index, str), 'Invalid index %s' % index
    assert isinstance(after, str), 'Invalid after index %s' % after
    if index in indexes: raise ValueError('The index %r is already registered' % index)
    indexes.insert(indexes.index(after) + 1, index)
    return index

def indexBefore(index, before):
    '''
    Register the index as being before the specified before index.
    
    @param index: string
        The index to register.
    @param before: string
        The index to register before.
    @return: string
        The index.
    '''
    assert isinstance(index, str), 'Invalid index %s' % index
    assert isinstance(before, str), 'Invalid before index %s' % before
    if index in indexes: raise ValueError('The index %r is already registered' % index)
    if index not in indexes:
        indexes.insert(indexes.index(before), index)
        # The index is already registered
    return index

# --------------------------------------------------------------------

def bindListener(to, key, listener, index=INDEX_DEFAULT):
    '''
    Binds the listener to the provided to object.
    
    @param to: object
        The object to bind the listeners to.
    @param key: object immutable|list(object immutable)|tuple(object immutable)
        The key to associate with the listener, this key will be used to associate the listener to a group that
        will be used in different situations.
    @param listener: callable|list(callable)|tuple(callable)
        A Callable that is called as listener.
    @param index: string
        The index at which to position the listener.
    '''
    assert isinstance(to, BindableSupport), 'The object %s is not bindeable' % to

    keys = key if isinstance(key, (list, tuple)) else [key]
    addlist = list(listener) if isinstance(listener, (list, tuple)) else [listener]
    assert addlist, 'At least one listener is required'
    assert isinstance(index, str), 'Invalid index %s' % index
    if index not in indexes: raise ValueError('Unknown index %s' % index)
    for key in keys:
        listeners = to._ally_listeners.get(key)
        if listeners:
            l = listeners.get(index)
            if not l:
                l = addlist
                listeners[index] = l
            else:
                l.extend(addlist)
        else:
            to._ally_listeners[key] = {index:addlist}

def clearBindings(to, *keys):
    '''
    Clear all listener bindings for the provided keys.
    
    @param to: object
        The object to clear the bindings.
    @param keys: arguments(object immutable)
        The keys to be cleared, if none specified than all listeners are removed.
    '''
    assert isinstance(to, BindableSupport), 'The object %s is not bindeable' % to

    if not keys:
        try:
            to._ally_listeners.clear()
        except AttributeError: pass
    else:
        try:
            for key in keys: to._ally_listeners.pop(key, None)
        except AttributeError: pass

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
    assert isinstance(to, BindableSupport), 'The object %s is not bindeable' % to

    try: listeners = to._ally_listeners.get(key)
    except AttributeError: pass
    else:
        if listeners:
            for index in indexes:
                listenersList = listeners.get(index)
                if listenersList:
                    for listener in listenersList:
                        if listener(*args) == False:
                            return False
    return True

# --------------------------------------------------------------------

def bindBeforeListener(to, listener, index=INDEX_DEFAULT):
    '''
    @see: bindListener
    The listener has to accept a parameter with the list of arguments and a parameter with the dictionary of
    key arguments. The listeners can alter the structure of the arguments and will be reflected into the
    actual call of the method. If a listener will return False than the invoking will not take place and 
    neither the after call listeners will not be invoked.
    '''
    bindListener(to, EVENT_BEFORE_CALL, listener, index)

def bindAfterListener(to, listener, index=INDEX_DEFAULT):
    '''
    @see: bindListener
    The listener has to accept a parameter containing the return value. If a listener will return False it 
    will block the call to the rest of the exception listeners.
    '''
    bindListener(to, EVENT_AFTER_CALL, listener, index)

def bindExceptionListener(to, listener, index=INDEX_DEFAULT):
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
    if not hasProxyHandler(BINDING_HANDLER, proxy): registerProxyHandler(BINDING_HANDLER, proxy)

class BindingHandler(IProxyHandler):
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

        try:
            if callListeners(proxy, EVENT_BEFORE_CALL, execution.args, execution.keyargs):
                if callListeners(proxyCall, EVENT_BEFORE_CALL, execution.args, execution.keyargs):
                    value = execution.invoke()
                    if callListeners(proxy, EVENT_AFTER_CALL, value):
                        callListeners(proxyCall, EVENT_AFTER_CALL, value)
                    return value
        except Exception as e:
            if callListeners(proxy, EVENT_EXCEPTION_CALL, e):
                callListeners(proxyCall, EVENT_EXCEPTION_CALL, e)
            raise


BINDING_HANDLER = BindingHandler()
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

    def acquire(*args): lock.acquire()
    def release(*args): lock.release()

    bindBeforeListener(proxy, acquire, index=INDEX_LOCK_BEGIN)
    bindAfterListener(proxy, release, index=INDEX_LOCK_END)
    bindExceptionListener(proxy, release, index=INDEX_LOCK_END)
