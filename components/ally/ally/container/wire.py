'''
Created on Dec 15, 2011

@package: ally base
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the IoC auto wiring.
'''

from ._impl._entity import Wiring, WireEntity, WireConfig
from ._impl._setup import normalizeConfigType, setupsOf, SetupConfig, register, \
    setupFirstOf
from ._impl._support import SetupEntityWire
from .error import WireError, ConfigError, SetupError
from ally.support.util_sys import callerLocals
from copy import deepcopy
from functools import partial
from inspect import isclass
    
# --------------------------------------------------------------------

def entity(name, type=None):
    '''
    Used for defining a wired entity attribute. If the type is not provided the entity attribute needs to contain a 
    class or type that will help the wiring to know exactly the expected type.
    
    @param attribute: string
        The entities attribute name to be added to the wiring context.
    @param type: class
        The class of the expected attribute value.
    '''
    assert isinstance(name, str), 'Invalid attribute name %s' % name
    locals = callerLocals()
    if not type:
        if name not in locals: raise WireError('Invalid entity name %r, cannot find it in locals' % name)
        type = locals[name]
    if not isclass(type): raise WireError('Invalid type %s for %r' % (type, name))
    Wiring.wiringFor(locals).addEntity(name, type)
        
def config(name, type=None, doc=None):
    '''
    Used for defining a wired configuration attribute. If the type is not provided the configuration attribute needs 
    to contain a class or type that will help the wiring to know exactly the expected type, if the attribute is None or 
    not existing than the attribute is not validate by type.
    
    @param name: string
        The configurations attribute names to be added to the wiring context.
    @param type: class
        The type of the attribute
    @param doc: string
        The description of the attribute
    '''
    assert isinstance(name, str), 'Invalid attribute name %s' % name
    assert not doc or isinstance(doc, str), 'Invalid description %s' % doc
    if not name.islower():
        raise WireError('Invalid name %r for configuration, needs to be lower case only' % name)
    locals = callerLocals()
    hasValue, value = False, None
    if not type:
        if name in locals:
            v = locals[name]
            if isclass(v): type = v
            else:
                hasValue, value = True, v
                if v is not None: type = v.__class__
        if type and not isclass(type): raise WireError('Invalid type %s for %r' % (type, name))
    else:
        if not isclass(type): raise WireError('Invalid type %s for %r' % (type, name))
        v = locals[name]
        if isinstance(v, type): hasValue, value = True, v
    
    type = normalizeConfigType(type)
    Wiring.wiringFor(locals).addConfiguration(name, type, hasValue, value, doc)

# --------------------------------------------------------------------

def wire(*classes):
    '''
    Decorator for setup functions that need to be wired. Attention you need to decorate an already decorated setup function.
    example:
        
        @wire.wire(MyClassImpl)
        @ioc.entity
        def myEntity() -> IMyClassAPI:
            return MyClassImpl()
    
    @param classes: arguments[class]
        The class(es) that contains the wirings to be associated with the entity of the decorated setup function.
    '''
    assert classes, 'At least one class is expected'
    if __debug__:
        for clazz in classes: assert isclass(clazz), 'Invalid class %s' % clazz
    def decorator(setup):
        from .support import nameEntity, nameInEntity
        registry = callerLocals()
        assert '__name__' in registry, 'The wire call needs to be made directly from the setup module'
        group = registry['__name__']
        for clazz in classes:
            if not createWirings(clazz, setup, group, registry, nameEntity, nameInEntity):
                raise SetupError('Invalid class %s, has no wirings' % clazz)
        return setup
    
    return decorator

# --------------------------------------------------------------------

def validateWiring(entity):
    '''
    Validates the wiring for the provided entity. Basically take all wirings and see if there is a valid value in the
    entity.
    
    @param entity: object
        The entity to validate.
    @raise WireError: In case of missing or invalid value for a wiring.
    '''
    assert entity is not None, 'A entity is required'
    wiring = Wiring.wiringOf(entity.__class__)
    assert isinstance(wiring, Wiring), 'No wiring available for %s' % entity.__class__
    for wentity in wiring.entities:
        assert isinstance(wentity, WireEntity)
        v = entity.__dict__.get(wentity.name)
        if not isinstance(v, wentity.type):
            raise WireError('Invalid entity value %s with expected type %s for %r' % (v, wentity.type, wentity.name))
    for wconfig in wiring.configurations:
        assert isinstance(wconfig, WireConfig)
        v = entity.__dict__.get(wconfig.name)
        if wconfig.type:
            if not isinstance(v, wconfig.type):
                raise WireError('Invalid configuration value %s with expected type %s for %r' % 
                                (v, wconfig.type, wconfig.name))
        elif not wconfig.hasValue:
            raise WireError('No configuration value for %r' % wconfig.name)

def createWirings(clazz, target, group, registry, nameEntity, nameInEntity):
    '''
    Create wiring bindings and setups for the provided parameters.
    
    @param clazz: class
        The class that contains the wirings.
    @param target: object
        The target setup to perform the wiring on.
    @param group: string
        The group used for the wiring setups.
    @param registry: dictionary{string: object}
        The registry where the wiring setups are placed.
    @param nameEntity: callable like @see: nameEntity in support
        The call to use in getting the setups functions names.
    @param nameInEntity: callable like @see: nameInEntity in support
        The call to use in getting the setups functions names based on entity properties.
    @return: boolean
        True if wirings have been created, False otherwise.
    '''
    assert isclass(clazz), 'Invalid class %s' % clazz
    assert target is not None, 'A target is required'
    assert isinstance(group, str), 'Invalid group %s' % group
    assert isinstance(registry, dict), 'Invalid registry %s' % registry
    assert callable(nameEntity), 'Invalid entity name call %s' % nameEntity
    assert callable(nameInEntity), 'Invalid name in entity call %s' % nameInEntity
    
    wiring = Wiring.wiringOf(clazz)
    if not wiring: return False
    mapping = {}
    assert isinstance(wiring, Wiring)
    for wconfig in wiring.configurations:
        assert isinstance(wconfig, WireConfig)
        name = nameInEntity(clazz, wconfig.name, location=target)
        for setup in setupsOf(registry, SetupConfig):
            assert isinstance(setup, SetupConfig)
            if setup.name == name: break
        else:
            mapping[wconfig.name] = name
            configCall = partial(wrapperWiredConfiguration, clazz, wconfig)
            configCall.__doc__ = wconfig.description
            if wconfig.type is not None: types = (wconfig.type,)
            else: types = ()
            register(SetupConfig(configCall, types=types, name=name, group=group), registry)
    wire = setupFirstOf(registry, SetupEntityWire)
    if not wire: wire = register(SetupEntityWire(group), registry)
    assert isinstance(wire, SetupEntityWire)
    wire.update(nameEntity(target), wiring, mapping)
    return True
        
def wrapperWiredConfiguration(clazz, wconfig):
    '''
    Wraps the wired configuration and behaves like a configuration function so it can be used for setup.
    
    @param clazz: class
        The class containing the wired configuration.
    @param wconfig: WireConfig
        The wired configuration to wrap.
    '''
    assert isclass(clazz), 'Invalid class %s' % clazz
    assert isinstance(wconfig, WireConfig), 'Invalid wire configuration %s' % wconfig
    value = clazz.__dict__.get(wconfig.name, None)
    if value and not isclass(value): return deepcopy(value)
    if wconfig.hasValue: return deepcopy(wconfig.value)
    raise ConfigError('A configuration value is required for \'%s\' in class %s' % (wconfig.name, clazz.__name__))
