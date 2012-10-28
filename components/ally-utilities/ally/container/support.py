'''
Created on Jan 12, 2012

@package: ally utilities
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides support functions for the container.
'''

from ..support.util_sys import callerLocals, callerGlobals
from ._impl.aop_container import AOPClasses, AOPResources
from ._impl.entity_handler import Wiring, WireConfig
from ._impl.ioc_setup import ConfigError, register, SetupConfig, setupsOf, \
    setupFirstOf, SetupStart
from ._impl.support_setup import SetupError, SetupEntityProxy, SetupEntityWire, \
    Assembly, CallEntity, SetupEntityCreate
from .aop import classesIn
from ally.container._impl.support_setup import SetupEntityListen, \
    SetupEntityListenAfterBinding
from copy import deepcopy
from functools import partial
from inspect import isclass, ismodule, getsource

# --------------------------------------------------------------------
# Functions available in setup modules.

def setup(type, name=None):
    '''
    Decorate a IMPL class with the info about required API class and optional a name
    
    @param type: class
        The type of the correspondent API.
    @param name: string
        The name associated to created IOC object
    '''
    assert isclass(type), 'Expected a class instead of %s ' % type
    if name: assert isinstance(name, str), 'Expected a string name instead of %s ' % name

    def decorator(clazz):
        setattr(clazz, '__ally_setup__', (type, name))
        return clazz

    return decorator

def createEntitySetup(*classes, formatter=lambda group, clazz, name: group + '.' + name if name else group + '.' + clazz.__name__,
                      module=None):
    '''
    For impl classes create the setup functions for the associated API classes. The name of the setup functions that will be generated
    are formed based on the provided formatter. To create a setup function a class from the impl classes has to inherit the api class.
    
    @param classes: arguments(string|class|AOPClasses)
        The classes to be considered the implementations for the APIs.
    @param formatter: Callable
        The formatter to use in creating the entity setup function name, the Callable will take three arguments, first is
        the group where the setup function is defined, the second is the class for wich the setup is created and the third 
        is optional and is the name of the created instance. 
    @param module: module|None
        If the setup module is not provided than the calling module will be considered.
    '''
    assert callable(formatter), 'Invalid formatter %s' % formatter
    if module:
        assert ismodule(module), 'Invalid setup module %s' % module
        registry = module.__dict__
        group = module.__name__
    else:
        registry = callerLocals()
        if '__name__' not in registry:
            raise SetupError('The create entity call needs to be made directly from the module')
        group = registry['__name__']

    wireClasses = []
    for clazz in _classes(classes):
        if not hasattr(clazz, '__ally_setup__'): continue
        setupTuple = clazz.__ally_setup__
        if not setupTuple: continue
        apiClass, name = setupTuple
        assert issubclass(clazz, apiClass), 'The impl class % do not extend the declared API class %s' % (clazz, apiClass)
        wireClasses.append(clazz)
        register(SetupEntityCreate(clazz, apiClass, name=formatter(group, apiClass, name), group=group), registry)

    wireEntities(*wireClasses, module=module)

def wireEntities(*classes, module=None):
    '''
    Creates entity wiring setups for the provided classes. The wiring setups consists of configurations found in the
    provided classes that will be published in the setup module.
    
    @param classes: arguments(string|class|AOPClasses)
        The classes to be wired.
    @param module: module|None
        If the setup module is not provided than the calling module will be considered.
    '''
    def processConfig(clazz, wconfig):
        assert isclass(clazz), 'Invalid class %s' % clazz
        assert isinstance(wconfig, WireConfig), 'Invalid wire configuration %s' % wconfig
        value = clazz.__dict__.get(wconfig.name, None)
        if value and not isclass(value): return deepcopy(value)
        if wconfig.hasValue: return deepcopy(wconfig.value)
        raise ConfigError('A configuration value is required for %r in class %r' % (wconfig.name, clazz.__name__))

    if module:
        assert ismodule(module), 'Invalid setup module %s' % module
        registry = module.__dict__
        group = module.__name__
    else:
        registry = callerLocals()
        if '__name__' not in registry:
            raise SetupError('The create wiring call needs to be made directly from the module')
        group = registry['__name__']
    wirings = {}
    for clazz in _classes(classes):
        wiring = Wiring.wiringOf(clazz)
        if wiring:
            wirings[clazz] = wiring
            assert isinstance(wiring, Wiring)
            for wconfig in wiring.configurations:
                assert isinstance(wconfig, WireConfig)
                name = SetupEntityWire.nameFor(group, clazz, wconfig)
                for setup in setupsOf(registry, SetupConfig):
                    assert isinstance(setup, SetupConfig)
                    if setup.name == name: break
                else:
                    configCall = partial(processConfig, clazz, wconfig)
                    configCall.__doc__ = wconfig.description
                    register(SetupConfig(configCall, type=wconfig.type, name=name, group=group), registry)
    if wirings:
        wire = setupFirstOf(registry, SetupEntityWire)
        if wire:
            assert isinstance(wire, SetupEntityWire)
            wire.update(wirings)
        else: register(SetupEntityWire(group, wirings), registry)

