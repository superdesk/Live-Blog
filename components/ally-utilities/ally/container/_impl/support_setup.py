'''
Created on Jan 13, 2012

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the setup implementations for the IoC support module.
'''

from ..proxy import ProxyWrapper
from .entity_handler import Wiring, WireConfig, WireEntity
from .ioc_setup import Setup, Assembly, SetupError, CallEntity, CallDeliverValue
from _abcoll import Callable
from inspect import isclass
from ally.container.proxy import createProxyOfImpl

# --------------------------------------------------------------------

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
        if self._name in assembly.calls:
            raise SetupError('Cannot add setup function because there is already a setup call for name %r' % self._name)
        assembly.calls[self._name] = CallDeliverValue(self._entity, self._type)

class SetupEntityWire(Setup):
    '''
    Provides the setup event function.
    '''
    
    priority = 4
    
    @classmethod
    def nameFor(cls, group, clazz, config):
        '''
        Creates the name based on the provided data.
        
        @param group: string
            The group.
        @param clazz: class
            The class that contains the configuration.
        @param config: WireConfig
            The configuration to create the name for.
        '''
        assert isinstance(group, str), 'Invalid group %s' % group
        assert isclass(clazz), 'Invalid class %s' % clazz
        assert isinstance(config, WireConfig), 'Invalid wire configuration %s' % config
        return group + '.' + clazz.__name__ + '.' + config.name

    def __init__(self, group, wirings):
        '''
        Creates a setup that will wire entities.
        The wire entities process is as follows:
            - find all entity calls that have the name starting with the provided group and their class is in the
              wired classes.
            - perform all required wirings (this means all wired attributes that have not been set).
        
        @param prefix: string
            The name prefix of the call entities to be wired.
        @param wirings: dictionary(class, Wiring)
            The classes with their wirings to performed wiring for.
        '''
        assert isinstance(group, str), 'Invalid group %s' % group
        assert isinstance(wirings, dict), 'Invalid wirings %s' % wirings
        if __debug__:
            for clazz, wiring in wirings.items():
                assert isclass(clazz), 'Invalid class %s' % clazz
                assert isinstance(wiring, Wiring), 'Invalid wiring %s' % wiring
        self._group = group
        self._wirings = wirings
        
    def update(self, wirings):
        '''
        Updates the wiring of this entity setup wiring.
        
        @param wirings: dictionary(class, Wiring)
            The classes with their wirings to performed wiring for.
        '''
        assert isinstance(wirings, dict), 'Invalid wirings %s' % wirings
        if __debug__:
            for clazz, wiring in wirings.items():
                assert isclass(clazz), 'Invalid class %s' % clazz
                assert isinstance(wiring, Wiring), 'Invalid wiring %s' % wiring
        self._wirings.update(wirings)
        
    def assemble(self, assembly):
        '''
        @see: Setup.assemble
        '''
        assert isinstance(assembly, Assembly), 'Invalid assembly %s' % assembly
        prefix = self._group + '.'
        for name, call in assembly.calls.items():
            if name.startswith(prefix) and isinstance(call, CallEntity):
                assert isinstance(call, CallEntity)
                call.addInterceptor(self._intercept)
                
    def _intercept(self, value):
        '''
        FOR INTERNAL USE!
        This is the interceptor method used in performing the wiring.
        '''
        if value:
            clazz = value.__class__
            wiring = self._wirings.get(clazz)
            if wiring:
                from ally.container.support import entityFor
                assert isinstance(wiring, Wiring)
                for wentity in wiring.entities:
                    assert isinstance(wentity, WireEntity)
                    entity = getattr(value, wentity.name, None)
                    if not entity or entity == wentity.type:
                        setattr(value, wentity.name, entityFor(wentity.type))
                for wconfig in wiring.configurations:
                    assert isinstance(wconfig, WireConfig)
                    config = getattr(value, wconfig.name, None)
                    if not config or config == wconfig.type:
                        setattr(value, wconfig.name, Assembly.process(self.nameFor(self._group, clazz, wconfig)))
        return value

class SetupEntityProxy(Setup):
    '''
    Provides the setup event function.
    '''
    
    priority = 5
    
    def __init__(self, group, classes, listeners):
        '''
        Creates a setup that will create proxies for the entities that inherit or are in the provided classes.
        The proxy create process is as follows:
            - find all entity calls that have the name starting with the provided group
            - if the entity instance inherits a class from the provided proxy classes it will create a proxy for
              that and wrap the entity instance.
            - after the proxy is created invoke all the proxy listeners.
        
        @param group: string
            The name group of the call entities to be proxied.
        @param classes: list[class]|tuple(class)
            The classes to create the proxies for.
        @param listeners: list[Callable]|tuple(Callable)
            A list of Callable objects to be invoked when a proxy is created. The Callable needs to take one parameter
            that is the proxy.
        '''
        assert isinstance(group, str), 'Invalid group %s' % group
        assert isinstance(classes, (list, tuple)), 'Invalid classes %s' % classes
        assert isinstance(listeners, (list, tuple)), 'Invalid proxy listeners %s' % listeners
        if __debug__:
            for clazz in classes: assert isclass(clazz), 'Invalid class %s' % clazz
            for call in listeners: assert isinstance(call, Callable), 'Invalid listener %s' % call
        self._group = group
        self._classes = classes
        self._listeners = listeners
        
    def assemble(self, assembly):
        '''
        @see: Setup.assemble
        '''
        assert isinstance(assembly, Assembly), 'Invalid assembly %s' % assembly
        prefix = self._group + '.'
        for name, call in assembly.calls.items():
            if name.startswith(prefix) and isinstance(call, CallEntity):
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
                    # If there are to many proxies we find out which ones are sub classes.
                    
                    proxies = [clazz for clazz in proxies 
                               if all(not issubclass(cls, clazz) for cls in proxies if cls != clazz)]
                if len(proxies) > 1:
                    raise SetupError('Cannot create proxy for %s, because to many proxy classes matched %s' % 
                                     (value, proxies))
                proxy = createProxyOfImpl(proxies[0])
                value = proxy(ProxyWrapper(value))
                
                for listener in self._listeners: listener(value)
        return value

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

