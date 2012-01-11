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
from .aop import AOPClasses, AOPModules
from .config import Config
from .proxy import createProxy, ProxyWrapper
from _abcoll import Callable
from functools import partial, update_wrapper
from inspect import isclass, isfunction, getfullargspec, ismodule, isgenerator
from itertools import chain
import importlib
import logging

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

class SetupError(Exception):
    '''
    Exception thrown when there is a setup problem.
    '''

class ConfigError(Exception):
    '''
    Exception thrown when there is a configuration problem.
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

def createEntitySetup(*classes):
    '''
    Creates entity setup functions for the provided classes.
    
    @param classes: arguments(class|AOPClasses)
        The classes to be added setup functions.
    @return: Entities
        The entities repository for the classes setup functions.
    '''
    clazzes = []
    for clazz in classes:
        if isclass(clazz): clazzes.append(clazz)
        elif isinstance(clazz, AOPClasses):
            assert isinstance(clazz, AOPClasses)
            clazzes.extend(clazz.asList())
        else: raise SetupError('Cannot use class %s' % clazz)
    
    registry = callerLocals()
    entities = []
    for clazz in clazzes:
        initializer = Initializer.initializerFor(clazz)
        if initializer: name = initializer.entityName
        else:
            name = clazz.__name__
            name = name[0].lower() + name[1:]
        name = registry['__name__'] + '.' + name
        entities.append(name)
        registerSetup(SetupEntityCreate(name, clazz))
    return Entities(entities)

def createEntityProxy(*classes, prefix='', listeners=None):
    '''
    Creates entity proxies that are for the provided classes.
    
    @param classes: arguments(class|AOPClasses)
        The classes to be proxied.
    @param prefix: string
        The prefix for the entities name to create the proxies for.
    @param listeners: None|Callable|list[Callable]|tuple(Callable)
        The listeners to be invoked when a proxy is created.
    '''
    assert isinstance(prefix, str), 'Invalid prefix %s' % prefix
    
    clazzes = []
    for clazz in classes:
        if isclass(clazz): clazzes.append(clazz)
        elif isinstance(clazz, AOPClasses):
            assert isinstance(clazz, AOPClasses)
            clazzes.extend(clazz.asList())
        else: raise SetupError('Cannot use class %s' % clazz)
    
    if not listeners: listeners = []
    elif not isinstance(listeners, (list, tuple)): listeners = [listeners]
            
    assert isinstance(listeners, (list, tuple)), 'Invalid listeners %s' % listeners
    registerSetup(SetupEntityProxy(prefix, clazzes, listeners))

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
    context.assemble(config).start(config)

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

class Entities:
    '''
    Provides a entities repository. Basically contains setup function references.
    '''
    
    def __init__(self, names):
        '''
        Initialize the context setup.
        
        @param names: list[string]
            A list containing the function names.
        '''
        assert isinstance(names, list), 'Invalid names %s' % names
        if __debug__:
            for name in names: assert isinstance(name, str), 'Invalid function name %s' % name
        self.names = names
        
    def entities(self):
        '''
        Provides all the entities represented by this entities repository.
        
        @return: list[object]
            The list of entities represented by this setup.
        '''
        return [Assembly.process(name) for name in self.names]

# --------------------------------------------------------------------

class Setup:
    '''
    The setup entity. This class provides the means of indexing setup Callable objects.
    '''
    
    priority = 1
    # Provides the assemble priority for the setup.

    def index(self, assembly):
        '''
        Indexes the call of the setup and other data.
        
        @param assembly: Assembly
            The assembly to index on.
        '''
        
    def assemble(self, assembly):
        '''
        Assemble the calls map and also add the call starts. This method will be invoked after all index methods have
        been finalized.
        
        @param assembly: Assembly
            The assembly to assemble additional behavior on.
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
        return Assembly.process(self._name)

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
        if self._name in assembly.callsByName:
            raise SetupError('There is already a setup call for name %r' % self._name)
        call = assembly.callsByName[self._name] = CallEntity(self._function, self._type)
        if self._type: assembly.callsByType.setdefault(self._type, []).append(call)

