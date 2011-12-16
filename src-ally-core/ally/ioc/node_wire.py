'''
Created on Dec 13, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Module containing the nodes for the IoC wiring setup.
'''

from .node import SetupError, IListener, Source
from inspect import isclass
import logging
from ally import omni
from ally.ioc.wire import _ATTR_WIRE

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

class Creator(Source):
    '''
    Creates entities for a class.
    '''
    
    def __init__(self, name, clazz):
        '''
        @see: Source.__init__
        
        @param clazz: class
            The class 
        '''
        Source.__init__(self, name, clazz)
        assert isclass(clazz), 'Invalid class %s' % clazz
        self._clazz = clazz
        
    def _process(self):
        '''
        Processes the function value.
        @see: Source.processValue
        '''
        entity = self._clazz()
        self.doSetValue(self._path, entity)
        self._listenersBefore()
        assert log.debug('Created and set entity %s of node %s', entity, self) or True
        
        self._listenersAfter(entity)
        assert log.debug('Initialized and set entity %s of node %s', entity, self) or True
        return entity

class WiringListener(IListener):
    '''
    Provides the listener used for wiring the entities.
    '''
    
    def before(self, source):
        '''
        @see: IListener.before
        '''
        
    def after(self, source, result):
        '''
        @see: IListener.after
        '''
        from .context import NAME_CONTEXT
        if result is not None: wire(source.doGetValue(NAME_CONTEXT, omni=omni.F_FIRST), result)
        
# --------------------------------------------------------------------

class Wiring:
    '''
    Provides the context for wiring.
    '''
    
    def __init__(self):
        '''
        Constructs the wiring context.
        '''
        self._entities = {}
        self._configurations = {}
        
    def addAttributeEntity(self, name, flag=0):
        '''
        Adds a new entity attribute.
        
        @param name: string
            The attribute name.
        @param flag: integer
            The flag to use for the attribute.
        '''
        assert isinstance(name, str), 'Invalid name %s' % name
        assert isinstance(flag, int), 'Invalid flag %s' % flag
        if name in self._entities: raise SetupError('There is already a entity attribute with name %r registered')
        if name in self._configurations:
            raise SetupError('There is already a configuration attribute with name %r registered')
        self._entities[name] = flag
        
    def addAttributeConfiguration(self, name, description=None, flag=0):
        '''
        Adds a new configuration attribute.
        
        @param name: string
            The attribute name.
        @param description: string|None
            The configuration description.
        @param flag: integer
            The flag to use for the attribute.
        '''
        assert isinstance(name, str), 'Invalid name %s' % name
        assert not description or isinstance(description, str), 'Invalid description %s' % description
        assert isinstance(flag, int), 'Invalid flag %s' % flag
        if name in self._entities: raise SetupError('There is already a entity attribute with name %r registered')
        if name in self._configurations:
            raise SetupError('There is already a configuration attribute with name %r registered')
        self._configurations[name] = (flag, description)

# --------------------------------------------------------------------

def wire(ctx, entity):
    '''
    Wires the provided entity if the entity is wired, otherwise no action is taken.
    
    @param ctx: object
        The context to wire with.
    @param entity: object
        The entity to wire.
    '''
    assert ctx is not None, 'A context is required'
    assert entity is not None, 'A entity is required'
    clazzes, entities, configurations = [entity.__class__], set(), set()
    while clazzes:
        clazz = clazzes.pop(0)
        if clazz == object: continue
        if _ATTR_WIRE.hasOwn(clazz):
            wiring = _ATTR_WIRE.getOwn(clazz)
            assert isinstance(wiring, Wiring)
            entities.update(wiring._entities)
            configurations.update(wiring._configurations.items())
        clazzes.extend(clazz.__bases__)

    for name in entities: _wireEntity(ctx, entity, name)
    
# --------------------------------------------------------------------

def _wireEntity(ctx, entity, name):
    '''
    Wires to the entity the attribute with the provided name.
    
    @param ctx: object
        The context to wire with.
    @param entity: object
        The entity to wire.
    @param name: string
        The attribute name.
    '''
    assert ctx is not None, 'A context is required'
    assert entity is not None, 'A entity is required'
    clazz = entity.__class__
    rscType = getattr(clazz, name, None)
    value = getattr(entity, name, None)
    if rscType is not value: return
    # If is not the same value it means the entity has something set on the attribute
    
    if isclass(rscType):
        if hasattr(ctx, name):
            rsc = getattr(ctx, name)
            if not isinstance(rsc, rscType):
                raise SetupError('Found entity for %r but is not of the expected class %r wired in %r',
                                 name, rscType.__name__, clazz.__name__)
        else:
            try: rsc = ctx[rscType]
            except KeyError:
                raise SetupError('Cannot locate any entity for %r of class %r to wire in %r',
                                 name, rscType.__name__, clazz.__name__)
    else:
        try: rsc = getattr(ctx, name)
        except AttributeError:
            raise SetupError('No entity for name %r was found to wire in %r', name, clazz.__name__)
    setattr(entity, name, rsc)  
