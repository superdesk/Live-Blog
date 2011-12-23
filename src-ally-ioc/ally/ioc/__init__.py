'''
Created on Sep 23, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the IoC (Inversion of Control or dependency injection) services. Attention the IoC should always be used from a
single thread at one time.
'''

from ..util_sys import isPackage, searchModules, packageModules, callerLocals
from .aop import AOPModules
from .context import NAMES_RESERVED, ContextIoC, addSetupModule
from .indexer import IndexerEventReferenced, IndexerEventStart, IndexerOnlyIf, \
    IndexerReplacerFunction, IndexerConfigurations
from .initializer import Initializer
from .node import SetupError, isConfig, argumentsFor
from .node_extra import EVENT_BEFORE, EVENT_AFTER
from _abcoll import Callable
from functools import partial
from inspect import isclass, ismodule, isfunction
from pkgutil import get_loader
from types import ModuleType
import importlib
import inspect
import os
import re

# --------------------------------------------------------------------

def injected(name=None):
    '''
    Decorator used for entity classes that are involved in the IoC process.
    
    @param name: string|None
        The name of the IoC entity, if not specified it will use the decorated class name making the first
        letter a lower case.
    '''
    if isclass(name):
        # The inject is used without arguments.
        clazz, name = name, name.__name__
        initializer = Initializer(clazz)
        initializer.entityName = name[0].lower() + name[1:]
        return clazz
    raise NotImplementedError()

def onNamedEvent(*args, **keyargs):
    '''
    Decorator used for functions that should be used as an event based setup for the specified entity name.
    
    @param args[0]: string
        The name of the entity that is the scope of the event setup, if not specified than the
        decorated function needs to have only one argument that will be considered as the before use scope. 
    @keyword event: string
        The event name.
    @keyword multiple: boolean|None
        True indicates that the event is allowed to be handled multiple times, False the event should be handled just
        once and None allows the event handler to provide a default behavior based on the reference
        (True for entities, False for configurations)
    '''
    assert 'event' in keyargs, 'Expected an event key argument, got key arguments %s' % keyargs
    event = keyargs.pop('event')
    assert isinstance(event, str), 'Invalid event %s' % event
    
    name = keyargs.pop('name', None)
    assert name is None or isinstance(name, str), 'Invalid name %s' % name
    
    multiple = keyargs.pop('multiple', None)
    assert multiple is None or isinstance(multiple, bool), 'Invalid multiple flag %s' % multiple
    
    wrap = keyargs.pop('wrap', False)
    if args:
        assert len(args) == 1, \
        'Expected only one argument that is the name of the entity setup, got %s arguments' % len(args)
        if not wrap:
            if isinstance(args[0], str): return partial(onNamedEvent, event=event, name=args[0], wrap=True)
            if isinstance(args[0], Callable): wrap = True
            else: raise SetupError('Cannot use argument value %s as a name' % args[0])
    if wrap:
        function = args[0]
        if not isfunction(function): raise SetupError('Expected a function as the argument, got %s' % function)
        
        args, __, __ = argumentsFor(function)
        if name is None:
            args = [argn for argn in args if argn not in NAMES_RESERVED]
            if len(args) != 1: raise SetupError('Expected one argument got %r arguments' % ','.join(args))
            name = args[0]
        IndexerEventReferenced(function, event, name, multiple)
        return function

    return partial(onNamedEvent, event=event, multiple=multiple, wrap=True)

def before(*args, multiple=None):
    '''
    Decorator used for functions that should be used as a setup for the specified entity name before initialization.
    
    @param args[0]: string|None
        The name of the entity that is the scope of the before initialization setup, if not specified than the
        decorated function needs to have only one argument that will be considered as the before use scope.
    @param multiple: boolean|None
        True indicates that the event is allowed to be handled multiple times, False the event should be handled just
        once and None allows the event handler to provide a default behavior based on the reference
        (True for entities, False for configurations)
    '''
    return onNamedEvent(*args, event=EVENT_BEFORE, multiple=multiple)

def after(*args, multiple=None):
    '''
    Decorator used for functions that should be used as a setup for the specified entity name after it is initialize.
    
    @param args[0]: string|None
        The name of the entity that is the scope of the after initialize setup, if not specified than the
        decorated function needs to have only one argument that will be considered as the after initialize scope.
    @param multiple: boolean|None
        True indicates that the event is allowed to be handled multiple times, False the event should be handled just
        once and None allows the event handler to provide a default behavior based on the reference
        (True for entities, False for configurations)
    '''
    return onNamedEvent(*args, event=EVENT_AFTER, multiple=multiple)

def start(*args):
    '''
    Decorator for global events for functions that should be used for the setup start.
    '''
    if not args: return start
    assert len(args) == 1, 'Expected only one argument that is the decorator function, got %s arguments' % len(args)
    function = args[0]
    if not isfunction(function): raise SetupError('Expected a function as the argument, got %s' % function)
    
    IndexerEventStart(function)
    return function

def replace(*args, target=None):
    '''
    Decorator used on functions that should replace other functions.
    
    @param target: string
        The target name to be replaced by this function.
    '''
    if not args: return partial(replace, target=target)
    assert len(args) == 1, 'Expected only one argument that is the decorator function, got %s arguments' % len(args)
    function = args[0]
    if not isfunction(function): raise SetupError('Expected a function as the argument, got %s' % function)
    if target is None: target = function.__name__
    if not isinstance(target, str): raise SetupError('Invalid target %s' % target)
    
    IndexerReplacerFunction(function, target)
    return function

