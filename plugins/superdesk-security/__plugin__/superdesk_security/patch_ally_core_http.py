'''
Created on Feb 19, 2013

@package: superdesk security
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the ally core http setup patch.
'''

from .service import assemblyGateways
from ally.container import ioc, support, aop
from ally.container.support import nameInEntity
from ally.design.processor.assembly import Assembly
import logging

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

try: from __setup__ import ally_core_http
except ImportError: log.info('No ally core http component available, thus cannot populate configurations and processors')
else:
    ally_core_http = ally_core_http  # Just to avoid the import warning
    # ----------------------------------------------------------------
    
    from . import patch_ally_core
    from .patch_ally_core import gatewaysFromPermissions, updateAssemblyGatewaysForResources
    from __setup__.ally_core_http.processor import root_uri_resources
    from __setup__.ally_http.processor import headerEncodeRequest
    from acl.core.impl.processor.resource_gateway import GatewaysFromPermissions
    from acl.core.impl.processor import resource_gateway_persist
    
    gatewaysPersistenceFromPermissions = support.notCreated  # Just to avoid errors
    support.createEntitySetup(aop.classesIn(resource_gateway_persist))
    
    # --------------------------------------------------------------------
    
    @ioc.entity
    def assemblyPersistenceGateways() -> Assembly:
        ''' Assembly used for creating the persistence gateways'''
        return Assembly('Persistence gateways')

    # --------------------------------------------------------------------

    root_uri = ioc.entityOf(nameInEntity(GatewaysFromPermissions, 'root_uri_resources'), module=patch_ally_core)
    ioc.doc(root_uri, '''
        !Attention, this is automatically set to the server resources root. 
        ''')
    
    @ioc.before(root_uri, auto=False)
    def root_uri_force():
        support.force(root_uri, root_uri_resources())
    
    @ioc.after(assemblyPersistenceGateways)
    def updateAssemblyPersistenceGateways():
        assemblyPersistenceGateways().add(gatewaysFromPermissions())
        
    @ioc.after(updateAssemblyGatewaysForResources)
    def updateAssemblyGatewaysForPersistenceResources():
        assemblyGateways().add(headerEncodeRequest(), gatewaysPersistenceFromPermissions(), before=gatewaysFromPermissions())