def listenToEntities(*classes, listeners=None, beforeBinding=True, module=None, all=False):
    '''
    Listens for entities defined in the provided module that are of the provided classes. The listening is done at the 
    moment of the entity creation so the listen is not dependent of the declared entity return type.
    
    @param classes: arguments(string|class|AOPClasses)
        The classes to listen to, this classes can be either the same class or a super class of the instances generated
        by the entity setup functions.
    @param listeners: None|Callable|list[Callable]|tuple(Callable)
        The listeners to be invoked. The listeners Callable's will take one argument that is the instance.
    @param module: module|dictionary{string:object}|None
        If the setup module is not provided than the calling module will be considered as the registry for the setup.
    @param all: boolean
        Flag indicating that the listening should be performed on all assembly.
    @param beforeBinding: boolean
        Flag indicating that the listening should be performed before any binding occurs (True) or after the
        bindings (False).
    '''
    if not listeners: listeners = []
    elif not isinstance(listeners, (list, tuple)): listeners = [listeners]
    assert isinstance(listeners, (list, tuple)), 'Invalid listeners %s' % listeners
    assert isinstance(beforeBinding, bool), 'Invalid before binding flag %s' % beforeBinding
    assert isinstance(all, bool), 'Invalid all flag %s' % all
    if not module:
        registry = callerLocals()
        if '__name__' not in registry:
            raise SetupError('The create proxy call needs to be made directly from the module')
        if all: group = None
        else: group = registry['__name__']
    elif ismodule(module):
        registry = module.__dict__
        if all: group = None
        else: group = module.__name__
    else:
        assert isinstance(module, dict), 'Invalid setup module %s' % module
        if '__name__' not in module:
            raise SetupError('The provided registry dictionary has no __name__')
        registry = module
        if all: group = None
        else: group = module['__name__']

    if beforeBinding: setup = SetupEntityListen(group, _classes(classes), listeners)
    else: setup = SetupEntityListenAfterBinding(group, _classes(classes), listeners)
    register(setup, registry)

def bindToEntities(*classes, binders=None, module=None):
    '''
    Creates entity implementation proxies for the provided entities classes found in the provided module. The binding is
    done at the moment of the entity creation so the binding is not dependent of the declared entity return type.
    
    @param classes: arguments(string|class|AOPClasses)
        The classes to be proxied.
    @param binders: None|Callable|list[Callable]|tuple(Callable)
        The binders to be invoked when a proxy is created. The binders Callable's will take one argument that is the newly
        created proxy instance.
    @param module: module|None
        If the setup module is not provided than the calling module will be considered.
    '''
    if not binders: binders = []
    elif not isinstance(binders, (list, tuple)): binders = [binders]
    assert isinstance(binders, (list, tuple)), 'Invalid binders %s' % binders
    if module:
        assert ismodule(module), 'Invalid setup module %s' % module
        registry = module.__dict__
        group = module.__name__
    else:
        registry = callerLocals()
        if '__name__' not in registry:
            raise SetupError('The create proxy call needs to be made directly from the module')
        group = registry['__name__']
    register(SetupEntityProxy(group, _classes(classes), binders), registry)

def loadAllEntities(*classes, module=None):
    '''
    Loads all entities that have the type in the provided classes.
    
    @param classes: arguments(string|class|AOPClasses)
        The classes to have the entities loaded for.
    @param module: module|None
        If the setup module is not provided than the calling module will be considered.
    @return: Setup
        The setup start that loads all the entities, the return value can be used for after and before events.
    '''
    def loadAll(prefix, classes):
        for clazz in classes:
            for name, call in Assembly.current().calls.items():
                if name.startswith(prefix) and isinstance(call, CallEntity) and call.type and \
                (call.type == clazz or issubclass(call.type, clazz)): Assembly.process(name)

    if module:
        assert ismodule(module), 'Invalid setup module %s' % module
        registry = module.__dict__
        group = module.__name__
    else:
        registry = callerLocals()
        if '__name__' not in registry:
            raise SetupError('The create proxy call needs to be made directly from the module')
        group = registry['__name__']

    loader = partial(loadAll, group + '.', _classes(classes))
    return register(SetupStart(loader, name='loader_%s' % id(loader)), registry)

