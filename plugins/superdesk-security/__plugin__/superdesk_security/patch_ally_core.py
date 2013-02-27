'''
Created on Feb 26, 2013

@package: superdesk security
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the ally core setup patch.
'''

from .service import assemblyGateways, updateAssemblyGateways, \
    registerMethodOverride, updateAssemblyActiveRights, assemblyActiveRights, \
    registerDefaultRights
from ally.container import support, ioc
import logging

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

try: from __setup__ import ally_core
except ImportError: log.info('No ally core component available, thus cannot populate processors')
else:
    ally_core = ally_core  # Just to avoid the import warning
    # ----------------------------------------------------------------
    
    from acl.core.impl.processor import resource_node_associate, resource_model_filter, resource_gateway
    
    iterateResourcePermissions = checkResourceAvailableRights = modelFiltersForPermissions = \
    authenticatedForPermissions = gatewaysFromPermissions = support.notCreated  # Just to avoid errors
    support.createEntitySetup(resource_node_associate, resource_model_filter, resource_gateway)
    
    # --------------------------------------------------------------------
    
    @ioc.after(updateAssemblyGateways)
    def updateAssemblyGatewaysForResources():
        assemblyGateways().add(iterateResourcePermissions(), authenticatedForPermissions(), gatewaysFromPermissions(),
                               before=registerMethodOverride())
       
    @ioc.after(updateAssemblyActiveRights)
    def updateAssemblyActiveRightsForResources():
        assemblyActiveRights().add(checkResourceAvailableRights(), after=registerDefaultRights())
        
