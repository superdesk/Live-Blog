'''
Created on Sep 9, 2012

@package: superdesk security
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Contains the services setups for superdesk security.
'''

from ..gateway.service import gatewayMethodMerge, registerMethodOverride
from ..gateway_acl.service import registerPermissionGateway, rootURI
from ..security.service import signaturesRight
from acl.core.impl.processor.gateway.acl_permission import \
    RegisterAclPermissionHandler
from acl.core.impl.processor.gateway.compensate import \
    RegisterCompensatePermissionHandler
from acl.core.spec import IAclPermissionProvider, signature, ICompensateProvider
from ally.container import ioc, support, app
from ally.container.support import entityFor
from ally.design.processor.assembly import Assembly
from ally.design.processor.handler import Handler
from sched import scheduler
from security.api.right import IRightService
from superdesk.security.api.user_rbac import IUserRbacService
from superdesk.security.core.impl.processor import gateway
from superdesk.security.core.spec import ICleanupService, AUTHENTICATED_MARKER
from superdesk.user.api.user import User
from threading import Thread
import time

# --------------------------------------------------------------------

# The gateway processors
userInject = support.notCreated  # Just to avoid errors

support.createEntitySetup(gateway)

# --------------------------------------------------------------------

@ioc.config
def cleanup_timeout() -> int:
    '''
    The number of seconds at which to run the cleanup for sessions and authentications.
    '''
    return 180

# --------------------------------------------------------------------

@ioc.entity
def assemblyUserGateways() -> Assembly:
    ''' Assembly used for creating the users gateways'''
    return Assembly('Users gateways')

# --------------------------------------------------------------------

@ioc.entity
def aclPermissionRightsProvider() -> IAclPermissionProvider: return entityFor(IRightService)

@ioc.entity
def compensateRightsProvider() -> ICompensateProvider: return entityFor(IRightService)

@ioc.entity
def registerAclPermission() -> Handler:
    b = RegisterAclPermissionHandler()
    b.aclPermissionProvider = entityFor(IUserRbacService)
    return b

@ioc.entity
def registerCompensatePermission() -> Handler:
    b = RegisterCompensatePermissionHandler()
    b.compensateProvider = entityFor(IUserRbacService)
    return b

# --------------------------------------------------------------------

@ioc.before(signaturesRight)
def updateSignaturesRight():
    signaturesRight()[signature(User.Id)] = AUTHENTICATED_MARKER

@ioc.after(assemblyUserGateways)
def updateAssemblyUserGateways():
    assemblyUserGateways().add(userInject(), rootURI(), registerAclPermission(), registerCompensatePermission(),
                               registerPermissionGateway(), gatewayMethodMerge(), registerMethodOverride())

# --------------------------------------------------------------------

@app.deploy(app.NORMAL)
def cleanup():
    ''' Start the cleanup process for authentications/sessions'''
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

