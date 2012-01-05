'''
Created on Sep 23, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the IoC (Inversion of Control or dependency injection) services. Attention the IoC should always be used from a
single thread at one time.
'''

from ..support.util import Attribute
from ..support.util_sys import callerLocals
from .aop import AOPModules
from _abcoll import Callable
from functools import partial, update_wrapper
from inspect import isclass, isfunction, getfullargspec, ismodule, isgenerator
from itertools import chain
import abc
import importlib
import logging

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

class SetupError(Exception):
    '''
    Exception thrown when there is a setup problem.
    '''

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
    hasType, type = _processFunction(function)
    if hasType and not isclass(type):
        raise SetupError('Expected a class as the return annotation for function %s' % function)
    return update_wrapper(registerSetup(SetupEntity(function, type)), function)

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
    hasType, type = _processFunction(function)
    if hasType and not isclass(type):
        raise SetupError('Expected a class as the return annotation for function %s' % function)
    return update_wrapper(registerSetup(SetupConfig(function, type)), function)

def before(setup):
    '''
    Decorator for setup functions that need to be called before other setup functions.
    
    @param setup: SetupFunction
        The setup function to listen to.
    '''
    def decorator(target, function):
        hasType, type = _processFunction(function)
        if hasType: raise SetupError('No return type expected for function %s' % function)
        return update_wrapper(registerSetup(SetupEvent(function, target, SetupEvent.BEFORE)), function)
    
    assert isinstance(setup, SetupFunction), 'Invalid setup function %s' % setup
    return partial(decorator, setup.name)

def after(setup):
    '''
    Decorator for setup functions that need to be called after other setup functions.
    
    @param setup: SetupFunction
        The setup function to listen to.
    '''
    def decorator(target, function):
        hasType, type = _processFunction(function)
        if hasType: raise SetupError('No return type expected for function %s' % function)
        return update_wrapper(registerSetup(SetupEvent(function, target, SetupEvent.AFTER)), function)
    
    assert isinstance(setup, SetupFunction), 'Invalid setup function %s' % setup
    return partial(decorator, setup.name)
    
def replace(setup):
    '''
    Decorator for setup functions that replace other setup functions in the underlying context.
    
    @param setup: SetupFunction
        The setup function to be replaced.
    '''
    def decorator(name, function):
        _processFunction(function)
        return update_wrapper(registerSetup(SetupReplace(function, name)), function)
    
    assert isinstance(setup, SetupFunction), 'Invalid setup function %s' % setup
    return partial(decorator, setup.name)
    
def start(*args):
    '''
    Decorator for setup functions that need to be called at IoC start.
    '''
    if not args: return start
    assert len(args) == 1, 'Expected only one argument that is the decorator function, got %s arguments' % len(args)
    function = args[0]
    hasType, _type = _processFunction(function)
    if hasType: raise SetupError('No return type expected for function %s' % function)
    return update_wrapper(registerSetup(SetupStart(function)), function)

# --------------------------------------------------------------------

def deploy(*modules, name='main', config=None):
    '''
    Load and assemble the setup modules.
    
    @param modules: arguments(path|AOPModules|module) 
        The modules that compose the setup.
    @param name: string
        The name of the context, if not provided will use the default.
    @param config: dictionary|None
        The configurations dictionary. This is the top level configurations the values provided here will override any
        other configuration.
    '''
    context = Context()
    for module in modules:
        if isinstance(module, str): module = importlib.import_module(module)
        
        if ismodule(module): context.addSetupModule(module)
        elif isinstance(module, AOPModules):
            assert isinstance(module, AOPModules)
            for m in module.load().asList(): context.addSetupModule(m)
        else: raise SetupError('Cannot use module %s' % module)
    context.start(config)

# --------------------------------------------------------------------

ATTR_SETUPS = Attribute(__name__, 'setups', list)
# The setups attribute.

def registerSetup(setup, register=None):
    '''
    Register the setup function into the calling module.
    
    @param setup: Setup
        The setup to register into the calling module.
    @param register: dictionary|None
        The register to place the setup in, if None than it will use the caller locals.
    @return: Setup
        The provided setup entity.
    '''
    assert isinstance(setup, Setup), 'Invalid setup %s' % setup
    if not register: register = callerLocals()
    assert isinstance(register, dict), 'Invalid register %s' % register
    if ATTR_SETUPS.hasDict(register): setups = ATTR_SETUPS.getDict(register)
    else: setups = ATTR_SETUPS.setDict(register, [])
    setups.append(setup)
    return setup

