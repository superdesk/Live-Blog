'''
Created on Dec 15, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the IoC auto wiring.
'''

from ._impl.entity_handler import Wiring, WireError
from ._impl.ioc_setup import normalizeConfigType
from ally.support.util_sys import callerLocals
from inspect import isclass

# --------------------------------------------------------------------

WireError = WireError
    
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
    type = normalizeConfigType(type)
    Wiring.wiringFor(locals).addConfiguration(name, type, hasValue, value, doc)
