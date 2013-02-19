'''
Created on Sep 9, 2012

@package: superdesk security
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Contains the services setups for superdesk security.
'''

from ally.container import ioc, support, app
from sched import scheduler
from superdesk.security.core.impl.gateways_filter import RegisterDefaultGateways, \
    PopulateMethodOverride
from superdesk.security.core.spec import ICleanupService
from threading import Thread
import time

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

@ioc.config
def default_authenticated_gateways():
    '''
    The default authenticated gateways that are available for any user as long as it is authenticated.
    This structure is the same as the one in 'default_gateways' configuration.
    '''
    return []

# --------------------------------------------------------------------

@ioc.entity
def gatewaysFilters() -> list:
    ''' The gateway filters that will be used by the authentication service'''
    return []

@ioc.entity
def defaultAuthenticatedGateways(): return RegisterDefaultGateways(default_authenticated_gateways())

@ioc.entity
def populateMethodOverrideGateways(): return PopulateMethodOverride()

# --------------------------------------------------------------------

@ioc.before(gatewaysFilters)
def updateGatewaysFilters():
    gatewaysFilters().append(populateMethodOverrideGateways())
    gatewaysFilters().append(defaultAuthenticatedGateways())

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

