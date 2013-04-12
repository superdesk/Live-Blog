'''
Created on Sep 23, 2011

@package: ally base
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the IoC (Inversion of Control or dependency injection) services. Attention the IoC should always be used from a
single thread at one time.
'''

from ..support.util_sys import callerLocals
from ._impl._entity import Initializer
from ._impl._setup import SetupEntity, SetupSource, SetupConfig, SetupFunction, \
    SetupEvent, SetupEventReplace, SetupSourceReplace, SetupStart, SetupEventCancel, \
    register, SetupConfigReplace, setupsOf
from .error import SetupError
from .impl.priority import Priority
from functools import partial, update_wrapper
from inspect import isclass, ismodule, getfullargspec, isfunction, cleandoc
import logging

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

PRIORITY_FINAL = Priority()
PRIORITY_LAST = Priority(PRIORITY_FINAL)
PRIORITY_NORMAL = Priority(PRIORITY_LAST)
PRIORITY_FIRST = Priority(PRIORITY_NORMAL)
PRIORITY_TOP = Priority(PRIORITY_FIRST)

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
    
# --------------------------------------------------------------------

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
    hasType, type = process(function)
    if hasType:
        if not isclass(type):
            raise SetupError('Expected a class as the return annotation for function %s' % function)
        else: types = (type,)
    else: types = ()
    return update_wrapper(register(SetupEntity(function, types=types), callerLocals()), function)

def config(*args):
    '''
    Decorator for configuration setup functions.
    For the configuration type the function will be searched for the return annotation and consider that as the type,
    if no annotation is present than this setup function is not known by return type. This creates problems whenever
    the configuration will be set externally because no validation or transformation is not possible.
    '''
    if not args: return config
    assert len(args) == 1, 'Expected only one argument that is the decorator function, got %s arguments' % len(args)
    function = args[0]
    hasType, type = process(function)
    if hasType:
        if not isclass(type):
            raise SetupError('Expected a class as the return annotation for function %s' % function)
        else: types = (type,)
    else: types = ()
    if not function.__name__.islower():
        raise SetupError('Invalid name %r for configuration, needs to be lower case only' % function.__name__)
    return update_wrapper(register(SetupConfig(function, types=types), callerLocals()), function)

def doc(setup, doc):
    '''
    Updates the documentation of the provided configuration setup.
    
    @param setup: SetupConfig
        The configuration setup to update the documentation for.
    @param doc: string
        The documentation to update with, automatically the provided documentation will start on a new line.
    '''
    assert isinstance(setup, (SetupConfig, SetupConfigReplace)), 'Invalid configuration setup %s' % setup
    assert isinstance(doc, str), 'Invalid documentation %s' % doc
    
    if isinstance(setup, SetupConfigReplace): setup = setup.target
    if setup.documentation is not None: setup.documentation += '\n%s' % cleandoc(doc)

def before(*setups, auto=True):
    '''
    Decorator for setup functions that need to be called before the other setup functions. If multiple before setup
    functions are provided then the before function will be invoked only for the first setup functions that occurs.
    
    @param setup: arguments[SetupFunction]
        The setup function to listen to.
    @param auto: boolean
        In some cases the event is not called (for instance externally provided configurations) this means is auto managed
        by the container, if placed on False the event is guaranteed to be called regardless of what the container option.
    '''
    if __debug__:
        for setup in setups: assert isinstance(setup, SetupFunction), 'Invalid setup function %s' % setup
    assert isinstance(auto, bool), 'Invalid auto flag %s' % auto
    def decorator(function):
        hasType, type = process(function)
        if hasType: raise SetupError('No return type expected for function %s' % function)
        return update_wrapper(register(SetupEvent(function, tuple(setup.name for setup in setups), SetupEvent.BEFORE, auto),
                                       callerLocals()), function)

    return decorator

def after(*setups, auto=True):
    '''
    Decorator for setup functions that need to be called after the other setup functions. If multiple after setup
    functions are provided then the after function will be invoked only after all the setup functions will occur.
    
    @param setups: arguments[SetupFunction]
        The setup function(s) to listen to.
    @param auto: boolean
        In some cases the event is not called (for instance externally provided configurations) this means is auto managed
        by the container, if placed on False the event is guaranteed to be called regardless of what the container option.
    '''
    if __debug__:
        for setup in setups: assert isinstance(setup, SetupFunction), 'Invalid setup function %s' % setup
    assert isinstance(auto, bool), 'Invalid auto flag %s' % auto
    def decorator(function):
        hasType, type = process(function)
        if hasType: raise SetupError('No return type expected for function %s' % function)
        return update_wrapper(register(SetupEvent(function, tuple(setup.name for setup in setups), SetupEvent.AFTER, auto),
                                       callerLocals()), function)
    return decorator

