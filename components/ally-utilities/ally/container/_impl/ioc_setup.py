'''
Created on Jan 12, 2012

@package: ally utilities
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the setup implementations for the IoC module.
'''

from ..config import Config
from .entity_handler import Initializer
from collections import deque
from functools import partial
from inspect import isclass, isfunction, getfullargspec, ismodule, isgenerator, \
    getdoc
from itertools import chain
from numbers import Number
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

def setupFirstOf(register, *classes):
    '''
    Provides the first setup in the register that is of the provided class.
    
    @param register: dictionary{string, object}
        The register to retrieve the setup from.
    @param classes: arguments[class]
        The setup class(es) to find for.
    @return: Setup|None
        The first found setup or None.
    '''
    assert isinstance(register, dict), 'Invalid register %s' % register
    setups = register.get('__ally_setups__')
    if setups is not None:
        for setup in setups:
            if isinstance(setup, classes): return setup
    return None

def setupsOf(register, *classes):
    '''
    Provides the setups in the register that are of the provided class.
    
    @param register: dictionary{string, object}
        The register to retrieve the setups from.
    @param classes: arguments[class]
        The setup class(es) to find for.
    @return: list[Setup]
        The setups list.
    '''
    assert isinstance(register, dict), 'Invalid register %s' % register
    setups = register.get('__ally_setups__')
    if setups is not None:
        return [setup for setup in setups if isinstance(setup, classes)]
    return []

def register(setup, register):
    '''
    Register the setup function into the calling module.
    
    @param setup: Setup
        The setup to register into the calling module.
    @param register: dictionary{string, object}
        The register to place the setup in.
    @return: Setup
        The provided setup entity.
    '''
    assert isinstance(register, dict), 'Invalid register %s' % register
    setups = register.get('__ally_setups__')
    if setups is None: setups = register['__ally_setups__'] = []
    setups.append(setup)
    return setup

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

    def addBefore(self, listener, auto):
        '''
        Adds a before listener.
        
        @param listener: Callable
            A callable that takes no parameters that will be invoked before the call is processed.
        @param auto: boolean
            Flag indicating that the call of the listener should be auto managed by the called.
        '''
        assert callable(listener), 'Invalid listener %s' % listener
        assert isinstance(auto, bool), 'Invalid auto flag %s' % auto
        self._listenersBefore.append((listener, auto))

    def addAfter(self, listener, auto):
        '''
        Adds an after listener.
        
        @param listener: Callable
            A callable that takes no parameters that will be invoked after the call is processed.
        @param auto: boolean
            Flag indicating that the call of the listener should be auto managed by the called.
        '''
        assert callable(listener), 'Invalid listener %s' % listener
        assert isinstance(auto, bool), 'Invalid auto flag %s' % auto
        self._listenersAfter.append((listener, auto))

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
        assert callable(call), 'Invalid callable %s' % call
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

    type = property(lambda self: self._type, doc=
'''
@type type: class
    The type.
''')

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

class Setup:
    '''
    The setup entity. This class provides the means of indexing setup Callable objects.
    '''

    priority_index = 1
    # Provides the indexing priority for the setup.
    priority_assemble = 1
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

class SetupFunction(Setup):
    '''
    A setup indexer based on a function.
    '''

    def __init__(self, function, name=None, group=None):
        '''
        Constructs the setup call for the provided function.
        
        @param function: function|Callable
            The function of the setup call, lambda functions or Callable are allowed only if the name is provided.
        @param name: string|None
            The name of this setup, if not specified it will be extracted from the provided function.
        @param group: string|None
            The group of this setup, if not specified it will be extracted from the provided function.
        '''
        assert not group or isinstance(group, str), 'Invalid group %s' % group
        if name:
            assert callable(function), 'Invalid callable function %s' % function
            assert isinstance(name, str), 'Invalid name %s' % name
            self.name = name
            self.group = group
        else:
            assert isfunction(function), 'Invalid function %s' % function
            assert function.__name__ != '<lambda>', 'Lambda functions cannot be used %s' % function
            if group: self.group = group
            else: self.group = function.__module__
            self.name = self.group + '.' + function.__name__
            if __debug__:
                fnArgs = getfullargspec(function)
                assert not (fnArgs.args or fnArgs.varargs or fnArgs.varkw), \
                'The setup function %r cannot have any type of arguments' % self.name
        self._function = function

    def __call__(self):
        '''
        Provides the actual setup of the call.
        '''
        return Assembly.process(self.name)