class SetupEntityCreate(Setup):
    '''
    Provides the create entity setup.
    '''
    
    def __init__(self, name, clazz):
        '''
        Create the setup for creating an entity based on the provided class.
        
        @param name: string
            The name used for the setup function.
        @param clazz: class
            The class to create the entity setup for.
        '''
        assert isinstance(name, str), 'Invalid name %s' % name
        assert isclass(clazz), 'Invalid class %s' % clazz
        self._name = name
        self._class = clazz
    
    def index(self, assembly):
        '''
        @see: Setup.index
        '''
        assert isinstance(assembly, Assembly), 'Invalid assembly %s' % assembly
        if self._name in assembly.callsByName:
            raise SetupError('Cannot create setup function because there is already a setup call for name %r' % 
                             self._name)
        call = assembly.callsByName[self._name] = CallEntity(CreateEntity(self._class), self._class)
        assembly.callsByType.setdefault(self._class, []).append(call)

class SetupEntityFixed(Setup):
    '''
    Provides a fixed entity value.
    '''
    
    def __init__(self, name, entity, type=None):
        '''
        Create the setup for providing a fixed entity setup.
        
        @param name: string
            The name used for the setup function.
        @param entity: object
            The entity to be provided.
        '''
        assert isinstance(name, str), 'Invalid name %s' % name
        assert entity, 'A entity is required' % entity
        if type:
            assert isclass(type), 'Invalid type %s' % type
            self._type = type
        else: self._type = entity.__class__
        self._name = name
        self._entity = entity
    
    def index(self, assembly):
        '''
        @see: Setup.index
        '''
        assert isinstance(assembly, Assembly), 'Invalid assembly %s' % assembly
        if self._name in assembly.callsByName:
            raise SetupError('Cannot add setup function because there is already a setup call for name %r' % self._name)
        call = assembly.callsByName[self._name] = CallDeliverValue(self._entity, self._type)
        assembly.callsByType.setdefault(self._type, []).append(call)

class SetupEntityProxy(Setup):
    '''
    Provides the setup event function.
    '''
    
    priority = 4
    
    def __init__(self, prefix, classes, listeners):
        '''
        Creates a setup that will create proxies for the entities that inherit or are in the provided classes.
        The proxy create process is as follows:
            - find all entity calls that have the name starting with the provided prefix
            - if the entity instance inherits a class from the provided proxy classes it will create a proxy for
              that and wrap the entity instance.
            - after the proxy is created invoke all the proxy listeners.
        
        @param prefix: string
            The name prefix of the call entities to be proxied.
        @param classes: list[class]|tuple(class)
            The classes to create the proxies for.
        @param listeners: list[Callable]|tuple(Callable)
            A list of Callable objects to be invoked when a proxy is created. The Callable needs to take one parameter
            that is the proxy.
        '''
        assert isinstance(prefix, str), 'Invalid prefix %s' % prefix
        assert isinstance(classes, (list, tuple)), 'Invalid classes %s' % classes
        assert isinstance(listeners, (list, tuple)), 'Invalid proxy listeners %s' % listeners
        if __debug__:
            for clazz in classes: assert isclass(clazz), 'Invalid class %s' % clazz
            for call in listeners: assert isinstance(call, Callable), 'Invalid listener %s' % call
        self._prefix = prefix
        self._classes = classes
        self._listeners = listeners
        
    def assemble(self, assembly):
        '''
        @see: Setup.assemble
        '''
        assert isinstance(assembly, Assembly), 'Invalid assembly %s' % assembly
        for name, call in assembly.callsByName.items():
            if name.startswith(self._prefix) and isinstance(call, CallEntity):
                assert isinstance(call, CallEntity)
                call.addInterceptor(self._intercept)
                
    def _intercept(self, value):
        '''
        FOR INTERNAL USE!
        This is the interceptor method used in creating the proxies.
        '''
        if value:
            proxies = [clazz for clazz in self._classes if isinstance(value, clazz)]
            if proxies:
                if len(proxies) > 1:
                    raise SetupError('Cannot create proxy for %s, because to many proxy classes matched %s' % 
                                     (value, proxies))
                proxy = createProxy(proxies[0])
                value = proxy(ProxyWrapper(value))
                
                for listener in self._listeners: listener(value)
        return value
            
