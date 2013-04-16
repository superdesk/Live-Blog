'''
Created on Feb 23, 2013

@package: ally base
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the entity bind operations.
'''

from ..support.util_sys import callerLocals
from ._impl._assembly import Assembly
from ._impl._setup import register, SetupSource
from ._impl._support import classesFrom, SetupEntityProxy
from .impl.proxy import IProxyHandler, registerProxyHandler
from ally.container.error import SetupError
from ally.support.util import iterRefClass
from collections import Iterable
from inspect import ismodule

# --------------------------------------------------------------------

def bindToEntities(*classes, binders=None, module=None):
    '''
    Creates entity implementation proxies for the provided entities classes found in the provided module. The binding is
    done at the moment of the entity creation so the binding is not dependent of the declared entity return type.

    @param classes: arguments(string|class|AOPClasses)
        The classes to be proxied.
    @param binders: Callable|list[Callable]|tuple(Callable)|SetupSource
        The binders to be invoked when a proxy is created. The binders Callable's will take one argument that is the newly
        created proxy instance.
    @param module: module|None
        If the setup module is not provided than the calling module will be considered.
    '''
    binders = processBinders(binders)
    assert binders, 'At least one binder is required'
    if module:
        assert ismodule(module), 'Invalid setup module %s' % module
        registry = module.__dict__
        group = module.__name__
    else:
        registry = callerLocals()
        assert '__name__' in registry, 'The bind to entities call needs to be made directly from the setup module'
        group = registry['__name__']
    register(SetupEntityProxy(group, classesFrom(classes), binders), registry)

def intercept(*references, handlers=None):
    '''
    Create an intercept binder that will only add the proxy handlers for the specified class and optionally the methods.
    
    @param references: arguments[class|tuple(class, string)]
        The class function references add the binders for.
    @param handlers: IProxyHandler|callable|Iterable(IProxyHandler)|Iterable(callable)
        The proxy handlers to be registered for the class and methods, also callable (setup functions) are allowed that 
        provide the proxy handler(s) and take no arguments, the callable's will be invoked only at the binding process.
    '''
    assert handlers, 'At least one proxy handler is required'
    classWithFn = iterRefClass(references)
    assert classWithFn, 'At least one reference or class is required'
    def binderIntercept(proxy):
        for clazz, methods in classWithFn.items():
            if isinstance(proxy, clazz):
                for handler in processHandlers(handlers):
                    if methods:
                        for method in methods: registerProxyHandler(handler, getattr(proxy, method))
                    else:
                        registerProxyHandler(handler, proxy)
    return binderIntercept

# --------------------------------------------------------------------

class BinderSetup:
    '''
    Provides a binder that uses a setup function in order to get the list of binders. The binders are fetched from the setup
    only when the first binding is done.
    '''
    __slots__ = ('_source', '_binders')
    
    def __init__(self, setup):
        '''
        Construct the bind repository.
        
        @param setup: SetupSource
            The setup to use as the source for the binders.
        '''
        assert isinstance(setup, SetupSource), 'Invalid setup %s' % setup
        
        self._source = setup.name
        self._binders = None
        
    def __call__(self, proxy):
        '''
        Called for binding.
        '''
        if not self._binders:
            binders = Assembly.process(self._source)
            if isinstance(binders, (list, tuple)): self._binders = binders
            elif callable(binders): self._binders = (binders,)
            else: raise SetupError('Invalid binders provided from %s' % self._source)
            for binder in self._binders: assert callable(binder), 'Invalid binder call %s' % binder 
        for binder in self._binders: binder(proxy)

# --------------------------------------------------------------------

def processBinders(binders):
    '''
    Process the binders of different types to a list of callable binders.
    
    @param binders: None|Callable|list[Callable]|tuple(Callable)|SetupSource
        The binders to be processed to a binders callables list.
    @return: list[Callable]
        The processed binders.
    '''
    processed = []
    if isinstance(binders, (list, tuple)): processed.extend(binders)
    elif binders: processed.append(binders)
    
    for k in range(len(processed)):
        if isinstance(processed[k], SetupSource): processed[k] = BinderSetup(processed[k])
    
    return processed

def processHandlers(handlers):
    '''
    Process the proxy handlers of different types to a list of proxy handlers.
    
    @param handlers: IProxyHandler|callable|Iterable(IProxyHandler)|Iterable(callable)
        The handlers to be processed to a proxy handlers list.
    @return: list[IProxyHandler]
        The processed handlers.
    '''
    processed = []
    if isinstance(handlers, Iterable):
        for handler in handlers:
            if callable(handler): processed.extend(processHandlers(handler()))
            else:
                assert isinstance(handler, IProxyHandler), 'Invalid proxy handler %s' % handler
                processed.append(handler)
                
    elif callable(handlers):
        processed.extend(processHandlers(handlers()))
    else:
        assert isinstance(handlers, IProxyHandler), 'Invalid proxy handlers %s' % handlers
        processed.append(handlers)
    return processed