class SetupSource(SetupFunction, WithType):
    '''
    Provides the setup for retrieving a value based on a setup function.
    '''

    def __init__(self, function, type=None, **keyargs):
        '''
        @see: SetupFunction.__init__
        
        @param type: class|None
            The type(class) of the value that is being delivered by this source.
        '''
        SetupFunction.__init__(self, function, **keyargs)
        WithType.__init__(self, type)

class SetupEntity(SetupSource):
    '''
    Provides the entity setup.
    '''

    def __init__(self, function, **keyargs):
        '''
        @see: SetupSource.__init__
        '''
        SetupSource.__init__(self, function, **keyargs)

    def index(self, assembly):
        '''
        @see: Setup.index
        '''
        assert isinstance(assembly, Assembly), 'Invalid assembly %s' % assembly
        if self.name in assembly.calls:
            raise SetupError('There is already a setup call for name %r' % self.name)
        assembly.calls[self.name] = CallEntity(assembly, self.name, self._function, self._type)

class SetupConfig(SetupSource):
    '''
    Provides the configuration setup.
    '''

    priority_assemble = 3

    def __init__(self, function, **keyargs):
        '''
        @see: SetupSource.__init__
        '''
        SetupSource.__init__(self, function, **keyargs)
        self._type = normalizeConfigType(self._type) if self._type else None
        self.documentation = getdoc(function)

    def index(self, assembly):
        '''
        @see: Setup.index
        '''
        assert isinstance(assembly, Assembly), 'Invalid assembly %s' % assembly
        if self.name in assembly.calls:
            raise SetupError('There is already a setup call for name %r' % self.name)

        assembly.calls[self.name] = CallConfig(assembly, self.name, self._type)

    def assemble(self, assembly):
        '''
        @see: Setup.assemble
        Checks for aliases to replace.
        '''
        assert isinstance(assembly, Assembly), 'Invalid assembly %s' % assembly
        config = assembly.calls.get(self.name)
        assert isinstance(config, CallConfig), 'Invalid call configuration %s' % config

        for name, val in assembly.configExtern.items():
            if name == self.name or self.name.endswith('.' + name):
                if name in assembly.configUsed:
                    raise SetupError('The configuration %r is already in use and the configuration "%s" cannot use it '
                                     'again, provide a more detailed path for the configuration (ex: "ally_core.url" '
                                     'instead of "url")' % (name, self.name))
                assembly.configUsed.add(name)
                config.external, config.value = True, val

        if not config.hasValue:
            try: config.value = self._function()
            except ConfigError as e: config.value = e

        cfg = assembly.configurations.get(self.name)
        if not cfg:
            cfg = Config(self.name, config.value, self.group, self.documentation)
            assembly.configurations[self.name] = cfg
        else:
            assert isinstance(cfg, Config), 'Invalid configuration %s' % cfg
            cfg.value = config.value

class SetupReplaceConfig(SetupFunction):
    '''
    Provides the setup for replacing a configuration setup function.
    '''

    priority_assemble = 2

    def __init__(self, function, target, **keyargs):
        '''
        @see: SetupFunction.__init__
        
        @param target: SetupFunction
            The setup name to be replaced.
        '''
        assert isinstance(target, SetupConfig), 'Invalid target %s' % target
        SetupFunction.__init__(self, function, name=target.name, group=target.group, ** keyargs)
        documentation = getdoc(function)
        if documentation:
            if target.documentation: target.documentation += '\n%s' % documentation
            else: target.documentation = documentation
        self.target = target

    def assemble(self, assembly):
        '''
        @see: Setup.assemble
        '''
        assert isinstance(assembly, Assembly), 'Invalid assembly %s' % assembly
        if self.name not in assembly.calls:
            raise SetupError('There is no setup configuration call for name %r to be replaced' % self.name)
        config = assembly.calls[self.name]
        assert isinstance(config, CallConfig), 'Invalid call configuration %s' % config
        try: config.value = self._function()
        except ConfigError as e: config.value = e

        assembly.configurations[self.name] = Config(self.name, config.value, self.group, self.target.documentation)

