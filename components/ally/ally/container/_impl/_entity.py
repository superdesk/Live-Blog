'''
Created on Jan 12, 2012

@package ally utilities
@copyright 2011 Sourcefabric o.p.s.
@license http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides handlers for entities.
'''

from ..error import WireError, AventError
from ..impl.priority import Priority
from collections import Iterable
from functools import partial
from inspect import isclass
import logging

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

class Initializer:
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

    @classmethod
    def initialize(cls, entity):
        '''
        Initialize the provided entity.
        '''
        assert entity is not None, 'Need to provide an entity to be initialized'
        initializer = Initializer.initializerFor(entity)
        if initializer is not None:
            assert isinstance(initializer, Initializer)
            if entity.__class__ == initializer._entityClazz:
                if entity.__dict__.get('_ally_ioc_initialized', False): return
                args, keyargs = entity._ally_ioc_arguments
                entity._ally_ioc_initialized = True
                del entity._ally_ioc_arguments
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
        if entity.__dict__.get('_ally_ioc_initialized'): self._entityInit(entity, *args, **keyargs)
        elif entity.__dict__.get('_ally_ioc_arguments') is None: entity._ally_ioc_arguments = (args, keyargs)
        else: raise TypeError('Cannot initialize twice the entity %s' % entity)

    def __get__(self, entity, owner=None):
        '''
        @see: http://docs.python.org/reference/datamodel.html
        '''
        if entity is not None: return partial(self.__call__, entity)
        return self

# --------------------------------------------------------------------

class WireEntity:
    '''
    Provides the container for data in order to wire an entity.
    '''

    def __init__(self, name, type):
        '''
        Construct the entity wiring.
        
        @param name: string
            The name of the attribute to wire the entity to.
        @param type: class
            The type of the entity to wire.
        '''
        assert isinstance(name, str), 'Invalid name %s' % name
        assert isclass(type), 'Invalid type %s' % type
        self.name = name
        self.type = type

class WireConfig:
    '''
    Provides the container for data in order to wire a configuration.
    '''

    def __init__(self, name, type=None, hasValue=False, value=None, description=None):
        '''
        Construct the entity wiring.
        
        @param name: string
            The name of the attribute to wire the configuration to.
        @param type: class|None
            The type of the configuration to wire.
        @param hasValue: boolean
            Flag indicating that there is a value for the configuration.
        @param value: object
            The configuration value.
        @param description: string|None
            The configuration description.
        '''
        assert isinstance(name, str), 'Invalid name %s' % name
        assert not type or isclass(type), 'Invalid type %s' % type
        assert isinstance(hasValue, bool), 'Invalid has value flag %s' % hasValue
        assert not description or isinstance(description, str), 'Invalid description %s' % description
        self.name = name
        self.type = type
        self.hasValue = hasValue
        self.value = value
        self.description = description

class Wiring:
    '''
    Provides the context for wiring.
    '''

    @classmethod
    def wiringFor(cls, register):
        '''
        Provides the wiring registered in the provided register, if there is no wiring one will be created.
        
        @param register: dictionary{string, object}
            The register to provide the wiring from.
        @return: Wiring
            The register wiring or newly created wiring object for the registry.
        '''
        assert isinstance(register, dict), 'Invalid register %s' % register
        wiring = register.get('__ally_wiring__')
        if wiring is None:
            wiring = register['__ally_wiring__'] = Wiring()
            from ally.container.wire import validateWiring
            if '__init__' not in register: register['__init__'] = validateWiring
        return wiring

    @classmethod
    def wiringOf(cls, clazz):
        '''
        Provides the wiring for the provided class. This process checks all the inherited classes and compiles a wiring.
        
        @param clazz: class
            The class to provide the compiled wiring for.
        @return: Wiring|None
            The compiled wiring for the class, or None if there is no wiring available.
        '''
        assert isclass(clazz), 'Invalid class %s' % clazz
        compiled = clazz.__dict__.get('__ally_wiring_compiled__')
        if compiled is None:
            wirings = []
            try: wirings.append(clazz.__ally_wiring__)
            except AttributeError: pass
            for claz in clazz.__bases__:
                if claz == object: continue
                wiring = cls.wiringOf(claz)
                if wiring: wirings.append(wiring)
            if wirings:
                if len(wirings) == 1: compiled = wirings[0]
                else:
                    compiled = Wiring()
                    for wiring in reversed(wirings):
                        assert isinstance(wiring, Wiring), 'Invalid wiring %s' % wiring
                        compiled._entities.update(wiring._entities)
                        compiled._configurations.update(wiring._configurations)
                clazz.__ally_wiring_compiled__ = compiled
            else: clazz.__ally_wiring_compiled__ = False
        elif compiled is False:
            # No compiled wiring available for class
            compiled = None
        return compiled

    def __init__(self):
        '''
        Constructs the wiring context.
        '''
        self._entities = {}
        self._configurations = {}

    configurations = property(lambda self: self._configurations.values(), doc=
'''
@type configurations: Iterable[WireConfig]
    The wired configurations.
''')
    entities = property(lambda self: self._entities.values(), doc=
'''
@type entities: Iterable[WireEntity]
    The wired entities.
''')

    def addEntity(self, name, type):
        '''
        Adds a new entity attribute.
        
        @param name: string
            The attribute name.
        @param type: class
            The type of the entity to wire.
        '''
        wentity = WireEntity(name, type)
        if wentity.name in self._entities:
            raise WireError('There is already a entity attribute with name \'%s\' registered' % wentity.name)
        if wentity.name in self._configurations:
            raise WireError('There is already a configuration attribute with name \'%s\' registered' % wentity.name)
        self._entities[wentity.name] = wentity

    def addConfiguration(self, name, type=None, hasValue=False, value=None, description=None):
        '''
        Adds a new configuration attribute.
        
        @param name: string
            The attribute name.
        @param type: class|None
            The type of the configuration to wire.
        @param hasValue: boolean
            Flag indicating that there is a value for the configuration.
        @param value: object
            The configuration value.
        @param description: string|None
            The configuration description.
        '''
        wconfig = WireConfig(name, type, hasValue, value, description)
        if wconfig.name in self._configurations:
            raise WireError('There is already a configuration attribute with name \'%s\' registered' % wconfig.name)
        if wconfig.name in self._entities:
            raise WireError('There is already a entity attribute with name \'%s\' registered' % wconfig.name)
        self._configurations[wconfig.name] = wconfig

