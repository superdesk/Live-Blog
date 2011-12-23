'''
Created on Dec 16, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Module containing the injected initializer.
'''

from functools import partial
from _abcoll import Callable
from inspect import isclass
import logging
from .node import IListener
from ally.util import Attribute

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

class InitializerListener(IListener):
    '''
    Provides the listener used for initializing the entities.
    '''
    
    def before(self, source):
        '''
        @see: IListener.before
        '''
        
    def after(self, source, result):
        '''
        @see: IListener.after
        '''
        if result is not None: Initializer.initialize(result)

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