class SetupConfig(SetupSource):
    '''
    Provides the configuration setup.
    '''
    
    def __init__(self, function, type=None):
        '''
        @see: SetupSource.__init__
        '''
        SetupSource.__init__(self, function, type)
        if not self._name.islower():
            raise SetupError('Invalid name %r for configuration, needs to be lower case only' % self._name)
    
    def index(self, assembly):
        '''
        @see: Setup.index
        '''
        assert isinstance(assembly, Assembly), 'Invalid assembly %s' % assembly
        if self._name in assembly.callsByName:
            raise SetupError('There is already a setup call for name %r' % self._name)
        hasValue, value = False, None
        for name, val in assembly.configExtern.items():
            if name == self._name or self._name.endswith('.' + name):
                if name in assembly.configUsed:
                    raise SetupError('The configuration %r is already in use and the configuration %r cannot use it '
                                     'again, provide a more detailed path for the configuration (ex: "ally_core.url" '
                                     'instead of "url")' % (name, self._name))
                assembly.configUsed.add(name)
                hasValue, value = True, val
        error = None
        if not hasValue:
            try: 
                value = self._function()
                hasValue = True
            except ConfigError as e: error = e
        if hasValue: assembly.callsByName[self._name] = CallDeliverValue(value, self._type)
        else: assembly.callsByName[self._name] = CallDeliverError(error)
        
        assembly.configurations[self._name] = Config(self._name, value, self._function.__module__,
                                                     self._function.__doc__, str(error) if error else None)

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
        if self._name not in assembly.callsByName:
            raise SetupError('There is no setup call for name %r to be replaced' % self._name)
        call = assembly.callsByName[self._name]
        if not isinstance(call, WithCall):
            raise SetupError('Cannot replace call for name %r' % self._name)
        assert isinstance(call, WithCall)
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
        if self._name in assembly.callsByName:
            raise SetupError('There is already a setup call for name %r' % self._name)
        assembly.callsByName[self._name] = CallEvent(self._function)
        
    def assemble(self, assembly):
        '''
        @see: Setup.assemble
        '''
        assert isinstance(assembly, Assembly), 'Invalid assembly %s' % assembly
        if self._target not in assembly.callsByName:
            raise SetupError('There is no setup call for target %r to add the event on' % self._target)
        call = assembly.callsByName[self._target]
        if not isinstance(call, WithListeners):
            raise SetupError('Cannot find any listener support for target %r to add the event' % self._target)
        assert isinstance(call, WithListeners)
        if self._event == self.BEFORE: call.addBefore(partial(assembly.processForName, self._name))
        elif self._event == self.AFTER: call.addAfter(partial(assembly.processForName, self._name))
        
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
        if self._name in assembly.callsByName:
            raise SetupError('There is already a setup call for name %r' % self._name)
        assembly.callsByName[self._name] = CallEvent(self._function)
        
    def assemble(self, assembly):
        '''
        @see: Setup.assemble
        '''
        assert isinstance(assembly, Assembly), 'Invalid assembly %s' % assembly
        assembly.callsStart.append(partial(assembly.processForName, self._name))

# --------------------------------------------------------------------

class WithListeners:
    '''
    Provides support for listeners to be notified of the call process.
    '''
    
    def __init__(self):
        '''
        Constructs the listener support.
        '''
        self._listenersBefore = []
        self._listenersAfter = []
        
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

class WithCall:
    '''
    Provides support for calls that are wrapped around another call.
    '''
    
    def __init__(self, call):
        '''
        Construct the with call support.
        
        @param call: Callable
            The call that is used by this Call in order to resolve.
        '''
        self.call = call
    
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
    
class WithType:
    '''
    Provides support for calls that have a type.
    '''
    
    def __init__(self, type):
        '''
        Construct the type support.
        
        @param type: class|None
            The type(class) of the value.
        '''
        assert type is None or isclass(type), 'Invalid type %s' % type
        self._type = type
        
    def validate(self, value):
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

# --------------------------------------------------------------------

