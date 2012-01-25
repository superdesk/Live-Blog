'''
Created on Sep 23, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the IoC (Inversion of Control or dependency injection) services. Attention the IoC should always be used from a
single thread at one time.
'''

from ..support.util_sys import callerLocals
from ._impl.entity_handler import Initializer
from ._impl.ioc_setup import SetupEntity, SetupConfig, SetupFunction, SetupEvent, \
    Context, SetupReplace, SetupStart, SetupError, register, ConfigError, Assembly
from ._impl.aop_container import AOPModules
from functools import partial, update_wrapper
from inspect import isclass, ismodule, getfullargspec, isfunction
import importlib
import logging

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

SetupError = SetupError
ConfigError = ConfigError

# --------------------------------------------------------------------

def injected(*args):
    '''
    Decorator used for entity classes that are involved in the IoC process.
    '''
    if not args: return injected
    assert len(args) == 1, 'Expected only one argument that is the decorator class, got %s arguments' % len(args)
    clazz = args[0]
    assert isclass(clazz), 'Invalid class %s' % clazz
    Initializer(clazz)
    return clazz

def entity(*args):
    '''
    Decorator for entity setup functions.
    For the entity type the function will be searched for the return annotation and consider that as the type, if no
    annotation is present than this setup function is not known by return type this will exclude this setup function
    from entities searched by type.
    '''
    if not args: return entity
    assert len(args) == 1, 'Expected only one argument that is the decorator function, got %s arguments' % len(args)
    function = args[0]
    hasType, type = _process(function)
    if hasType and not isclass(type):
        raise SetupError('Expected a class as the return annotation for function %s' % function)
    return update_wrapper(register(SetupEntity(function, type=type), callerLocals()), function)

def config(*args, alias=None):
    '''
    Decorator for configuration setup functions.
    For the configuration type the function will be searched for the return annotation and consider that as the type,
    if no annotation is present than this setup function is not known by return type. This creates problems whenever
    the configuration will be set externally because no validation or transformation is not possible.
    
    @param alias: string|tuple(string)|list(string)
        The alias(es) for this configuration, all the the configurations found that have the provided aliases will point
        to this configuration setup, is like a replace for entity but it is able to replace multiple configurations and
        if the alias is not found in the assembly is simply ignored.
    '''
    if not args: return partial(config, alias=alias)
    assert len(args) == 1, 'Expected only one argument that is the decorator function, got %s arguments' % len(args)
    function = args[0]
    if alias:
        if not isinstance(alias, (tuple, list)): alias = (alias,)
        if __debug__:
            for name in alias: assert isinstance(name, str), 'Invalid alias name %s' % name
    hasType, type = _process(function)
    if hasType and not isclass(type):
        raise SetupError('Expected a class as the return annotation for function %s' % function)
    if not function.__name__.islower():
        raise SetupError('Invalid name %r for configuration, needs to be lower case only' % function.__name__)
    return update_wrapper(register(SetupConfig(function, alias, type=type), callerLocals()), function)

def before(setup):
    '''
    Decorator for setup functions that need to be called before other setup functions.
    
    @param setup: SetupFunction
        The setup function to listen to.
    '''
    def decorator(target, function):
        hasType, type = _process(function)
        if hasType: raise SetupError('No return type expected for function %s' % function)
        return update_wrapper(register(SetupEvent(function, target, SetupEvent.BEFORE), callerLocals()), function)
    
    assert isinstance(setup, SetupFunction), 'Invalid setup function %s' % setup
    return partial(decorator, setup.name)

def after(setup):
    '''
    Decorator for setup functions that need to be called after other setup functions.
    
    @param setup: SetupFunction
        The setup function to listen to.
    '''
    def decorator(target, function):
        hasType, type = _process(function)
        if hasType: raise SetupError('No return type expected for function %s' % function)
        return update_wrapper(register(SetupEvent(function, target, SetupEvent.AFTER), callerLocals()), function)
    
    assert isinstance(setup, SetupFunction), 'Invalid setup function %s' % setup
    return partial(decorator, setup.name)
    
def replace(setup):
    '''
    Decorator for setup functions that replace other setup functions in the underlying context.
    
    @param setup: SetupFunction
        The setup function to be replaced.
    '''
    def decorator(name, function):
        _process(function)
        return update_wrapper(register(SetupReplace(function, name), callerLocals()), function)
    
    assert isinstance(setup, SetupFunction), 'Invalid setup function %s' % setup
    return partial(decorator, setup.name)
    
def start(*args):
    '''
    Decorator for setup functions that need to be called at IoC start.
    '''
    if not args: return start
    assert len(args) == 1, 'Expected only one argument that is the decorator function, got %s arguments' % len(args)
    function = args[0]
    hasType, _type = _process(function)
    if hasType: raise SetupError('No return type expected for function %s' % function)
    return update_wrapper(register(SetupStart(function), callerLocals()), function)

# --------------------------------------------------------------------

def open(*modules, config=None):
    '''
    Load and assemble the setup modules and keeps them opened for retrieving and processing values. Call the close
    function after finalization.
    
    @param modules: arguments(path|AOPModules|module) 
        The modules that compose the setup.
    @param config: dictionary|None
        The configurations dictionary. This is the top level configurations the values provided here will override any
        other configuration.
    @return: object
        The assembly object.
    '''
    context = Context()
    for module in modules:
        if isinstance(module, str): module = importlib.import_module(module)
        
        if ismodule(module): context.addSetupModule(module)
        elif isinstance(module, AOPModules):
            assert isinstance(module, AOPModules)
            for m in module.load().asList(): context.addSetupModule(m)
        else: raise SetupError('Cannot use module %s' % module)
        
    assembly = context.assemble(config)
    Assembly.stack.append(assembly)
    return assembly

def close():
    '''
    Closes the ongoing assembly.
    '''
    assert Assembly.stack, 'No assembly available for close'
    Assembly.stack.pop()

def initialize(entity):
    '''
    Initializes the provided entity if the entity is decorated with injected, otherwise no action is taken.
    
    @param entity: object
        The entity to initialize.
    '''
    if entity is not None: Initializer.initialize(entity)

# --------------------------------------------------------------------

def _process(function):
    '''
    FOR INTERNAL USE ONLY!
    Processes and validates the function as a setup function.
    
    @param function: function
        The function to be processed.
    @return: tuple(boolean, object)
        A tuple with a boolean on the first position that indicates if the function has a return type (True) or not, and
        on the second position the return type if available or None.
    '''
    if not isfunction(function): raise SetupError('Expected a function as the argument, got %s' % function)
    if function.__name__ == '<lambda>': raise SetupError('Lambda functions cannot be used %s' % function)
    fnArgs = getfullargspec(function)
    if fnArgs.args or fnArgs.varargs or fnArgs.varkw:
        raise SetupError('The setup function %s cannot have any type of arguments' % function)

    return 'return' in fnArgs.annotations, fnArgs.annotations.get('return')
