'''
Created on Dec 15, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the IoC auto wiring.
'''

from ally.ioc.node_wire import Wiring
import inspect
from ally.util import Attribute

# --------------------------------------------------------------------
# Flags

F_HAS_DEFAULT = 1
# Flag indicating that the wired attribute has a default value. It means that the entity has a default and if the 
# context is not able to provide another value then keep the one that is set on the attribute.
F_NO_UPDATE = 2
# Flag indicating that the wired attribute does not support updates after the entity has been created.

# --------------------------------------------------------------------

_ATTR_WIRE = Attribute(__name__, 'wiring', Wiring)
# The attribute for the handler.

# --------------------------------------------------------------------

def entity(*attributes, flag=0):
    '''
    Used for defining a wired entity attribute. The entity attribute needs to contain a class or type that will help the
    wiring to know exactly the expected type, if the attribute is None or not existing than only the attribute name will
    be used. If the flag F_HAS_DEFAULT is set then the default value class will be used. If the default is None then the
    name of the attribute will be used for wiring.
    
    @param attributes: arguments[string]
        The entities attribute names to be added to the wiring context.
    @param flag: integer
        The flags for the wired entity(s), see all constants starting with F_ defined in this module.
    '''
    assert isinstance(flag, int), 'Invalid flag %s' % flag
    callerLocals = inspect.stack()[1][0].f_locals # Provides the locals from the calling class
    if _ATTR_WIRE.hasDict(callerLocals): wiring = _ATTR_WIRE.getDict(callerLocals)
    else: wiring = _ATTR_WIRE.setDict(callerLocals, Wiring())
    for name in attributes:
        assert isinstance(name, str), 'Invalid name %s' % name
        wiring.addAttributeEntity(name, flag)
        
def config(*attributes, doc=None, flag=0):
    '''
    Used for defining a wired configuration attribute. The configuration attribute needs to contain a class or type 
    that will help the wiring to know exactly the expected type, if the attribute is None or not existing than only 
    the attribute name will be used. If the flag F_HAS_DEFAULT is set then the default value class will be used. 
    If the default is None then the name of the attribute will be used for wiring.
    
    @param attributes: arguments[string]
        The configurations attribute names to be added to the wiring context.
    @param flag: integer
        The flags for the wired configuration(s), see all constants starting with F_ defined in this module.
    '''
    assert isinstance(flag, int), 'Invalid flag %s' % flag
    callerLocals = inspect.stack()[1][0].f_locals # Provides the locals from the calling class
    if _ATTR_WIRE.hasDict(callerLocals): wiring = _ATTR_WIRE.getDict(callerLocals)
    else: wiring = _ATTR_WIRE.setDict(callerLocals, Wiring())
    for name in attributes:
        assert isinstance(name, str), 'Invalid name %s' % name
        wiring.addAttributeEntity(name, flag)

# --------------------------------------------------------------------