def replace(setup):
    '''
    Decorator for setup functions that replace other setup functions in the underlying context.
    The decorated function based on the replaced setup it can receive a single argument in which the original value will be
    received.
    
    @param setup: SetupFunction
        The setup function to be replaced.
    '''
    assert isinstance(setup, SetupFunction), 'Invalid setup function %s' % setup
    def decorator(function):
        hasArg, hasType, type = processWithOneArg(function)
        if isinstance(setup, SetupConfig):
            if hasArg: raise SetupError('No argument expected for function %s, when replacing a configuration' % function)
            if hasType: raise SetupError('No return type expected for function %s, when replacing a configuration' % function)
            return update_wrapper(register(SetupConfigReplace(function, setup), callerLocals()), function)
        
        if isinstance(setup, SetupEvent):
            if hasArg: raise SetupError('No argument expected for function %s, when replacing an event' % function)
            if hasType: raise SetupError('No return type expected for function %s, when replacing an event' % function)
            return update_wrapper(register(SetupEventReplace(function, setup), callerLocals()), function)
        
        if hasType:
            if not isclass(type):
                raise SetupError('Expected a class as the return annotation for function %s' % function)
            else: types = (type,)
        else: types = ()

        return update_wrapper(register(SetupSourceReplace(function, setup, hasArg, types), callerLocals()), function)

    return decorator

def start(*args, priority=PRIORITY_NORMAL):
    '''
    Decorator for setup functions that need to be called at IoC start.
    
    @param priority: Priority
        The priority for the start call.
    '''
    if not args: return partial(start, priority=priority)
    assert len(args) == 1, 'Expected only one argument that is the decorator function, got %s arguments' % len(args)
    assert isinstance(priority, Priority), 'Invalid priority %s' % priority
    function = args[0]
    hasType, _type = process(function)
    if hasType: raise SetupError('No return type expected for function %s' % function)
    return update_wrapper(register(SetupStart(function, priority), callerLocals()), function)

# --------------------------------------------------------------------

def cancel(setup):
    '''
    Cancel the provided event setup.
    
    @param setup: SetupEvent
        The event setup to cancel.
    '''
    assert isinstance(setup, SetupEvent), 'Invalid setup %s' % setup
    register(SetupEventCancel(setup), callerLocals())
    
# --------------------------------------------------------------------

def initialize(entity):
    '''
    Initializes the provided entity if the entity is decorated with injected, otherwise no action is taken.
    
    @param entity: object
        The entity to initialize.
    '''
    if entity is not None: Initializer.initialize(entity)

def entityOf(identifier, module=None):
    '''
    Provides the setup function from the provided module (if not specified it will consider the calling module) based on the
    identifier. The identifier can be either a name (string form) or a returned type (class form).
    
    @param identifier: string|class
        The setup function identifier, either the setup name or the setup returned type.
    @param module: module
        The module where to search the setup function.
    @return: function
        The found setup function.
    '''
    assert isinstance(identifier, (str, type)), 'Invalid identifier %s' % identifier
    
    if module is None: register = callerLocals()
    else:
        assert ismodule(module), 'Invalid module %s' % module
        register = module.__dict__
    assert isinstance(register, dict), 'Invalid register %s' % register
    
    setups = setupsOf(register, SetupSource)
    assert setups is not None, 'No setups available in register %s' % register
    
    found = []
    if isinstance(identifier, str):
        assert '__name__' in register, 'The entity of call needs to be made directly from the setup module'
        group = register['__name__']
        if not identifier.startswith('%s.' % group): identifier = '%s.%s' % (group, identifier)
        
        for setup in setups:
            assert isinstance(setup, SetupSource)
            if isinstance(identifier, str):
                if setup.name == identifier: found.append(setup)
    else:
        assert isclass(identifier), 'Invalid identifier class %s' % identifier
        
        for setup in setups:
            assert isinstance(setup, SetupSource)
            if setup.isOf(identifier): found.append(setup)
            
    if not found: raise SetupError('No setup entity as found for \'%s\'' % identifier)
    if len(found) > 1: raise SetupError('To many setup entities found:\n%s\nfor: %s' % 
                                        ('\n'.join(str(setup) for setup in found), identifier))
    return found[0]

# --------------------------------------------------------------------

def process(function):
    '''
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

def processWithOneArg(function):
    '''
    Processes and validates the function as a setup function with one argument allowed.
    
    @param function: function
        The function to be processed.
    @return: tuple(boolean, boolean, object)
        A tuple with a boolean on the first position that indicates if the function has one argument (True) or no
        arguments (False) in the second position a flag indicating if the function has a return type (True) or not, and
        on the last position the return type if available or None.
    '''
    if not isfunction(function): raise SetupError('Expected a function as the argument, got %s' % function)
    if function.__name__ == '<lambda>': raise SetupError('Lambda functions cannot be used %s' % function)
    fnArgs = getfullargspec(function)
    if fnArgs.args and len(fnArgs.args) > 1:
        raise SetupError('The setup function %s can only have one argument' % function)
    if fnArgs.varargs or fnArgs.varkw:
        raise SetupError('The setup function %s cannot have any variable arguments' % function)

    return len(fnArgs.args) > 0, 'return' in fnArgs.annotations, fnArgs.annotations.get('return')
