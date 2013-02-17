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

@app.deploy
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