class SetupReplace(SetupFunction):
    '''
    Provides the setup for replacing an entity or event setup function.
    '''

    priority_assemble = 2

    def __init__(self, function, target, **keyargs):
        '''
        @see: SetupFunction.__init__
        
        @param target: SetupSource
            The setup to be replaced.
        '''
        assert isinstance(target, SetupSource), 'Invalid target %s' % target
        SetupFunction.__init__(self, function, name=target.name, group=target.group, ** keyargs)

    def assemble(self, assembly):
        '''
        @see: Setup.assemble
        '''
        assert isinstance(assembly, Assembly), 'Invalid assembly %s' % assembly
        if self.name not in assembly.calls:
            raise SetupError('There is no setup call for name %r to be replaced' % self.name)
        call = assembly.calls[self.name]
        if not isinstance(call, WithCall):
            raise SetupError('Cannot replace call for name %r' % self.name)
        assert isinstance(call, WithCall)
        call.call = self._function

class SetupEvent(SetupFunction):
    '''
    Provides the setup event function.
    '''

    priority_assemble = 4

    BEFORE = 'before'
    AFTER = 'after'
    EVENTS = [BEFORE, AFTER]

    def __init__(self, function, target, event, auto, **keyargs):
        '''
        @see: SetupFunction.__init__
        
        @param target: string|tuple(string)
            The target name of the event call.
        @param event: string
            On of the defined EVENTS.
        @param auto: boolean
            Flag indicating that the event call should be auto managed by the container.
        '''
        SetupFunction.__init__(self, function, **keyargs)
        if isinstance(target, str): targets = (target,)
        else: targets = target
        assert isinstance(targets, tuple), 'Invalid targets %s' % targets
        if __debug__:
            for target in targets: assert isinstance(target, str), 'Invalid target %s' % target
        assert event in self.EVENTS, 'Invalid event %s' % event
        assert isinstance(auto, bool), 'Invalid auto flag %s' % auto
        self._targets = targets
        self._event = event
        self._auto = auto

    def index(self, assembly):
        '''
        @see: Setup.index
        '''
        assert isinstance(assembly, Assembly), 'Invalid assembly %s' % assembly
        if self.name in assembly.calls:
            raise SetupError('There is already a setup call for name %r' % self.name)
        if self._event == self.BEFORE or len(self._targets) == 1:
            assembly.calls[self.name] = CallEvent(assembly, self.name, self._function)
        else: assembly.calls[self.name] = CallEventOnCount(assembly, self.name, self._function, len(self._targets))

    def assemble(self, assembly):
        '''
        @see: Setup.assemble
        '''
        assert isinstance(assembly, Assembly), 'Invalid assembly %s' % assembly
        for target in self._targets:
            if target not in assembly.calls:
                raise SetupError('There is no setup call for target \'%s\' to add the event on' % target)
            call = assembly.calls[target]
            if not isinstance(call, WithListeners):
                raise SetupError('Cannot find any listener support for target %r to add the event' % target)
            assert isinstance(call, WithListeners)
        if self._event == self.BEFORE: call.addBefore(partial(assembly.processForName, self.name), self._auto)
        elif self._event == self.AFTER: call.addAfter(partial(assembly.processForName, self.name), self._auto)

    def __call__(self):
        '''
        Provides the actual setup of the call.
        '''
        raise SetupError('Cannot invoke the event setup %r directly' % self.name)

