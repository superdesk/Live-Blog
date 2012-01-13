'''
Created on Jan 12, 2012

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides support functions for the container.
'''

from ..support.util_sys import callerLocals, callerGlobals
from ._impl.aop_container import AOPClasses, AOPResources
from ._impl.entity_handler import Wiring, WireConfig
from ._impl.ioc_setup import ConfigError, register, SetupConfig, SetupEntity, setups
from ._impl.support_setup import CreateEntity, SetupError, SetupEntityProxy, \
    SetupEntityWire, Assembly, CallEntity
from copy import deepcopy
from functools import partial
from inspect import isclass

# --------------------------------------------------------------------
# Functions available in setup modules.

def createEntitySetup(*classes, format='%s'):
    '''
    Creates entity setup functions for the provided classes. The name of the setup functions that will be generated are
    formed based on the class name of the provided classes.
    
    @param classes: arguments(class|AOPClasses)
        The classes to be added setup functions.
    @param format: string
        The format to use on the entity setup function name. 
    @return: References
        The entities repository for the classes setup functions.
    '''
    assert isinstance(format, str), 'Invalid format %s' % format
    registry = callerLocals()
    if '__name__' not in registry:
        raise SetupError('The create entity call needs to be made directly from the module')
    group = registry['__name__']; prefix = group + '.'
    for clazz in _classes(classes):
        name = prefix + format % clazz.__name__
        register(SetupEntity(CreateEntity(clazz), type=clazz, name=name, group=group), registry)
    createEntityWiring(*classes)

def createEntityWiring(*classes):
    '''
    Creates entity wiring setups for the provided classes. The wiring setups consists of configurations found in the
    provided classes that will be published in the calling setup module.
    
    @param classes: arguments(class|AOPClasses)
        The classes to be wired.
    '''
    def processConfig(clazz, wconfig):
        assert isclass(clazz), 'Invalid class %s' % clazz
        assert isinstance(wconfig, WireConfig), 'Invalid wire configuration %s' % wconfig
        value = clazz.__dict__.get(wconfig.name, None)
        if value and not isclass(value): return deepcopy(value)
        if wconfig.hasValue: return deepcopy(wconfig.value)
        raise ConfigError('A configuration value is required for %r in class %s' % (wconfig.name, clazz))
        
    registry = callerLocals()
    if '__name__' not in registry:
        raise SetupError('The create wiring call needs to be made directly from the module')
    wirings = {}
    group = registry['__name__']; prefix = group + '.'
    for clazz in _classes(classes):
        wiring = Wiring.wiringOf(clazz)
        if wiring:
            wirings[clazz] = wiring
            assert isinstance(wiring, Wiring)
            for wconfig in wiring.configurations:
                assert isinstance(wconfig, WireConfig)
                name = SetupEntityWire.nameFor(prefix, clazz, wconfig)
                for setup in setups(registry):
                    if isinstance(setup, SetupConfig) and setup.name == name: break
                else:
                    configCall = partial(processConfig, clazz, wconfig)
                    configCall.__doc__ = wconfig.description
                    register(SetupConfig(configCall, type=wconfig.type, name=name, group=group), registry)
    register(SetupEntityWire(prefix, wirings), registry)
    
def createEntityProxy(*classes, listeners=None):
    '''
    Creates entity proxies that are for the provided classes only for the entities found in the calling module.
    
    @param classes: arguments(class|AOPClasses)
        The classes to be proxied.
    @param listeners: None|Callable|list[Callable]|tuple(Callable)
        The listeners to be invoked when a proxy is created.
    '''
    if not listeners: listeners = []
    elif not isinstance(listeners, (list, tuple)): listeners = [listeners]
    assert isinstance(listeners, (list, tuple)), 'Invalid listeners %s' % listeners
    registry = callerLocals()
    if '__name__' not in registry:
        raise SetupError('The create proxy call needs to be made directly from the module')
    register(SetupEntityProxy(registry['__name__'] + '.', _classes(classes), listeners), callerLocals())

# --------------------------------------------------------------------
# Functions available in setup functions calls.

def entities():
    '''
    !Attention this function only available from within a setup functions!
    Provides all the entities references found in the current assembly wrapped in a AOP class.
    
    @return: AOP
        The resource AOP.
    '''
    return AOPResources({name:name for name, call in Assembly.current().calls.items() if isinstance(call, CallEntity)})

def entitiesLocal():
    '''
    !Attention this function only available from within a setup functions!
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

def entityFor(clazz):
    '''
    !Attention this function only available from within a setup functions!
    Provides the entity for the provided class (only if the setup function exposes a return type that is either the
    provided class or a super class) found in the current assembly.
    
    @param clazz: class
        The class to find the entity for.
    @return: object
        The instance for the provided class.
    @raise SetupError: In case there is no entity for the required class or there are to many.
    '''
    assert isclass(clazz), 'Invalid class %s' % clazz
    entities = [name for name, call in Assembly.current().calls.items()
                if isinstance(call, CallEntity) and call.type and (call.type == clazz or issubclass(call.type, clazz))]
    if not entities:
        raise SetupError('There is no entity setup function having a return type of class or subclass %s' % clazz)
    if len(entities) > 1:
        raise SetupError('To many entities setup functions %r having a return type of class or subclass %s' % 
                         (', '.join(entities), clazz))
    return Assembly.process(entities[0])

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
        if isclass(clazz): clazzes.append(clazz)
        elif isinstance(clazz, AOPClasses):
            assert isinstance(clazz, AOPClasses)
            clazzes.extend(clazz.asList())
        else: raise SetupError('Cannot use class %s' % clazz)
    return clazzes