# --------------------------------------------------------------------

class Event:
    '''
    Contains the event data.
    '''
    
    def __init__(self, name, priority, triggers):
        '''
        Construct the event.
        
        @param name: string
            The name of the method to be called for event.
        @param priority: Priority
            The event priority.
        @param triggers: Iterable(ITrigger)
            The triggers to be associated.
        '''
        assert isinstance(name, str), 'Invalid name %s' % name
        assert isinstance(priority, Priority), 'Invalid priority %s' % priority
        assert isinstance(triggers, Iterable), 'Invalid triggers %s' % triggers
        triggers = triggers if isinstance(triggers, set) else set(triggers)
        if __debug__:
            from ..event import ITrigger
            for trigger in triggers: assert isinstance(trigger, ITrigger), 'Invalid trigger %s' % trigger
        self.name = name
        self.priority = priority
        self.triggers = triggers

class Advent:
    '''
    Provides the context for events.
    '''

    @classmethod
    def adventFor(cls, register):
        '''
        Provides the advent registered in the provided register, if there is no advent one will be created.
        
        @param register: dictionary{string, object}
            The register to provide the advent from.
        @return: Advent
            The register advent or newly created advent object for the registry.
        '''
        assert isinstance(register, dict), 'Invalid register %s' % register
        advent = register.get('__ally_advent__')
        if advent is None: advent = register['__ally_advent__'] = Advent()
        return advent

    @classmethod
    def adventOf(cls, clazz):
        '''
        Provides the advent for the provided class. This process checks all the inherited classes and compiled a wiring.
        
        @param clazz: class
            The class to provide the compiled wiring for.
        @return: Wiring|None
            The compiled wiring for the class, or None if there is no wiring available.
        '''
        assert isclass(clazz), 'Invalid class %s' % clazz
        compiled = clazz.__dict__.get('__ally_advent_compiled__')
        if compiled is None:
            advents = []
            try: advents.append(clazz.__ally_advent__)
            except AttributeError: pass
            for claz in clazz.__bases__:
                if claz == object: continue
                advent = cls.adventOf(claz)
                if advent: advents.append(advent)
            if advents:
                if len(advents) == 1: compiled = advents[0]
                else:
                    compiled = Advent()
                    for advent in reversed(advents):
                        assert isinstance(advent, Advent), 'Invalid advent %s' % advent
                        compiled._events.update(advent._events)
                clazz.__ally_advent_compiled__ = compiled
            else: clazz.__ally_advent_compiled__ = False
        elif compiled is False:
            # No compiled wiring available for class
            compiled = None
        return compiled

    def __init__(self):
        '''
        Constructs the events context.
        '''
        self._events = {}

    events = property(lambda self: self._events.values(), doc=
'''
@type events: Iterable[Event]
    The events of the advent.
''')

    def addEvent(self, name, priority, triggers):
        '''
        Adds a new event.
        
        @param name: string
            The name of the method to be called for event.
        @param priority: integer
            The event priority.
        @param triggers: Iterable(ITrigger)
            The triggers to be associated.
        '''
        event = Event(name, priority, triggers)
        if event.name in self._events:
            raise AventError('There is already an event with name %r registered' % event.name)
        self._events[event.name] = event

