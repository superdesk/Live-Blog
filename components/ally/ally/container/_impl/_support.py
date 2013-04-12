'''
Created on Jan 13, 2012

@package: ally base
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the setup implementations for the IoC support module.
'''

from ..aop import classesIn
from ..impl.proxy import proxyWrapFor
from ._aop import AOPClasses
from ._entity import Wiring, WireConfig, WireEntity
from ._setup import Setup, Assembly, SetupError, CallEntity, SetupSource
from ally.support.util_sys import locationStack
from functools import partial
from inspect import isclass, ismodule
import logging

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

class SetupEntityWire(Setup):
    '''
    Provides the setup event function.
    '''

    priority_assemble = 4

    def __init__(self, group):
        '''
        Creates a setup that will wire entities.
        The wire entities process is as follows:
            - find all entity calls that have the name starting with the provided group and their class is in the
              wired classes.
            - perform all required wirings (this means all wired attributes that have not been set).

        @param group: string
            The group name of the call entities to be wired.
        '''
        assert isinstance(group, str), 'Invalid group %s' % group
        self.group = group
        self._wirings = {}

    def update(self, name, wiring, mapping):
        '''
        Updates the wiring of this entity setup wiring.

        @param name: string
            The entity setup name to bind with the provided wiring.
        @param wiring: Wiring
            The wiring to be used for the provided entity setup name.
        @param mapping: dictionary{string: string}
            The name mappings, as a key the wired configuration name and as a value the setup function name where to get
            the configuration value from.
        '''
        assert isinstance(name, str), 'Invalid name %s' % name
        assert isinstance(wiring, Wiring), 'Invalid wiring %s' % wiring
        assert isinstance(mapping, dict), 'Invalid mapping %s' % mapping

        wirings = self._wirings.get(name)
        if wirings is None: wirings = self._wirings[name] = {}
        wirings[wiring] = mapping

    def assemble(self, assembly):
        '''
        @see: Setup.assemble
        '''
        assert isinstance(assembly, Assembly), 'Invalid assembly %s' % assembly
        for name, call in assembly.calls.items():
            wirings = self._wirings.get(name)
            if wirings is not None and isinstance(call, CallEntity):
                assert isinstance(call, CallEntity)
                if call.marks.count(self) == 0:
                    call.addInterceptor(partial(self._intercept, assembly, wirings))
                    call.marks.append(self)

    def _intercept(self, assembly, wirings, value, followUp):
        '''
        FOR INTERNAL USE!
        This is the interceptor method used in performing the wiring.
        '''
        assert isinstance(assembly, Assembly), 'Invalid assembly %s' % assembly
        assert isinstance(wirings, dict), 'Invalid wiring %s' % wirings
        if value is not None:
            def followWiring():
                from ally.container.support import entityFor
                wiring = Wiring.wiringOf(value.__class__)
                if wiring:
                    assert isinstance(wiring, Wiring), 'Invalid wiring %s' % wiring
                    for wentity in wiring.entities:
                        assert isinstance(wentity, WireEntity)
                        if wentity.name not in value.__dict__:
                            try: setattr(value, wentity.name, entityFor(wentity.type, wentity.name))
                            except: raise SetupError('Cannot solve wiring \'%s\' at: %s' %
                                                     (wentity.name, locationStack(value.__class__)))

                    mapping = wirings.get(wiring)
                    if mapping:
                        assert isinstance(mapping, dict), 'Invalid mapping %s' % mapping
                        for wconfig in wiring.configurations:
                            assert isinstance(wconfig, WireConfig)
                            if wconfig.name not in value.__dict__:
                                name = mapping.get(wconfig.name)
                                if name is not None: setattr(value, wconfig.name, assembly.processForName(name))

                if followUp: followUp()
            return value, followWiring
        return value, followUp

    def __str__(self): return '%s for %s' % (self.__class__.__name__, ', '.join(self._wirings.keys()))

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

    def __str__(self): return '%s for:%s' % (self.__class__.__name__,
                                             '\n'.join(locationStack(clazz) for clazz in self._classes))

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
            for clazz in self._classes:
                if isinstance(value, clazz):
                    valueProxy = proxyWrapFor(value)
                    for binder in self._binders:
                        assert log.debug('Binded %s to %s', binder, value) or True
                        binder(valueProxy)
                    value = valueProxy
                    break

        return value, followUp

    def __str__(self): return '%s for:%s' % (self.__class__.__name__,
                                             '\n'.join(locationStack(clazz) for clazz in self._classes))

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

    def __init__(self, function, types, **keyargs):
        '''
        Create a setup for entity creation.

        @param types: tuple(class)|None
            The api classes of the entity to create.
        @see: SetupSource.__init__
        '''
        assert isclass(type), 'Invalid api class %s' % type
        SetupSource.__init__(self, function, types, **keyargs)

    def index(self, assembly):
        '''
        @see: Setup.index
        '''
        assert isinstance(assembly, Assembly), 'Invalid assembly %s' % assembly
        if self.name in assembly.calls: raise SetupError('There is already a setup call for name %r' % self.name)
        assembly.calls[self.name] = CallEntity(assembly, self.name, self._function, self._types)

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

def classesFrom(classes):
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
        if isinstance(clazz, str) or ismodule(clazz):
            clazzes.extend(classesIn(clazz).asList())
        elif isclass(clazz): clazzes.append(clazz)
        elif isinstance(clazz, AOPClasses):
            assert isinstance(clazz, AOPClasses)
            clazzes.extend(clazz.asList())
        else: raise SetupError('Cannot use class %s' % clazz)
    return clazzes