class CallEvent(Callable, WithCall, WithListeners):
    '''
    Provides the event call.
    @see: Callable, WithCall, WithType, WithListeners
    '''
    
    def __init__(self, call):
        '''
        Construct the event call.
        @see: WithCall.__init__
        @see: WithListeners.__init__
        '''
        WithCall.__init__(self, call)
        WithListeners.__init__(self)
        self._processed = False

    def __call__(self):
        '''
        Provides the call for the source.
        '''
        if self._processed: raise SetupError('The event call cannot be dispatched twice')
        self._processed = True
        
        for listener in self._listenersBefore: listener()
        ret = self.call()
        if ret is not None: raise SetupError('The event call cannot return any value')
        for listener in self._listenersAfter: listener()
 
class CallEntity(Callable, WithCall, WithType, WithListeners):
    '''
    Call that resolves an entity setup.
    @see: Callable, WithCall, WithType, WithListeners
    '''
    
    def __init__(self, call, type=None):
        '''
        Construct the entity call.
        @see: WithCall.__init__
        @see: WithType.__init__
        @see: WithListeners.__init__
        '''
        WithCall.__init__(self, call)
        WithType.__init__(self, type)
        WithListeners.__init__(self)
        
        self._hasValue = False
        self._interceptors = []
    
    def addInterceptor(self, interceptor):
        '''
        Adds a value interceptor. A value interceptor is a Callable object that takes as an argument the entity value
        and returns the value for the entity.
        
        @param interceptor: Callable
            The interceptor.
        '''
        assert isinstance(interceptor, Callable), 'Invalid interceptor %s' % interceptor
        self._interceptors.append(interceptor)
    
    def __call__(self):
        '''
        Provides the call for the entity.
        '''
        if not self._hasValue:
            ret = self.call()
        
            if isgenerator(ret): value, generator = next(ret), ret
            else: value, generator = ret, None
            
            assert log.debug('Processed entity %s', value) or True
            v = self.validate(value)
            for inter in self._interceptors: v = inter(v)
            
            self._hasValue = True
            self._value = v
            
            for listener in self._listenersBefore: listener()
            
            if generator:
                try: next(generator)
                except StopIteration: pass
            
            Initializer.initialize(value)
    
            for listener in self._listenersAfter: listener()
            
            assert log.debug('Finalized entity %s', value) or True
        return self._value

class CallDeliverValue(Callable, WithType, WithListeners):
    '''
    Call that delivers a value.
    @see: Callable, WithType, WithListeners
    '''
    
    def __init__(self, value, type=None):
        '''
        Construct the configuration call.
        @see: WithType.__init__
        @see: WithListeners.__init__
        '''
        WithType.__init__(self, type)
        WithListeners.__init__(self)
        self._value = self.validate(value)
        self._processed = False
        
    def __call__(self):
        '''
        Provides the call for the entity.
        '''
        if not self._processed:
            self._processed = True
            for listener in chain(self._listenersBefore, self._listenersAfter): listener()
        return self._value
    
class CallDeliverError(Callable, WithListeners):
    '''
    Call that delivers an exception.
    @see: Callable, WithListeners
    '''
    
    def __init__(self, error):
        '''
        Construct the configuration call.
        @see: WithListeners.__init__
        
        @param error: Exception
            The exception to be raised.
        '''
        assert isinstance(error, Exception), 'Invalid error %s' % error
        WithListeners.__init__(self)
        self._error = error
        
    def __call__(self):
        '''
        Provides the call for the entity.
        '''
        for listener in chain(self._listenersBefore, self._listenersAfter): listener()
        raise self._error

# --------------------------------------------------------------------

class CreateEntity(Callable):
    '''
    Callable class that provides the entity creation based on the provided class.
    '''
    
    def __init__(self, clazz):
        '''
        Create the entity creator.
        
        @param clazz: class
            The class to create the entity based on.
        '''
        assert isclass(clazz), 'Invalid class %s' % clazz
        self._class = clazz
    
    def __call__(self):
        '''
        Provide the entity creation
        '''
        return self._class()

# --------------------------------------------------------------------

