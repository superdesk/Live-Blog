'''
Created on Feb 19, 2013

@package: superdesk security
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the ally core http setup patch.
'''

from .service import assemblyGateways, userRbacProvider, rbacPopulateRights, \
    registerDefaultRights
from ally.container import ioc, support
from ally.design.processor.assembly import Assembly
from ally.design.processor.handler import Handler
from ally.design.processor.processor import restructure
import logging

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

try: from __setup__ import ally_core_http
except ImportError: log.info('No ally core http component available, thus cannot populate configurations and processors')
else:
    ally_core_http = ally_core_http  # Just to avoid the import warning
    # ----------------------------------------------------------------
    
    from .patch_ally_core import gatewaysFromPermissions, updateAssemblyGatewaysForResources, \
        iterateResourcePermissions, modelFiltersForPermissions, alternateNavigationPermissions, userValueForFilter, \
        alternateNavigationPermissions
    from __setup__.ally_core_http.processor import assemblyResources, encoderPathResource
    from __setup__.ally_core.processor import invoking
    from superdesk.security.core.impl.processor import user_persistence_filter
    
    userPersistenceForPermissions = invokingFilter = support.notCreated  # Just to avoid errors
    support.createEntitySetup(user_persistence_filter)
    
    # --------------------------------------------------------------------
    
    @ioc.entity
    def encoderPathGateway() -> Handler:
        return restructure(encoderPathResource(), ('response', 'solicitation'), ('request', 'solicitation'))
    
    @ioc.entity
    def assemblyPermissions() -> Assembly:
        ''' Assembly used for creating resource permissions'''
        return Assembly('Resource permissions')
        
    # --------------------------------------------------------------------
        
    @ioc.before(assemblyPermissions)
    def updateAssemblyPermissions():
        assemblyPermissions().add(userRbacProvider(), rbacPopulateRights(), registerDefaultRights(), iterateResourcePermissions(),
                                  userValueForFilter(), alternateNavigationPermissions(), modelFiltersForPermissions())
        
    @ioc.after(updateAssemblyGatewaysForResources)
    def updateAssemblyGatewaysForHTTPResources():
        assemblyGateways().add(userPersistenceForPermissions(), before=gatewaysFromPermissions())
        assemblyGateways().add(encoderPathGateway(), before=alternateNavigationPermissions())
    
    @ioc.start  # The update needs to be on start event since the resource assembly id from setup context 
    def updateAssemblyResourcesForInvokingFilter():
        assemblyResources().add(invokingFilter(), before=invoking())