def onlyIf(*args, doc=None, **options):
    '''
    Decorator used on functions that should be considered in the setup process only if the provided configuration
    have the provided value.
    
    @param doc: string
        The description to associate with any configurations that might be first decalred in the decorator.
    @param options: key arguments
        The key is the configuration name with prefix and all, and the value is the required value for the
        configuration.
    '''
    wrap = options.pop('wrap', False)
    if wrap:
        assert len(args) == 1, \
        'Expected only one argument that is the decorator function, got %s arguments' % len(args)
        function = args[0]
        if not isfunction(function): raise SetupError('Expected a function as the argument, got %s' % function)

        IndexerOnlyIf(function, function.__name__, options)

        return function
    else:
        assert doc is None or isinstance(doc, str), 'Invalid documentation %s' % doc
        assert options, 'Need to provide at least one set of options'
        for name in options:
            if not isConfig(name):
                raise SetupError('The argument keys need to be configurations names, got %r' % name)
        return partial(onlyIf, wrap=True, doc=doc, **options)

# --------------------------------------------------------------------

def configurations(configurations):
    '''
    Sets to the loading context the provided configurations dictionary.
    
    @param configurations: dictionary{string, object}
        The configurations dictionary.
    '''
    IndexerConfigurations.place(callerLocals(), configurations)

def modulesIn(*paths):
    '''
    Provides all the modules that are found in the provided package paths.
    
    @param paths: arguments[string|module]
        The package paths to load modules from.
    '''
    new = {}
    for path in paths:
        if isinstance(path, str):
            for modulePath in searchModules(path): new[modulePath] = modulePath
        elif ismodule(path):
            if not isPackage(path):
                raise SetupError('The provided module %r is not a package' % path)
            for modulePath in packageModules(path): new[modulePath] = modulePath
        else: raise SetupError('Cannot use path %s' % path)
    return AOPModules(new)

def modulesOf(*modules):
    '''
    Provides all the modules that are found in the provided package paths that are registered in the package __init__
    module under the __all__ attribute. Attention this will load the __init__ module.
    
    @param modules: arguments[string|module]
        The package modules or paths to load modules from.
    '''
    modules = list(modules)
    new = {}
    while modules:
        module = modules.pop(0)
        if isinstance(module, str): module = importlib.import_module(module)
        if ismodule(module):
            if not isPackage(module):
                raise SetupError('The provided module %r is not a package' % module)
        else: raise SetupError('Cannot use path %s' % module)
        
        new[module.__name__] = module.__name__
        all = module.__dict__.get('__all__')
        if isinstance(all, list):
            for name in all:
                path = module.__name__ + '.' + name
                loader = get_loader(path)
                if loader.is_package(path): modules.append(path)
                else: new[path] = path
    return AOPModules(new)

# --------------------------------------------------------------------

def load(*modules, name='main', config=None):
    '''
    Loads the setup modules.
    
    @param modules: arguments(path|AOPModules|module) 
        The modules that compose the setup.
    @param name: string
        The name of the context, if not provided will use the default.
    @param config: dictionary|None
        The configurations dictionary. This is the top level configurations the values provided here will override any
        other configuration.
    @return: Repository
        The loaded repository.
    '''
    return Repository(modules, name, config)

def assemble(*modules, name='main', config=None):
    '''
    Load and assemble the setup modules.
    
    @param modules: arguments(path|AOPModules|module) 
        The modules that compose the setup.
    @param name: string
        The name of the context, if not provided will use the default.
    @param config: dictionary|None
        The configurations dictionary. This is the top level configurations the values provided here will override any
        other configuration.
    @return: Context
        The assembles context.
    '''
    return load(*modules, name=name, config=config).assemble()

# --------------------------------------------------------------------

class Repository:
    '''
    The loaded setup repository.
    '''
    
    __slots__ = ['_context', '_config']
    
    def __init__(self, modules, name, config=None):
        '''
        Initialize the repository for with the context.
        
        @param context: ContextIoC
        '''
        if config is None: config = {}
        else: assert isinstance(config, dict), 'Invalid configurations %s' % config
        self._context = None
        self._config = config
        self.load(*modules, name=name)
        
    def assemble(self):
        '''
        Assembles the repository.
        
        @return: Context
            The assembled context.
        '''
        self._context.assemble()
        for name, value in self._config.items():
            toPaths = self._context.doSetConfiguration(name, value)
            if not toPaths: raise SetupError('Cannot set configuration %r with value %s' % (name, value))
        return self._context.start()
    
    def load(self, *modules, name='main', config=None):
        '''
        Loads the setup modules as a new context that will be merged into the repository.
        
        @param modules: arguments(path|AOPModules|module) 
            The modules that compose the setup.
        @param name: string
            The name of the context, if not provided will use the default.
        @param config: dictionary|None
            The configurations dictionary. This is the top level configurations the values provided here 
            will override any other configuration.
        @return: self
            The repository for chaining purposes.
        '''
        if config is not None:
            assert isinstance(config, dict), 'Invalid configurations %s' % config
            self._config.update(config)
        
        self._context = ContextIoC(name, self._context)
        for module in modules:
            if isinstance(module, str): module = importlib.import_module(module)
            if ismodule(module):
                if not hasattr(module, '__path__'):
                    addSetupModule(self._context, module)
                    continue
                else: module = modulesOf(module)
    
            if isinstance(module, AOPModules):
                assert isinstance(module, AOPModules)
                for m in module.load().asList(): addSetupModule(self._context, m)
            else: raise SetupError('Cannot use module %s' % module)
        return self._context