class Assembly:
    '''
    Provides the assembly data.
    '''
    
    current = []
    # The current assemblies.
    
    @classmethod
    def process(cls, name):
        '''
        Process the specified name into the current active context.
        
        @param name: string
            The name to be processed.
        '''
        if not cls.current: raise SetupError('There is no active assembly to process on')
        ass = cls.current[-1]
        assert isinstance(ass, Assembly), 'Invalid assembly %s' % ass
        return ass.processForName(name)
    
    def __init__(self, configExtern):
        '''
        Construct the assembly.
        
        @param configExtern: dictionary{string, object}
            The external configurations values to be used in the context.
        @ivar configUsed: set{string}
            A set containing the used configurations names from the external configurations.
        @ivar configurations: dictionary[string, Config]
            A dictionary of the assembly configurations, the key is the configuration name and the value is a
            Config object.
        @ivar callsByName: dictionary{string, Callable}
            A dictionary containing as a key the name of the call to be resolved and as a value the Callable that will
            resolve the name. The Callable will not take any argument.
        @ivar callsByType: dictionary{string, list[Callable]}
            A dictionary containing as a key the type provided by the calls and as a value a list of calls that provide
            that type.
        @ivar callsStart: list[Callable]
            A list of Callable that are used as IoC start calls.
        '''
        assert isinstance(configExtern, dict), 'Invalid external configurations %s' % configExtern
        self.configExtern = configExtern
        self.configUsed = set()
        self.configurations = {}
        self.callsByName = {}
        self.callsByType = {}
        self.callsStart = []
        
    def trimmedConfigurations(self):
        '''
        Provides a configurations dictionary that has the configuration names trimmed.
        
        @return:  dictionary[string, Config]
            A dictionary of the assembly configurations, the key is the configuration name and the value is a
            Config object.
        ''' 
        def expand(name, sub):
            ''' Used for expanding configuration names'''
            if sub: root = name[:-len(sub)]
            else: root = name
            if not root: return name
            if root[-1] == '.': root = root[:-1]
            k = root.rfind('.')
            if k < 0: return name
            if sub: return root[k + 1:] + '.' + sub
            return root[k + 1:]
            
        configs = {}
        for name, config in self.configurations.items():
            sname = expand(name, '')
            other = configs.pop(sname, None)
            while other:
                assert isinstance(other, Config)
                configs[expand(other.name, sname)] = other
                sname = expand(name, sname)
                other = configs.pop(sname, None)
            configs[sname] = config
        return configs
            
    def processForName(self, name):
        '''
        Process the specified name into this assembly.
        
        @param name: string
            The name to be processed.
        '''
        assert isinstance(name, str), 'Invalid name %s' % name
        call = self.callsByName.get(name)
        if not call: raise SetupError('No IoC resource for name %r' % name)
        if not isinstance(call, Callable): raise SetupError('Invalid call %s for name %r' % (call, name))
        return call()
    
    def processStart(self):
        '''
        Starts the assembly, basically call all setup functions that have been decorated with start.
        '''
        if self.callsStart:
            unused = set(self.configExtern)
            unused = unused.difference(self.configUsed)
            if unused: log.warn('Unknown configurations: %r', ', '.join(unused))
            
            self.current.append(self)
            try:     
                for call in self.callsStart: call()
            finally: self.current.pop()
        else: log.error('No IoC start calls to start the setup')

class Context:
    '''
    Provides the context of the setup functions and setup calls.
    '''
    
    def __init__(self):
        '''
        Construct the context.
        '''
        self._setups = []
        
    def addSetup(self, setup):
        '''
        Adds a new setup to the context.
        
        @param setup: Setup
            The setup to add to the context.
        '''
        assert isinstance(setup, Setup), 'Invalid setup %s' % setup
        self._setups.append(setup)

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
        
    def assemble(self, configurations=None):
        '''
        Creates and assembly based on this context.
        
        @param configurations: dictionary{string, object}
            The external configurations values to be used for the assembly.
        '''
        assembly = Assembly(configurations or {})
        
        setups = sorted(self._setups, key=lambda setup: setup.priority)
        for setup in setups:
            assert isinstance(setup, Setup), 'Invalid setup %s' % setup
            setup.index(assembly)
            
        self._indexing = False
        for setup in setups: setup.assemble(assembly)
        
        return assembly
 