# --------------------------------------------------------------------

def _processFunction(function):
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

# --------------------------------------------------------------------

class Initializer(Callable):
    '''
    Class used as the initializer for the entities classes.
    '''
    
    INITIALIZED = Attribute(__name__, 'initialized', bool)
    # Provides the attribute for the initialized flag.
    ARGUMENTS = Attribute(__name__, 'arguments')
    # Provides the attribute for the arguments for initialization.
    
    @staticmethod
    def initializerFor(entity):
        '''
        Provides the Initializer for the provided entity if is available.
        
        @param entity: object
            The entity to provide the initializer for.
        @return: Initializer|None
            The Initializer or None if not available.
        '''
        if not isclass(entity): clazz = entity.__class__
        else: clazz = entity
        initializer = clazz.__dict__.get('__init__')
        if isinstance(initializer, Initializer): return initializer
    
    @classmethod
    def initialize(cls, entity):
        '''
        Initialize the provided entity.
        '''
        assert entity is not None, 'Need to provide an entity to be initialized'
        initializer = Initializer.initializerFor(entity)
        if initializer and not cls.INITIALIZED.get(entity, False):
            assert isinstance(initializer, Initializer)
            if entity.__class__ == initializer._entityClazz:
                args, keyargs = cls.ARGUMENTS.getOwn(entity)
                cls.ARGUMENTS.deleteOwn(entity)
                cls.INITIALIZED.set(entity, True)
                if initializer._entityInit:
                    initializer._entityInit(entity, *args, **keyargs)
                    log.info('Initialized entity %s' % entity)
    
    def __init__(self, clazz):
        '''
        Create a entity initializer for the specified class.
        
        @param clazz: class
            The entity class of this entity initializer.
        '''
        assert isclass(clazz), 'Invalid entity class %s' % clazz
        self._entityClazz = clazz
        self._entityInit = getattr(clazz, '__init__', None)
        setattr(clazz, '__init__', self)
        
    def __call__(self, entity, *args, **keyargs):
        '''
        @see: Callable.__call__
        '''
        assert isinstance(entity, self._entityClazz), 'Invalid entity %s for class %s' % (entity, self._entityClazz)
        if self.INITIALIZED.get(entity, False):
            return self._entityInit(entity, *args, **keyargs)
        assert not self.ARGUMENTS.hasOwn(entity), 'Cannot initialize twice the entity %s' % entity
        self.ARGUMENTS.setOwn(entity, (args, keyargs))

    def __get__(self, entity, owner=None):
        '''
        @see: http://docs.python.org/reference/datamodel.html
        '''
        if entity is not None: return partial(self.__call__, entity)
        return self

# --------------------------------------------------------------------

class Assembly:
    '''
    Provides the assembly data.
    '''
    
    def __init__(self, configurations):
        '''
        Construct the assembly.
        
        @param configurations: dictionary{string, object}
            The configurations used for the class map indexing.
        @ivar calls: dictionary{string, Callable}
            A dictionary containing as a key the name of the call to be resolved and as a value the Callable that will
            resolve the name. The Callable will not take any argument.
        @ivar configurationsUsed: set{string}
            A set containing the used configurations names.
        @ivar start: list[Callable]
            A list of Callable that are used as IoC start calls.
        '''
        assert isinstance(configurations, dict), 'Invalid configurations %s' % configurations
        self.calls = {}
        self.configurations = configurations
        self.configurationsUsed = set()
        self.start = []

class Setup:
    '''
    The setup entity. This class provides the means of indexing setup Callable objects.
    '''
    
    priority = 1
    # Provides the assemble priority for the setup.

    def index(self, assembly):
        '''
        Indexes the call of the setup to the calls map.
        
        @param assembly: Assembly
            The assembly to index on.
        '''
        
    def assemble(self, assembly):
        '''
        Assemble the calls map and also add the call starts. This method will be invoked after all index methods have
        been finalized.
        
        @param assembly: Assembly
            The assembly to assemble aditional behaviour on.
        '''
        