class SetupStart(SetupFunction):
    '''
    Provides the start function.
    '''

    def __init__(self, function, **keyargs):
        '''
        @see: SetupFunction.__init__
        '''
        SetupFunction.__init__(self, function, **keyargs)

    def index(self, assembly):
        '''
        @see: Setup.index
        '''
        assert isinstance(assembly, Assembly), 'Invalid assembly %s' % assembly
        if self.name in assembly.calls:
            raise SetupError('There is already a setup call for name %r' % self.name)
        assembly.calls[self.name] = CallEvent(assembly, self.name, self._function)

    def assemble(self, assembly):
        '''
        @see: Setup.assemble
        '''
        assert isinstance(assembly, Assembly), 'Invalid assembly %s' % assembly
        assembly.callsStart.append(partial(assembly.processForName, self.name))

# --------------------------------------------------------------------

class CallEvent(WithCall, WithListeners):
    '''
    Provides the event call.
    @see: Callable, WithCall, WithType, WithListeners
    '''

    def __init__(self, assembly, name, call):
        '''
        Construct the event call.
        
        @param assembly: Assembly
            The assembly to which this call belongs.
        @param name: string
            The event name.
            
        @see: WithCall.__init__
        @see: WithListeners.__init__
        '''
        assert isinstance(assembly, Assembly), 'Invalid assembly %s' % assembly
        assert isinstance(name, str), 'Invalid name %s' % name
        WithCall.__init__(self, call)
        WithListeners.__init__(self)

        self._assembly = assembly
        self.name = name
        self._processed = False

    def __call__(self):
        '''
        Provides the call for the source.
        '''
        if self._processed: return
        self._processed = True
        self._assembly.called.add(self.name)

        for listener, _auto in self._listenersBefore: listener()
        ret = self.call()
        if ret is not None: raise SetupError('The event call %r cannot return any value' % self.name)
        for listener, _auto in self._listenersAfter: listener()
        
class CallEventOnCount(CallEvent):
    '''
    Event call that triggers only after being called count times.
    @see: CallEvent
    '''

    def __init__(self, assembly, name, call, count):
        '''
        Construct the call on count event.
        @see: CallEvent.__init__
        
        @param count: integer
            The number of calls that the event needs to be called in order to actually trigger.
        '''
        assert isinstance(count, int) and count > 0, 'Invalid count %s' % count
        super().__init__(assembly, name, call)
        
        self._count = count

    def __call__(self):
        '''
        Provides the call for the source.
        '''
        if self._count > 0: self._count -= 1
        if self._count <= 0: super().__call__()

class CallEntity(WithCall, WithType, WithListeners):
    '''
    Call that resolves an entity setup.
    @see: Callable, WithCall, WithType, WithListeners
    '''

    def __init__(self, assembly, name, call, type=None):
        '''
        Construct the entity call.
        
        @param assembly: Assembly
            The assembly to which this call belongs.
        @param name: string
            The entity name.
        
        @see: WithCall.__init__
        @see: WithType.__init__
        @see: WithListeners.__init__
        '''
        assert isinstance(assembly, Assembly), 'Invalid assembly %s' % assembly
        assert isinstance(name, str), 'Invalid name %s' % name
        WithCall.__init__(self, call)
        WithType.__init__(self, type)
        WithListeners.__init__(self)

        self.marks = []

        self._assembly = assembly
        self.name = name
        self._hasValue = False
        self._processing = False
        self._interceptors = []

    def addInterceptor(self, interceptor):
        '''
        Adds a value interceptor. A value interceptor is a Callable object that takes as the first argument the entity
        value and as the second value the follow up Callable of the value and returns the value for the entity and the
        new follow up.
        
        @param interceptor: Callable(object, Callable)
            The interceptor.
        '''
        assert callable(interceptor), 'Invalid interceptor %s' % interceptor
        self._interceptors.append(interceptor)

    def __call__(self):
        '''
        Provides the call for the entity.
        '''
        if not self._hasValue:
            if self._processing:
                raise SetupError('Cyclic dependency detected for %r, try using yield' % self.name)
            self._processing = True
            self._assembly.called.add(self.name)

            ret = self.call()

            if isgenerator(ret): value, followUp = next(ret), partial(next, ret, None)
            else: value, followUp = ret, None

            if value is not None:
                valueId, value_calls = id(value), self._assembly.value_calls
                calls = value_calls.get(valueId)
                if calls is None: value_calls[valueId] = calls = deque([self])
                else: calls.append(self)
            else: valueId = None

            assert log.debug('Processed entity %r with value %s', self.name, value) or True
            v = self.validate(value)
            for inter in self._interceptors:
                v, followUp = inter(v, followUp)

            self._hasValue = True
            self._value = v

            for listener, _auto in self._listenersBefore: listener()

            if followUp: followUp()

            if valueId:
                calls.pop()
                if len(calls) == 0:
                    Initializer.initialize(value)
                    del value_calls[valueId]

            for listener, _auto in self._listenersAfter: listener()

            assert log.debug('Finalized %r with value %s', self.name, value) or True
        return self._value

