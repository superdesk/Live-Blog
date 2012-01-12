'''
Created on Dec 15, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the IoC auto wiring.
'''

from ally.support.util import Attribute
from inspect import isclass
import inspect

# --------------------------------------------------------------------
# Flags

F_HAS_VALUE = 1
# Flag indicating that the wired attribute has a default value. It means that the entity has a default and the context
# will use this value to populate on.
F_NO_UPDATE = 2
# Flag indicating that the wired attribute does not support updates after the entity has been created.

# --------------------------------------------------------------------

class WireError(Exception):
    '''
    Exception thrown when there is a wiring problem.
    '''
    
# --------------------------------------------------------------------

def entity(*attributes, criteria=None, flag=0):
    '''
    Used for defining a wired entity attribute. If the criteria is not provided the entity attribute needs to contain a 
    class or type that will help the wiring to know exactly the expected type, if the attribute is None or not existing 
    than only the attribute name will be used. If the flag F_HAS_VALUE is set then this will be the original value for
    the attribute. If the entity that is to be wired has a value for the attribute name than that attribute will not be
    wired, also if a criteria is provided then the attribute is only read, this is helpful to use descriptors for setting
    properties.
    
    @param attributes: arguments[string]
        The entities attribute names to be added to the wiring context.
    @param criteria: object
        The criteria of the attribute.
    @param flag: integer
        The flags for the wired entity(s), see all constants starting with F_ defined in this module.
    '''
    assert isinstance(flag, int), 'Invalid flag %s' % flag
    callerLocals = inspect.stack()[1][0].f_locals # Provides the locals from the calling class
    if ATTR_WIRE.hasDict(callerLocals): wiring = ATTR_WIRE.getDict(callerLocals)
    else: wiring = ATTR_WIRE.setDict(callerLocals, Wiring())
    for name in attributes:
        assert isinstance(name, str), 'Invalid name %s' % name
        #wiring.addAttributeEntity(name, criteria, flag)
        
def config(*attributes, doc=None, criteria=None, flag=0):
    '''
    Used for defining a wired configuration attribute. If the criteria is not provided the configuration attribute needs 
    to contain a class or type that will help the wiring to know exactly the expected type, if the attribute is None or 
    not existing than only the attribute name will be used. If the flag F_HAS_VALUE is set then this will be the 
    original value for the attribute. If a criteria is provided then the attribute is only read, this is helpful to use
    descriptors for setting properties.
    
    @param attributes: arguments[string]
        The configurations attribute names to be added to the wiring context.
    @param criteria: class
        The criteria of the attribute.
    @param flag: integer
        The flags for the wired configuration(s), see all constants starting with F_ defined in this module.
    '''
    assert isinstance(flag, int), 'Invalid flag %s' % flag
    callerLocals = inspect.stack()[1][0].f_locals # Provides the locals from the calling class
    if ATTR_WIRE.hasDict(callerLocals): wiring = ATTR_WIRE.getDict(callerLocals)
    else: wiring = ATTR_WIRE.setDict(callerLocals, Wiring())
    for name in attributes:
        assert isinstance(name, str), 'Invalid name %s' % name
        #wiring.addAttributeConfiguration(name, doc, criteria, flag)

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
        if name in self._entities: raise WireError('There is already a entity attribute with name %r registered')
        if name in self._configurations:
            raise WireError('There is already a configuration attribute with name %r registered')
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
        if name in self._entities: raise WireError('There is already a entity attribute with name %r registered')
        if name in self._configurations:
            raise WireError('There is already a configuration attribute with name %r registered')
        self._configurations[name] = (flag, description)

# --------------------------------------------------------------------

ATTR_WIRE = Attribute(__name__, 'wiring', Wiring)
# The attribute for the handler.

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
        if ATTR_WIRE.hasOwn(clazz):
            wiring = ATTR_WIRE.getOwn(clazz)
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
                raise WireError('Found entity for %r but is not of the expected class %r wired in %r',
                                 name, rscType.__name__, clazz.__name__)
        else:
            try: rsc = ctx[rscType]
            except KeyError:
                raise WireError('Cannot locate any entity for %r of class %r to wire in %r',
                                 name, rscType.__name__, clazz.__name__)
    else:
        try: rsc = getattr(ctx, name)
        except AttributeError:
            raise WireError('No entity for name %r was found to wire in %r', name, clazz.__name__)
    setattr(entity, name, rsc)  

