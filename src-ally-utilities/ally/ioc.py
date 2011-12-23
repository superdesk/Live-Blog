'''
Created on Sep 23, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the IoC (Inversion of Control or dependency injection) services. Attention the IoC should always be used from a
single thread at one time.
'''

from .util import Attribute
from _abcoll import Callable
from functools import partial
from inspect import isclass, isfunction, getfullargspec, ismodule, isgenerator
import logging
import importlib
from ally.aop import AOPModules

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

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

def entity(function, type=None, doc=None):
    '''
    Used to wrap entity setup functions, also can be used as a decorator for entity functions.
    
    @param function: function
        The setup function.
    @param type: class|None
        The type of the entity provided by the function, if not provided the function will be searched for the return
        annotation and consider that as the type, if no annotation is present than this setup function is not known by
        return type this will exclude this setup function from entities searched by type.
    @param doc: string|None
        A description for the setup function, if not provided than the function doc will be used.
    @return: Callable
        The wrapped callable object that will manage the setup function.
    '''
    return CallEntity(function)
    

def config(function, type=None, doc=None):
    '''
    Used to wrap configuration setup functions, also can be used as a decorator for configurations functions.
    
    @param function: function
        The setup function.
    @param type: class|None
        The type of the configuration provided by the function, if not provided the function will be searched for the 
        return annotation and consider that as the type, if no annotation is present than this setup function is not 
        known by return type. This creates problems whenever the configuration will be set externally because no
        validation or transformation is not possible.
    @param doc: string|None
        A description for the setup function, if not provided than the function doc will be used.
    @return: Callable
        The wrapped callable object that will manage the setup function.
    '''
    return CallConfig(function)

def before(call):
    '''
    '''
    #TODO: comment
    def beforeDecorator(call, function):
        assert isinstance(call, Call), 'Invalid call %s' % call
        event = CallEvent(function)
        call._listenersBefore.append(event.dispatch)
        return event
    
    assert isinstance(call, Call), 'Invalid call %s' % call
    return partial(beforeDecorator, call)

def after(call):
    '''
    To be used only as a decorator for functions that need to be called after the provided setup function has finalized.
    '''
    #TODO: comment
    def afterDecorator(call, function):
        assert isinstance(call, Call), 'Invalid call %s' % call
        event = CallEvent(function)
        call._listenersAfter.append(event.dispatch)
        return event
    
    assert isinstance(call, Call), 'Invalid call %s' % call
    return partial(afterDecorator, call)
    
def replace(call):
    '''
    '''
    #TODO: comment
    def replaceDecorator(call, function): return CallReplacer(function, call)
    
    assert isinstance(call, Call), 'Invalid call %s' % call
    assert not isinstance(call, CallReplacer), 'Cannot replace a replacer %s' % call
    return partial(replaceDecorator, call)
    
def start(function):
    '''
    '''
    #TODO: comment
    return CallStart(function)

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
    context.start()

# --------------------------------------------------------------------

ATTR_INITIALIZED = Attribute(__name__, 'initialized', bool)
# Provides the attribute for the initialized flag.
ATTR_ARGUMENTS = Attribute(__name__, 'arguments')
# Provides the attribute for the arguments for initialization.

class Initializer(Callable):
    '''
    Class used as the initializer for the entities classes.
    '''
    
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
    
    @staticmethod
    def initialize(entity):
        '''
        Initialize the provided entity.
        '''
        assert entity is not None, 'Need to provide an entity to be initialized'
        initializer = Initializer.initializerFor(entity)
        if initializer:
            assert isinstance(initializer, Initializer)
            if entity.__class__ == initializer._entityClazz:
                args, keyargs = ATTR_ARGUMENTS.getOwn(entity)
                ATTR_ARGUMENTS.deleteOwn(entity)
                ATTR_INITIALIZED.set(entity, True)
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
        if ATTR_INITIALIZED.get(entity, False):
            return self._entityInit(entity, *args, **keyargs)
        assert not ATTR_ARGUMENTS.hasOwn(entity), 'Cannot initialize twice the entity %s' % entity
        ATTR_ARGUMENTS.setOwn(entity, (args, keyargs))

    def __get__(self, entity, owner=None):
        '''
        @see: http://docs.python.org/reference/datamodel.html
        '''
        if entity is not None: return partial(self.__call__, entity)
        return self.__call__

# --------------------------------------------------------------------

class SetupError(Exception):
    '''
    Exception thrown when there is a setup problem.
    '''

