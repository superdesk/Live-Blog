'''
Created on Feb 19, 2013

@package: superdesk security
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the ally core http setup patch.
'''

from .service import assemblyGateways, userRbac, rbacPopulateRights, \
    registerDefaultRights
from ally.container import ioc, support
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
    from .patch_ally_core import gatewaysFromPermissions, updateAssemblyGatewaysForResources, \
        iterateResourcePermissions, modelFiltersForPermissions
    from __setup__.ally_core_http.processor import root_uri_resources, assemblyResources
    from __setup__.ally_core.processor import invoking
    from acl.core.impl.processor.resource_gateway import GatewaysFromPermissions
    from superdesk.security.core.impl.processor import user_persistence_filter
    
    gatewaysPersistenceFromPermissions = invokingFilter = support.notCreated  # Just to avoid errors
    support.createEntitySetup(user_persistence_filter)
    
    # --------------------------------------------------------------------
    
    @ioc.entity
    def assemblyGatewaysFromPermissions() -> Assembly:
        ''' Assembly used for creating gateways based on resource permissions'''
        return Assembly('Persistence gateways')
    
    @ioc.entity
    def assemblyPermissions() -> Assembly:
        ''' Assembly used for creating resource permissions'''
        return Assembly('Resource permissions')
        
    # --------------------------------------------------------------------
 
    @ioc.before(assemblyGatewaysFromPermissions)
    def updateAssemblyGatewaysFromPermissions():
        assemblyGatewaysFromPermissions().add(gatewaysFromPermissions())
        
    @ioc.before(assemblyPermissions)
    def updateAssemblyPermissions():
        assemblyPermissions().add(userRbac(), rbacPopulateRights(), registerDefaultRights(),
                                  iterateResourcePermissions(), modelFiltersForPermissions())
        
    @ioc.after(updateAssemblyGatewaysForResources)
    def updateAssemblyGatewaysForPersistenceResources():
        assemblyGateways().add(gatewaysPersistenceFromPermissions(), before=gatewaysFromPermissions())

    root_uri = ioc.entityOf(nameInEntity(GatewaysFromPermissions, 'root_uri_resources'), module=patch_ally_core)
    ioc.doc(root_uri, '''
        !Attention, this is automatically set to the server resources root. 
        ''')
    
    @ioc.before(root_uri, auto=False)
    def root_uri_force():
        support.force(root_uri, root_uri_resources())
    
    @ioc.start  # The update needs to be on start event since the resource assembly id from setup context 
    def updateAssemblyResourcesForInvokingFilter():
        assemblyResources().add(invokingFilter(), before=invoking())
