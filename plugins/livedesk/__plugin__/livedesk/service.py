'''
Created on Jan 9, 2012

@package: livedesk
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Contains the services for livedesk.
'''

from ally.cdm.spec import ICDM
from ally.container import support, bind, ioc, app
from livedesk.core.spec import IBlogCollaboratorGroupCleanupService
from sched import scheduler
from threading import Thread
import time
from ..plugin.registry import registerService
from ..superdesk.database import binders
from ..cdm.service import contentDeliveryManager

# --------------------------------------------------------------------

SERVICES = 'livedesk.api.**.I*Service'

bind.bindToEntities('livedesk.impl.**.*Alchemy', IBlogCollaboratorGroupCleanupService, binders=binders)
support.createEntitySetup('livedesk.impl.**.*')
support.listenToEntities(SERVICES, listeners=registerService)
support.loadAllEntities(SERVICES)

# --------------------------------------------------------------------

@ioc.entity
def blogThemeCDM() -> ICDM: return contentDeliveryManager()

# --------------------------------------------------------------------

@ioc.config
def perform_group_cleanup() -> bool:
    '''
    True if blog collaborator groups should be cleaned.
    '''
    return True

# --------------------------------------------------------------------

@ioc.config
def cleanup_group_timeout() -> int:
    '''
    The number of seconds at which to run the cleanup for blog collaborator groups.
    '''
    return 600

# --------------------------------------------------------------------

@app.deploy
def cleanup():
    if not perform_group_cleanup(): return
    timeout, cleanup = cleanup_group_timeout(), support.entityFor(IBlogCollaboratorGroupCleanupService)

    schedule = scheduler(time.time, time.sleep)
    def executeCleanup():
        assert isinstance(cleanup, IBlogCollaboratorGroupCleanupService)
        cleanup.cleanExpired()
        schedule.enter(timeout, 1, executeCleanup, ())

    schedule.enter(timeout, 1, executeCleanup, ())
    scheduleRunner = Thread(name='Cleanup blog collaborator groups thread', target=schedule.run)
    scheduleRunner.daemon = True
    scheduleRunner.start()
