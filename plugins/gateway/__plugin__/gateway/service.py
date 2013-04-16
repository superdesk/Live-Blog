'''
Created on Jan 9, 2012

@package: gateway
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Contains the services for gateway.
'''
    
from ..plugin.registry import registerService
from ally.container import support, ioc
from ally.container.support import nameInEntity
from ally.design.processor.assembly import Assembly
from gateway.core.impl.processor.default_gateway import RegisterDefaultGateways

# --------------------------------------------------------------------

registerDefaultGateways = support.notCreated  # Just to avoid errors

# --------------------------------------------------------------------

SERVICES = 'gateway.api.**.I*Service'

support.createEntitySetup('gateway.impl.**.*', RegisterDefaultGateways)
support.listenToEntities(SERVICES, listeners=registerService)
support.loadAllEntities(SERVICES)

# --------------------------------------------------------------------

default_gateways = ioc.entityOf(nameInEntity(RegisterDefaultGateways, 'default_gateways'))

# --------------------------------------------------------------------

@ioc.entity
def assemblyAnonymousGateways() -> Assembly:
    ''' The assembly used for generating anonymous gateways'''
    return Assembly('Anonymous gateways')

# --------------------------------------------------------------------

@ioc.before(assemblyAnonymousGateways)
def updateAssemblyAnonymousGateways():
    assemblyAnonymousGateways().add(registerDefaultGateways())
