'''
Created on Sep 9, 2012

@package: superdesk security
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Contains the services setups for superdesk security.
'''

from acl.core.impl.processor import default_right
from ally.container import ioc, support, app
from ally.design.processor.assembly import Assembly
from gateway.core.impl.processor import method_override_gateway
from sched import scheduler
from security.rbac.core.impl.processor import rbac_right
from superdesk.security.core.impl.processor import user_rbac_provider, \
    user_filter_value
from superdesk.security.core.spec import ICleanupService
from superdesk.security.impl.filter_authenticated import \
    AuthenticatedFilterService
from threading import Thread
import time

# --------------------------------------------------------------------

userRbacProvider = userValueForFilter = registerMethodOverride = rbacPopulateRights = \
registerDefaultRights = support.notCreated  # Just to avoid errors
support.createEntitySetup(user_rbac_provider, user_filter_value, method_override_gateway, rbac_right, default_right)

# --------------------------------------------------------------------

@ioc.config
def cleanup_timeout() -> int:
    '''
    The number of seconds at which to run the cleanup for sessions and authentications.
    '''
    return 180

# --------------------------------------------------------------------

@ioc.entity
def equaliltyUserFilterClasses() -> list:
    ''' The @see: IAclFilter classes that checks if the authenticated identifier is same with the resource identifier'''
    return [AuthenticatedFilterService]

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
    assemblyGateways().add(userRbacProvider(), rbacPopulateRights(), registerDefaultRights(), registerMethodOverride())
   
@ioc.before(assemblyActiveRights)
def updateAssemblyActiveRights():
    assemblyActiveRights().add(userRbacProvider(), rbacPopulateRights(), registerDefaultRights())

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