class SetupFunction(Setup, Callable):
    '''
    A setup indexer based on a function.
    '''
    
    def __init__(self, function):
        '''
        Constructs the setup call for the provided function.
        
        @param function: function
            The function of the setup call.
        '''
        assert isfunction(function), 'Invalid function %s' % function
        assert function.__name__ != '<lambda>', 'Lambda functions cannot be used %s' % function
        if __debug__:
            fnArgs = getfullargspec(function)
            assert not (fnArgs.args or fnArgs.varargs or fnArgs.varkw), \
            'The setup function %r cannot have any type of arguments' % self._name
        self._function = function
        self._name = self._function.__module__ + '.' + self._function.__name__
    
    name = property(lambda self: self._name, doc=
'''
@type name: string
    The name of the setup call.
''')
    
    def __call__(self):
        '''
        Provides the actual setup of the call.
        '''
        return Context.process(self._name)

class SetupSource(SetupFunction):
    '''
    Provides the setup for retrieving a value based on a setup function.
    '''
    
    def __init__(self, function, type=None):
        '''
        @see: SetupFunction.__init__
        
        @param type: class|None
            The type(class) of the value that is being delivered by this source.
        '''
        SetupFunction.__init__(self, function)
        assert type is None or isclass(type), 'Invalid type %s' % type
        self._type = type
        
class SetupEntity(SetupSource):
    '''
    Provides the entity setup.
    '''
    
    def __init__(self, function, type=None):
        '''
        @see: SetupSource.__init__
        '''
        SetupSource.__init__(self, function, type)
    
    def index(self, assembly):
        '''
        @see: Setup.index
        '''
        assert isinstance(assembly, Assembly), 'Invalid assembly %s' % assembly
        if self._name in assembly.calls: raise SetupError('There is already a setup call for name %r' % self._name)
        assembly.calls[self._name] = CallEntity(self._function, self._type)
        
class SetupConfig(SetupSource):
    '''
    Provides the configuration setup.
    '''
    
    def __init__(self, function, type=None):
        '''
        @see: SetupSource.__init__
        '''
        SetupSource.__init__(self, function, type)
    
    def index(self, assembly):
        '''
        @see: Setup.index
        '''
        assert isinstance(assembly, Assembly), 'Invalid assembly %s' % assembly
        if self._name in assembly.calls: raise SetupError('There is already a setup call for name %r' % self._name)
        hasValue, value = False, None
        for name, val in assembly.configurations.items():
            if name == self._name or self._name.endswith('.' + name):
                if name in assembly.configurationsUsed:
                    raise SetupError('The configuration %r is already in use and the configuration %r cannot use it '
                                     'again, provide a more detailed path for the configuration (ex: "ally_core.url" '
                                     'instead of "url")' % (name, self._name))
                assembly.configurationsUsed.add(name)
                hasValue, value = True, val
        assembly.calls[self._name] = CallConfig(self._function, self._type, hasValue, value)

class SetupReplace(SetupFunction):
    '''
    Provides the setup for replacing an entity or configuration setup function.
    '''
    
    priority = 2
    
    def __init__(self, function, name):
        '''
        @see: SetupFunction.__init__
        
        @param name: string
            The setup name to be replaced.
        '''
        SetupFunction.__init__(self, function)
        assert isinstance(name, str), 'Invalid replace name %s' % name
        self._name = name # We actually set the setup replace name with the replacer name.
        
    def assemble(self, assembly):
        '''
        @see: Setup.assemble
        '''
        assert isinstance(assembly, Assembly), 'Invalid assembly %s' % assembly
        if self._name not in assembly.calls:
            raise SetupError('There is no setup call for name %r to be replaced' % self._name)
        call = assembly.calls[self._name]
        if not isinstance(call, Call):
            raise SetupError('Cannot find any Call object for name %r to be replaced' % self._name)
        assert isinstance(call, Call)
        call.call = self._function
        