def include(module, inModule=None):
    '''
    By including the provided module all the setup functions from the the included module are added as belonging to the
    including module, is just like defining the setup functions again in the including module.
    
    @param module: module
        The module to be included.
    @param inModule: module|None
        If the setup module is not provided than the calling module will be considered.
    '''
    assert ismodule(module), 'Invalid module %s' % module

    if inModule:
        assert ismodule(inModule), 'Invalid setup module %s' % inModule
        registry = inModule.__dict__
    else: registry = callerLocals()
    exec(compile(getsource(module), registry['__file__'], 'exec'), registry)

# --------------------------------------------------------------------
# Functions available in setup functions calls.

def entities():
    '''
    !Attention this function is only available in an open assembly @see: ioc.open!
    Provides all the entities references found in the current assembly wrapped in a AOP class.
    
    @return: AOP
        The resource AOP.
    '''
    return AOPResources({name:name for name, call in Assembly.current().calls.items() if isinstance(call, CallEntity)})

def entitiesLocal():
    '''
    !Attention this function is only available in an open assembly @see: ioc.open!
    Provides all the entities references for the module from where the call is made found in the current assembly.
    
    @return: AOP
        The resource AOP.
    '''
    registry = callerGlobals()
    if '__name__' not in registry:
        raise SetupError('The create call needs to be made from a module function')
    rsc = AOPResources({name:name for name, call in Assembly.current().calls.items() if isinstance(call, CallEntity)})
    rsc.filter(registry['__name__'] + '.**')
    return rsc

def entitiesFor(clazz, assembly=None):
    '''
    !Attention this function is only available in an open assembly if the assembly is not provided @see: ioc.open!
    Provides the entities for the provided class (only if the setup function exposes a return type that is either the
    provided class or a super class) found in the current assembly.
    
    @param clazz: class
        The class to find the entities for.
    @param assembly: Assembly|None
        The assembly to find the entities in, if None the current assembly will be considered.
    @return: list[object]
        The instances for the provided class.
    '''
    assert isclass(clazz), 'Invalid class %s' % clazz
    assembly = assembly or Assembly.current()
    assert isinstance(assembly, Assembly), 'Invalid assembly %s' % assembly

    entities = (name for name, call in assembly.calls.items()
                if isinstance(call, CallEntity) and call.type and (call.type == clazz or issubclass(call.type, clazz)))

    Assembly.stack.append(assembly)
    try: return [assembly.processForName(name) for name in entities]
    finally: Assembly.stack.pop()

def entityFor(clazz, assembly=None):
    '''
    !Attention this function is only available in an open assembly @see: ioc.open!
    Provides the entity for the provided class (only if the setup function exposes a return type that is either the
    provided class or a super class) found in the current assembly.
    
    @param clazz: class
        The class to find the entity for.
    @param assembly: Assembly|None
        The assembly to find the entity in, if None the current assembly will be considered.
    @return: object
        The instance for the provided class.
    @raise SetupError: In case there is no entity for the required class or there are to many.
    '''
    assert isclass(clazz), 'Invalid class %s' % clazz
    assembly = assembly or Assembly.current()
    assert isinstance(assembly, Assembly), 'Invalid assembly %s' % assembly

    entities = [name for name, call in assembly.calls.items()
                if isinstance(call, CallEntity) and call.type and (call.type == clazz or issubclass(call.type, clazz))]
    if not entities:
        raise SetupError('There is no entity setup function having a return type of class or subclass %s' % clazz)
    if len(entities) > 1:
        raise SetupError('To many entities setup functions %r having a return type of class or subclass %s' % 
                         (', '.join(entities), clazz))

    Assembly.stack.append(assembly)
    try: return assembly.processForName(entities[0])
    finally: Assembly.stack.pop()

# --------------------------------------------------------------------

def _classes(classes):
    '''
    Provides the classes from the list of provided class references.
    
    @param classes: list(class|AOPClasses)|tuple(class|AOPClasses)
        The classes or class reference to pull the classes from.
    @return: list[class]
        the list of classes obtained.
    '''
    assert isinstance(classes, (list, tuple)), 'Invalid classes %s' % classes
    clazzes = []
    for clazz in classes:
        if isinstance(clazz, str):
            clazzes.extend(classesIn(clazz).asList())
        elif isclass(clazz): clazzes.append(clazz)
        elif isinstance(clazz, AOPClasses):
            assert isinstance(clazz, AOPClasses)
            clazzes.extend(clazz.asList())
        else: raise SetupError('Cannot use class %s' % clazz)
    return clazzes
