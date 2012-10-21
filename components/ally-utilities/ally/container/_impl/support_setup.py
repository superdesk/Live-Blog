'''
Created on Jan 13, 2012

@package: ally utilities
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the setup implementations for the IoC support module.
'''

from ..proxy import proxyWrapFor
from .entity_handler import Wiring, WireConfig, WireEntity
from .ioc_setup import Setup, Assembly, SetupError, CallEntity, SetupSource
from functools import partial
from inspect import isclass
import logging

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

class SetupEntityWire(Setup):
    '''
    Provides the setup event function.
    '''

    priority_assemble = 4

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
        self.group = group
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
        prefix = self.group + '.'
        for name, call in assembly.calls.items():
            if name.startswith(prefix) and isinstance(call, CallEntity):
                assert isinstance(call, CallEntity)
                if call.marks.count(self) == 0:
                    call.addInterceptor(partial(self._intercept, assembly))
                    call.marks.append(self)

    def _intercept(self, assembly, value, followUp):
        '''
        FOR INTERNAL USE!
        This is the interceptor method used in performing the wiring.
        '''
        assert isinstance(assembly, Assembly), 'Invalid assembly %s' % assembly
        if value is not None:
            clazz = value.__class__
            wiring = self._wirings.get(clazz)
            if wiring:
                def followWiring():
                    from ally.container.support import entityFor
                    assert isinstance(wiring, Wiring)
                    for wentity in wiring.entities:
                        assert isinstance(wentity, WireEntity)
                        if wentity.name not in value.__dict__:
                            try: setattr(value, wentity.name, entityFor(wentity.type))
                            except: raise SetupError('Cannot solve wiring \'%s\' for %s' % (wentity.name, value))
                    for wconfig in wiring.configurations:
                        assert isinstance(wconfig, WireConfig)
                        if wconfig.name not in value.__dict__:
                            name = self.nameFor(self.group, clazz, wconfig)
                            setattr(value, wconfig.name, assembly.processForName(name))
                    if followUp: followUp()
                return value, followWiring
        return value, followUp

class SetupEntityListen(Setup):
    '''
    Provides the setup entity listen by type.
    '''

    priority_assemble = 5

    def __init__(self, group, classes, listeners):
        '''
        Creates a setup that will listen for entities that inherit or are in the provided classes.
        
        @param group: string|None
            The name group of the call entities to be listened.
        @param classes: list[class]|tuple(class)
            The classes to listen for.
        @param listeners: list[Callable]|tuple(Callable)
           The listeners to be invoked. The listeners Callable's will take one argument that is the instance.
        '''
        assert group is None or isinstance(group, str), 'Invalid group %s' % group
        assert isinstance(classes, (list, tuple)), 'Invalid classes %s' % classes
        assert isinstance(listeners, (list, tuple)), 'Invalid listeners %s' % listeners
        if __debug__:
            for clazz in classes: assert isclass(clazz), 'Invalid class %s' % clazz
            for call in listeners: assert callable(call), 'Invalid listener %s' % call
        self.group = group
        self._classes = classes
        self._listeners = listeners

    def assemble(self, assembly):
        '''
        @see: Setup.assemble
        '''
        assert isinstance(assembly, Assembly), 'Invalid assembly %s' % assembly
        if self.group: prefix = self.group + '.'
        else: prefix = None
        for name, call in assembly.calls.items():
            if isinstance(call, CallEntity):
                assert isinstance(call, CallEntity)
                if prefix is None or name.startswith(prefix):
                    if call.marks.count(self) == 0:
                        call.addInterceptor(self._intercept)
                        call.marks.append(self)

    def _intercept(self, value, followUp):
        '''
        FOR INTERNAL USE!
        This is the interceptor method used in listening.
        '''
        if value is not None:
            for clazz in self._classes:
                if isinstance(value, clazz):
                    for listener in self._listeners: listener(value)
                    break
        return value, followUp

class SetupEntityProxy(Setup):
    '''
    Provides the setup entity proxy binding by type.
    '''

    priority_assemble = 6

    def __init__(self, group, classes, binders):
        '''
        Creates a setup that will create proxies for the entities that inherit or are in the provided classes.
        The proxy create process is as follows:
            - find all entity calls that have the name starting with the provided group
            - if the entity instance inherits a class from the provided proxy classes it will create a proxy for
              that and wrap the entity instance.
            - after the proxy is created invoke all the proxy binders.
        
        @param group: string
            The name group of the call entities to be proxied.
        @param classes: list[class]|tuple(class)
            The classes to create the proxies for.
        @param binders: list[Callable]|tuple(Callable)
            A list of Callable objects to be invoked when a proxy is created. The Callable needs to take one parameter
            that is the proxy.
        '''
        assert isinstance(group, str), 'Invalid group %s' % group
        assert isinstance(classes, (list, tuple)), 'Invalid classes %s' % classes
        assert isinstance(binders, (list, tuple)), 'Invalid proxy binders %s' % binders
        if __debug__:
            for clazz in classes: assert isclass(clazz), 'Invalid class %s' % clazz
            for call in binders: assert callable(call), 'Invalid binder %s' % call
        self.group = group
        self._classes = classes
        self._binders = binders

    def assemble(self, assembly):
        '''
        @see: Setup.assemble
        '''
        assert isinstance(assembly, Assembly), 'Invalid assembly %s' % assembly
        prefix = self.group + '.'
        for name, call in assembly.calls.items():
            if name.startswith(prefix) and isinstance(call, CallEntity):
                assert isinstance(call, CallEntity)
                if call.marks.count(self) == 0:
                    call.addInterceptor(self._intercept)
                    call.marks.append(self)

    def _intercept(self, value, followUp):
        '''
        FOR INTERNAL USE!
        This is the interceptor method used in creating the proxies.
        '''
        if value is not None:
            proxies = [clazz for clazz in self._classes if isinstance(value, clazz)]
            if proxies:
                if len(proxies) > 1:
                    # If there are to many proxies we find out which ones are sub classes.

                    proxies = [clazz for clazz in proxies
                               if all(not issubclass(cls, clazz) for cls in proxies if cls != clazz)]
                if len(proxies) > 1:
                    raise SetupError('Cannot create proxy for %s, because to many proxy classes matched %s' % 
                                     (value, proxies))

                value = proxyWrapFor(value)

                for binder in self._binders: binder(value)
        return value, followUp

class SetupEntityListenAfterBinding(SetupEntityListen):
    '''
    Provides the setup entity listen by type but after the binding occurs.
    '''

    priority_assemble = 7

    def __init__(self, group, classes, listeners):
        '''
        @see: SetupEntityListen.__init__
        '''
        super().__init__(group, classes, listeners)

class SetupEntityCreate(SetupSource):
    '''
    Provides the entity create setup.
    '''

    priority_index = 2

    def __init__(self, function, type, **keyargs):
        '''
        Create a setup for entity creation.
        
        @param type: class
            The api class of the entity to create.
        @see: SetupSource.__init__
        '''
        assert isclass(type), 'Invalid api class %s' % type
        SetupSource.__init__(self, function, type, **keyargs)

    def index(self, assembly):
        '''
        @see: Setup.index
        '''
        assert isinstance(assembly, Assembly), 'Invalid assembly %s' % assembly
        if self.name in assembly.calls: raise SetupError('There is already a setup call for name %r' % self.name)
        assembly.calls[self.name] = CallEntity(assembly, self.name, self._function, self.type)

# --------------------------------------------------------------------

class CreateEntity:
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

