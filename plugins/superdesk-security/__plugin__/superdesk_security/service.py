'''
Created on Sep 9, 2012

@package: superdesk security
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Contains the services setups for superdesk security.
'''

from acl.core.impl.processor.default_right import RegisterDefaultRights
from acl.core.impl.processor.method_override_gateway import \
    RegisterMethodOverride
from acl.core.impl.processor.rbac_right import RbacPopulateRights
from acl.core.impl.processor.resource_gateway import \
    GatewaysFromResourcePermissions
from acl.core.impl.processor.resource_node_associate import \
    RepositoryNodeService, IterateResourcePermissions, CheckResourceAvailableRights
from ally.container import ioc, support, app
from ally.design.processor.assembly import Assembly
from sched import scheduler
from superdesk.security.core.impl.processor.user_rbac_provider import \
    UserRbacProvider
from superdesk.security.core.spec import ICleanupService
from threading import Thread
import time

# --------------------------------------------------------------------

support.createEntitySetup(UserRbacProvider, RbacPopulateRights, RegisterDefaultRights, IterateResourcePermissions,
                          GatewaysFromResourcePermissions, RegisterMethodOverride, RepositoryNodeService,
                          CheckResourceAvailableRights)

global userRbacProvider, rbacPopulateRights, registerDefaultRights, iterateResourcePermissions, checkResourceAvailableRights, \
gatewaysFromResourcePermissions, registerMethodOverride

# --------------------------------------------------------------------

@ioc.config
def perform_cleanup() -> bool:
    '''
    True if the expired sessions and authentications should be cleaned.
    '''
    return True

@ioc.config
def cleanup_timeout() -> int:
    '''
    The number of seconds at which to run the cleanup for sessions and authentications.
    '''
    return 180

# --------------------------------------------------------------------

@ioc.entity
def assemblyGateways() -> Assembly:
    ''' Assembly used for creating the users gateways'''
    return Assembly('Users gateways')

@ioc.entity
def assemblyActiveRights() -> Assembly:
    ''' Assembly used for getting the users active rights'''
    return Assembly('Active rights')

# --------------------------------------------------------------------

@ioc.before(assemblyGateways)
def updateAssemblyGateways():
    assemblyGateways().add(userRbacProvider(), rbacPopulateRights(), registerDefaultRights(), iterateResourcePermissions(),
                           gatewaysFromResourcePermissions(), registerMethodOverride())
    
@ioc.before(assemblyActiveRights)
def updateAssemblyActiveRights():
    assemblyActiveRights().add(userRbacProvider(), rbacPopulateRights(), registerDefaultRights(),
                               checkResourceAvailableRights())

# --------------------------------------------------------------------

@app.deploy(app.NORMAL)
def cleanup():
    if not perform_cleanup(): return
    timeout, cleanup = cleanup_timeout(), support.entityFor(ICleanupService)

    schedule = scheduler(time.time, time.sleep)
    def executeCleanup():
        assert isinstance(cleanup, ICleanupService)
        cleanup.cleanExpired()
        schedule.enter(timeout, 1, executeCleanup, ())

    schedule.enter(timeout, 1, executeCleanup, ())
    scheduleRunner = Thread(name='Cleanup authentications/sessions thread', target=schedule.run)
    scheduleRunner.daemon = True
    scheduleRunner.start()