class SetupEvent(SetupFunction):
    '''
    Provides the setup event function.
    '''
    
    priority = 3
    
    BEFORE = 'before'
    AFTER = 'after'
    EVENTS = [BEFORE, AFTER]
    
    def __init__(self, function, target, event):
        '''
        @see: SetupFunction.__init__
        
        @param target: string
            The target name of the event call.
        @param event: string
            On of the defined EVENTS.
        '''
        SetupFunction.__init__(self, function)
        assert isinstance(target, str), 'Invalid target %s' % target
        assert event in self.EVENTS, 'Invalid event %s' % event
        self._target = target
        self._event = event
        
    def index(self, assembly):
        '''
        @see: Setup.index
        '''
        assert isinstance(assembly, Assembly), 'Invalid assembly %s' % assembly
        if self._name in assembly.calls: raise SetupError('There is already a setup call for name %r' % self._name)
        assembly.calls[self._name] = CallEvent(self._function)
        
    def assemble(self, assembly):
        '''
        @see: Setup.assemble
        '''
        assert isinstance(assembly, Assembly), 'Invalid assembly %s' % assembly
        if self._target not in assembly.calls:
            raise SetupError('There is no setup call for target %r to add the event on' % self._target)
        call = assembly.calls[self._target]
        if not isinstance(call, Call):
            raise SetupError('Cannot find any Call object for target %r to add the event' % self._target)
        assert isinstance(call, Call)
        if self._event == self.BEFORE: call.addBefore(partial(Context.process, self._name))
        elif self._event == self.AFTER: call.addAfter(partial(Context.process, self._name))
        
    def __call__(self):
        '''
        Provides the actual setup of the call.
        '''
        raise SetupError('Cannot invoke the event setup %r directly' % self._name)
    
class SetupStart(SetupFunction):
    '''
    Provides the start function.
    '''
    
    def __init__(self, function):
        '''
        @see: SetupFunction.__init__
        '''
        SetupFunction.__init__(self, function)
        
    def index(self, assembly):
        '''
        @see: Setup.index
        '''
        assert isinstance(assembly, Assembly), 'Invalid assembly %s' % assembly
        if self._name in assembly.calls: raise SetupError('There is already a setup call for name %r' % self._name)
        assembly.calls[self._name] = CallEvent(self._function)
        
    def assemble(self, assembly):
        '''
        @see: Setup.assemble
        '''
        assert isinstance(assembly, Assembly), 'Invalid assembly %s' % assembly
        assembly.start.append(partial(Context.process, self._name))
        
# --------------------------------------------------------------------

class Call(Callable):
    '''
    Provides the base class of calls. Is just a simple wrapper for another Callable object but it provides listeners for
    the call process.
    '''
    
    def __init__(self, call):
        '''
        Constructs the call.
        
        @param call: Callable
            The call that is used by this Call in order to resolve.
        '''
        self.call = call
        self._listenersBefore = []
        self._listenersAfter = []
        
    def setCall(self, call):
        '''
        Sets the call for this Call.
        
        @param call: Callable
            The call that is used by this Call in order to resolve.
        '''
        assert isinstance(call, Callable), 'Invalid callable %s' % call
        self._call = call
        
    call = property(lambda self: self._call, setCall, doc=
'''
@type call: Callable
    The call used for resolve.
''')
        
    def addBefore(self, listener):
        '''
        Adds a before listener.
        
        @param listener: Callable
            A callable that takes no parameters that will be invoked before the call is processed.
        '''
        assert isinstance(listener, Callable), 'Invalid listener %s' % listener
        self._listenersBefore.append(listener)
        
    def addAfter(self, listener):
        '''
        Adds an after listener.
        
        @param listener: Callable
            A callable that takes no parameters that will be invoked after the call is processed.
        '''
        assert isinstance(listener, Callable), 'Invalid listener %s' % listener
        self._listenersAfter.append(listener)

class CallSource(Call):
    '''
    Provides the base for calls that are value sources.
    '''
    
    def __init__(self, call, type, hasValue=False, value=None):
        '''
        @see: Call.__init__
        
        @param type: class|None
            The type(class) of the value that is being delivered by this source.
        @param hasValue: boolean
            Flag indicating if this source has a value.
        @param value: object
            The value of the source
        '''
        Call.__init__(self, call)
        assert type is None or isclass(type), 'Invalid type %s' % type
        assert isinstance(hasValue, bool), 'Invalid has value flag %s' % hasValue
        self._type = type
        self._hasValue = hasValue
        self._value = self._validate(value)
        self._processed = False
        
    def _validate(self, value):
        '''
        Validates the provided value against the source type.
        
        @param value: object   
            The value to check.
        @return: object
            The same value as the provided value.
        @raise SetupError: In case the value is not valid.
        '''
        if self._type and value is not None and not isinstance(value, self._type):
            raise SetupError('Invalid value provided %s, expected type %s' % (value, self._type))
        return value

    def __call__(self):
        '''
        Provides the call for the source.
        '''
        if not self._processed:
            self._processed = True
            if self._hasValue:
                for listener in chain(self._listenersBefore, self._listenersAfter): listener()
            else: self._process()
        return self._value

    @abc.abstractclassmethod
    def _process(self):
        '''
        Called in order to process the source value. This method has to set the _hasValue flag and also populate the
        _value attribute.
        '''