class CallConfig(WithType, WithListeners):
    '''
    Call that delivers a value.
    @see: Callable, WithType, WithListeners
    '''

    def __init__(self, assembly, name, type=None):
        '''
        Construct the configuration call.
        
        @param assembly: Assembly
            The assembly to which this call belongs.
        @param name: string
            The configuration name.
        @param value: object
            The value to deliver.
            
        @see: WithType.__init__
        @see: WithListeners.__init__
        '''
        WithType.__init__(self, type)
        WithListeners.__init__(self)

        self._assembly = assembly
        self.name = name
        self.external = False
        self._hasValue = False
        self._processed = False

    def setValue(self, value):
        '''
        Sets the value to deliver.
        
        @param value: object
            The value to deliver.
        '''
        if isinstance(value, Exception):
            self._value = value
        else:
            self._value = self.validate(value)
            self._hasValue = True

    hasValue = property(lambda self: self._hasValue, doc=
'''
@type hasValue: boolean
    True if the configuration has a value.
''')
    value = property(lambda self: self._value, setValue, doc=
'''
@type value: object
    The value to deliver.
''')

    def __call__(self):
        '''
        Provides the call for the entity.
        '''
        if not self._processed:
            self._processed = True
            self._assembly.called.add(self.name)
            for listener, auto in chain(self._listenersBefore, self._listenersAfter):
                if auto:
                    if not self.external: listener() 
                    # We only call the listeners if the configuration was not provided externally
                else: listener()
        if isinstance(self._value, Exception): raise self._value
        if not self._hasValue: raise ConfigError('No value for configuration %s' % self.name)
        return self._value

# --------------------------------------------------------------------