class Context:
    '''
    Provides the context of the setup functions and setup data.
    '''
    
    def __init__(self):
        '''
        Construct the context.
        '''
        self._calls = {}
        self._data = {}
    
    def addSetupModule(self, module):
        '''
        Adds a new setup module to the context.
        
        @param module: module
            The setup module.
        ''' 
        assert ismodule(module), 'Invalid module setup %s' % module
        path, calls = module.__name__ + '.', self._calls
        for call in module.__dict__.values():
            if isinstance(call, Call):
                assert isinstance(call, Call)
                if call._name.startswith(path):
                    assert call._name not in calls, 'There is already a call %s registered' % call._name
                    calls[call._name] = call
                    
    def start(self):
        '''
        Starts the context, basically call all setup functions that have been decorated with start.
        '''
        _CONTEXTS.append(self)
        try:
            for call in self._calls.values():
                if isinstance(call, CallStart):
                    assert isinstance(call, CallStart)
                    call.dispatch()
        finally: _CONTEXTS.pop()

_CONTEXTS = []
# The current setup contexts

class Call(Callable):
    '''
    Provides the base class of calls.
    '''
    
    def __init__(self, function):
        '''
        Constructs the call for the provided function.
        
        @param function: function
            The function of the call.
        '''
        assert isfunction(function), 'Invalid function %s' % function
        assert function.__name__ != '<lambda>', 'Lambda functions cannot be used %s' % function
        self._call = function
        self._name = function.__module__ + '.' + function.__name__
        fnArgs = getfullargspec(function)
        if fnArgs.args or fnArgs.varargs or fnArgs.varkw:
            raise SetupError('The setup function %r cannot have any type of arguments' % self._name)
        self._listenersBefore = []
        self._listenersAfter = []

class CallSetup(Call):
    '''
    Provides the base class of setup calls.
    '''
    
    def __call__(self):
        '''
        Provides the actual setup of the call. Attention this method is only available if a _CONTEXT is available.
        '''
        ctx = _CONTEXTS[-1]
        if not ctx: raise SetupError('There is no context to setup') 
        assert isinstance(ctx, Context), 'Invalid context %s' % ctx
        if self._name not in ctx._calls:
            raise SetupError('The setup call %r is not registered with the active context' % self._name)
        
        if self._name in ctx._data: return ctx._data[self._name]
        ret = self._call()
        
        if isgenerator(ret): value, generator = next(ret), ret
        else: value, generator = ret, None
        
        assert log.debug('Processed %r for value %s', self._name, value) or True
        ctx._data[self._name] = value
        
        for listener in self._listenersBefore: listener()
        
        if generator:
            try: next(generator)
            except StopIteration: pass
        
        Initializer.initialize(value)
        
        for listener in self._listenersAfter: listener()
        
        assert log.debug('Finalized %r with value %s', self._name, value) or True
        return value
    
class CallEntity(CallSetup):
    '''
    Provides the call for entities.
    '''
    
class CallConfig(CallSetup):
    '''
    Provides the call for configurations.
    '''

class CallReplacer(Call):
    '''
    Provides the call for replacer.
    '''
    
    def __init__(self, function, replaced):
        '''
        @see: Call.__init__
        
        @param replaced: Call
            The replaced call.
        '''
        Call.__init__(self, function)
        assert isinstance(replaced, Call), 'Invalid replaced call %s' % replaced
        self._replaced = replaced
        replaced._call = self._call
        self._listenersBefore = replaced._listenersBefore
        self._listenersAfter = replaced._listenersAfter
    
    def __call__(self):
        '''
        @see: Callable.__call__
        '''
        return self._replaced()

class CallEvent(Call):
    '''
    Provides the base class of event calls.
    '''
        
    def dispatch(self):
        '''
        Provides the actual event call. Attention this method is only available if a _CONTEXT is available.
        '''
        ctx = _CONTEXTS[-1]
        if not ctx: raise SetupError('There is no context to setup') 
        assert isinstance(ctx, Context), 'Invalid context %s' % ctx
        if self._name not in ctx._calls:
            raise SetupError('The setup call %r is not registered with the active context' % self._name)
        if self._name in ctx._data:
            raise SetupError('The event call %r cannot be called twice' % self._name)
        
        ctx._data[self._name] = True
        
        for listener in self._listenersBefore: listener()
        self._call()
        for listener in self._listenersAfter: listener()
        assert log.debug('Dispatched event call %r', self._name) or True
        
    def __call__(self):
        '''
        @see: Callable.__call__
        '''
        raise SetupError('You cannot directly call the event setup %r' % self._name)

class CallStart(CallEvent):
    '''
    Provides the start event.
    '''
