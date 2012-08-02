'''
Created on Sep 9, 2012

@package: superdesk authentication
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Contains the services setups for superdesk authentication.
'''

from ..superdesk.db_superdesk import createTables
from ally.container import ioc, support
from sched import scheduler
import time
from superdesk.authentication.core.spec import ICleanupService
from superdesk.authentication.api.authentication import IAuthenticationService
from threading import Thread

# --------------------------------------------------------------------

@ioc.config
def cleanup_timeout() -> int:
    '''
    The number of seconds at which to run the cleanup for sessions and authentications.
    '''
    return 10

# --------------------------------------------------------------------

@ioc.after(createTables)
def cleanup():
    timeout, cleanup = cleanup_timeout(), support.entityFor(IAuthenticationService)
    # TODO: fix this after merge with devel

    schedule = scheduler(time.time, time.sleep)
    def executeCleanup():
        assert isinstance(cleanup, ICleanupService)
        cleanup.cleanExpired()
        schedule.enter(timeout, 1, executeCleanup, ())

    schedule.enter(timeout, 1, executeCleanup, ())
    Thread(target=schedule.run, name='Cleanup authentications/sessions thread').start()