class Assembly:
    '''
    Provides the assembly data.
    '''

    stack = []
    # The current assemblies stack.

    @classmethod
    def current(cls):
        '''
        Provides the current assembly.
        
        @return: Assembly
            The current assembly.
        @raise SetupError: if there is no current assembly.
        '''
        if not cls.stack: raise SetupError('There is no active assembly to process on')
        return cls.stack[-1]

    @classmethod
    def process(cls, name):
        '''
        Process the specified name into the current active context.
        
        @param name: string
            The name to be processed.
        '''
        ass = cls.current()
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
        @ivar calls: dictionary{string, Callable}
            A dictionary containing as a key the name of the call to be resolved and as a value the Callable that will
            resolve the name. The Callable will not take any argument.
        @ivar callsStart: deque[Callable]
            A list of Callable that are used as IoC start calls.
        @ivar callsFinalize: deque[Callable]
            A list of Callable that are used as IoC finalize calls.
        @ivar called: set[string]
            A set of the called calls in this assembly.
        @ivar started: boolean
            Flag indicating if the assembly is started.
            
        @ivar _processing: deque(string)
            Used internally for tracking the processing chain.
        '''
        assert isinstance(configExtern, dict), 'Invalid external configurations %s' % configExtern
        self.configExtern = configExtern
        self.configUsed = set()
        self.configurations = {}
        self.calls = {}
        self.value_calls = {}
        self.callsStart = deque()
        self.called = set()
        self.started = False

        self._processing = deque()

    def trimmedConfigurations(self):
        '''
        Provides a configurations dictionary that has the configuration names trimmed.
        
        @return:  dictionary[string, Config]
            A dictionary of the assembly configurations, the key is the configuration name and the value 
            is a Config object.
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
            assert isinstance(config, Config), 'Invalid configuration %s' % config
            sname = name[len(config.group) + 1:]
            other = configs.pop(sname, None)
            while other:
                assert isinstance(other, Config)
                configs[expand(other.name, sname)] = other
                sname = expand(name, sname)
                other = configs.pop(sname, None)
            configs[sname] = config
        return configs
    
    def fetchForName(self, name):
        '''
        Fetch the call with the specified name.
        
        @param name: string
            The name of the call to be fetched.
        '''
        assert isinstance(name, str), 'Invalid name %s' % name
        call = self.calls.get(name)
        if not call: raise SetupError('No IoC resource for name %r' % name)
        if not callable(call): raise SetupError('Invalid call %s for name %r' % (call, name))
        return call

    def processForName(self, name):
        '''
        Process the specified name into this assembly.
        
        @param name: string
            The name to be processed.
        '''
        assert isinstance(name, str), 'Invalid name %s' % name
        self._processing.append(name)
        try: value = self.fetchForName(name)()
        except SetupError: raise
        except: raise SetupError('Exception occurred for %r in processing chain %r' % 
                                 (name, ', '.join(self._processing)))
        self._processing.pop()
        return value

    def processForPartialName(self, name):
        '''
        Process the specified partial name into this assembly.
        
        @param name: string
            The partial name to be processed.
        '''
        assert isinstance(name, str), 'Invalid name %s' % name
        if not name.startswith('.'): pname = '.' + name
        else: pname = name
        names = [fname for fname in self.calls if fname == name or fname.endswith(pname)]

        if not names: raise SetupError('No IoC resource for name %r' % name)
        if len(names) > 1: raise SetupError('To many IoC resource for name %r' % name)
        return self.processForName(names[0])

    def processStart(self):
        '''
        Starts the assembly, basically call all setup functions that have been decorated with start.
        '''
        if self.callsStart:
            unused = set(self.configExtern)
            unused = unused.difference(self.configUsed)
            if unused: log.info('Unknown configurations: %r', ', '.join(unused))

            for call in self.callsStart: call()
            self.started = True
        else: log.error('No IoC start calls to start the setup')

class Context:
    '''
    Provides the context of the setup functions and setup calls.
    '''

    def __init__(self):
        '''
        Construct the context.
        '''
        self._modules = []

    def addSetupModule(self, module):
        '''
        Adds a new setup module to the context.
        
        @param module: module
            The setup module.
        '''
        assert ismodule(module), 'Invalid module setup %s' % module
        try: module.__ally_setups__
        except AttributeError: log.info('No setup found in %s', module)
        else:
            self._modules.append(module)
            self._modules.sort(key=lambda module: module.__name__)

    def assemble(self, configurations=None):
        '''
        Creates and assembly based on this context.
        
        @param configurations: dictionary{string, object}
            The external configurations values to be used for the assembly.
        '''
        assembly = Assembly(configurations or {})
        
        setups = deque()
        for module in self._modules: setups.extend(module.__ally_setups__) 
        
        for setup in sorted(setups, key=lambda setup: setup.priority_index):
            assert isinstance(setup, Setup), 'Invalid setup %s' % setup
            setup.index(assembly)

        for setup in sorted(setups, key=lambda setup: setup.priority_assemble):
            setup.assemble(assembly)

        return assembly

# --------------------------------------------------------------------

def normalizeConfigType(clazz):
    '''
    Checks and normalizes the provided configuration type.
    
    @param clazz: class
        The configuration type to normalize.
    @return: class
        The normalized type.
    '''
    if clazz:
        assert isclass(clazz), 'Invalid class %s' % clazz
        if clazz == float: return Number
    return clazz
