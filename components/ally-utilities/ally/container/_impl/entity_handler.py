'''
Created on Jan 12, 2012

@package Newscoop
@copyright 2011 Sourcefabric o.p.s.
@license http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides handlers for entities.
'''

from _abcoll import Callable
from ally.support.util import Attribute
from functools import partial
from inspect import isclass
import logging

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

class Initializer(Callable):
    '''
    Class used as the initializer for the entities classes.
    '''
    
    ATTR_INITIALIZED = Attribute(__name__, 'initialized', bool)
    # Provides the attribute for the initialized flag.
    ATTR_ARGUMENTS = Attribute(__name__, 'arguments')
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
        if initializer and not cls.ATTR_INITIALIZED.get(entity, False):
            assert isinstance(initializer, Initializer)
            if entity.__class__ == initializer._entityClazz:
                args, keyargs = cls.ATTR_ARGUMENTS.getOwn(entity)
                cls.ATTR_ARGUMENTS.deleteOwn(entity)
                cls.ATTR_INITIALIZED.set(entity, True)
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
        if self.ATTR_INITIALIZED.get(entity, False):
            return self._entityInit(entity, *args, **keyargs)
        assert not self.ATTR_ARGUMENTS.hasOwn(entity), 'Cannot initialize twice the entity %s' % entity
        self.ATTR_ARGUMENTS.setOwn(entity, (args, keyargs))

    def __get__(self, entity, owner=None):
        '''
        @see: http://docs.python.org/reference/datamodel.html
        '''
        if entity is not None: return partial(self.__call__, entity)
        return self

# --------------------------------------------------------------------

class WireError(Exception):
    '''
    Exception thrown when there is a wiring problem.
    '''

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
    
    ATTR_WIRE = Attribute(__name__, 'wiring')
    # The attribute for the wiring.
    ATTR_WIRE_COMPILED = Attribute(__name__, 'compiled')
    # The attribute for the wiring.
    
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
        wiring = cls.ATTR_WIRE.getDict(register, None)
        if not wiring:
            wiring = Wiring()
            cls.ATTR_WIRE.setDict(register, wiring)
        return wiring
    
    @classmethod
    def wiringOf(cls, clazz):
        '''
        Provides the wiring for the provided class. This process checks all the inherited classes and compiled a wiring.
        
        @param clazz: class
            The class to provide the compiled wiring for.
        @return: Wiring|None
            The compiled wiring for the class, or None if there is no wiring available.
        '''
        assert isclass(clazz), 'Invalid class %s' % clazz
        compiled = cls.ATTR_WIRE_COMPILED.getOwn(clazz, None)
        if compiled is None:
            wirings = []
            if cls.ATTR_WIRE.hasOwn(clazz): wirings.append(cls.ATTR_WIRE.getOwn(clazz))
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
                cls.ATTR_WIRE_COMPILED.set(clazz, compiled)
            else: cls.ATTR_WIRE_COMPILED.set(clazz, False)
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
            raise WireError('There is already a entity attribute with name %r registered' % wentity.name)
        if wentity.name in self._configurations:
            raise WireError('There is already a configuration attribute with name %r registered' % wentity.name)
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
            raise WireError('There is already a configuration attribute with name %r registered' % wconfig.name)
        if wconfig.name in self._entities:
            raise WireError('There is already a entity attribute with name %r registered' % wconfig.name)
        self._configurations[wconfig.name] = wconfig