class CallEntity(CallSource):
    '''
    Call that resolves an entity setup.
    '''
    
    def __init__(self, call, type):
        '''
        @see: CallSource.__init__
        '''
        CallSource.__init__(self, call, type)
    
    def _process(self):
        '''
        @see: CallSource._process
        '''
        ret = self._call()
        
        if isgenerator(ret): value, generator = next(ret), ret
        else: value, generator = ret, None
        
        assert log.debug('Processed entity %s', value) or True
        self._value = self._validate(value)
        self._hasValue = True
        
        for listener in self._listenersBefore: listener()
        
        if generator:
            try: next(generator)
            except StopIteration: pass
        
        Initializer.initialize(value)

        for listener in self._listenersAfter: listener()
        
        assert log.debug('Finalized entity %s', value) or True
        return value

class CallConfig(CallSource):
    '''
    Call that resolves a configuration setup.
    '''
    
    def __init__(self, call, type, hasValue=False, value=None):
        '''
        @see: CallSource.__init__
        '''
        CallSource.__init__(self, call, type, hasValue, value)
    
    def _process(self):
        '''
        @see: CallSource._process
        '''
        value = self._call()
        assert log.debug('Processed configuration %s', value) or True
        self._value = self._validate(value)
        self._hasValue = True
        
        for listener in chain(self._listenersBefore, self._listenersAfter): listener()
        
        assert log.debug('Finalized configuration %s', value) or True
        return value

class CallEvent(Call):
    '''
    Provides the event call.
    '''
    
    def __init__(self, call):
        '''
        @see: Call.__init__
        '''
        Call.__init__(self, call)
        self._invoked = False

    def __call__(self):
        '''
        Provides the call for the source.
        '''
        if self._invoked: raise SetupError('The event call cannot be dispatched twice')
        self._invoked = True
        
        for listener in self._listenersBefore: listener()
        ret = self._call()
        if ret is not None: raise SetupError('The event call cannot return any value')
        for listener in self._listenersAfter: listener()

# --------------------------------------------------------------------

class Context:
    '''
    Provides the context of the setup functions and setup calls.
    '''
    
    CONTEXTS = []
    # The current setup contexts
    
    @staticmethod
    def process(name):
        '''
        Process the specified name into this context.
        
        @param name: string
            The name to be processed.
        '''
        assert isinstance(name, str), 'Invalid name %s' % name
        if not Context.CONTEXTS: raise SetupError('There is no active context to process')
        ctx = Context.CONTEXTS[-1]
        assert isinstance(ctx, Context)
        if not ctx._calls: raise SetupError('The active context is not started')
        call = ctx._calls.get(name)
        if not isinstance(call, Callable): raise SetupError('Invalid call %s for name %r' % (call, name))
        return call()
    
    def __init__(self):
        '''
        Construct the context.
        '''
        self._setups = []
        self._calls = None

    def addSetupModule(self, module):
        '''
        Adds a new setup module to the context.
        
        @param module: module
            The setup module.
        ''' 
        assert ismodule(module), 'Invalid module setup %s' % module
        setups = ATTR_SETUPS.get(module, None)
        if setups: self._setups.extend(setups)
        else: log.info('No setup found in %s', module)
        
    def start(self, configurations=None):
        '''
        Starts the context, basically call all setup functions that have been decorated with start.
        '''
        assembly = Assembly(configurations or {})
        
        setups = sorted(self._setups, key=lambda setup: setup.priority)
        for setup in setups:
            assert isinstance(setup, Setup), 'Invalid setup %s' % setup
            setup.index(assembly)

        for setup in setups: setup.assemble(assembly)
        
        if not assembly.start: log.error('No IoC start calls to start the setup')
        
        unused = set(assembly.configurations)
        unused = unused.difference(assembly.configurationsUsed)
        if unused: log.warn('Unknown configurations: %r', ', '.join(unused))
        
        self._calls = assembly.calls
        Context.CONTEXTS.append(self)
        try:     
            for call in assembly.start:
                assert isinstance(call, Callable), 'Invalid call %s' % call
                call()
        finally: Context.CONTEXTS.pop()
