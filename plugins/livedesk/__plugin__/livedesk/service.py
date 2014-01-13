'''
Created on Jan 9, 2012

@package: livedesk
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Contains the services for livedesk.
'''

from ..cdm import contentDeliveryManager
from ..plugin.registry import addService
from ..superdesk.db_superdesk import bindSuperdeskSession, \
    bindSuperdeskValidations
from ally.cdm.spec import ICDM
from ally.container import support, bind, ioc, app
from ally.internationalization import NC_
from itertools import chain
from livedesk.core.spec import IBlogCollaboratorGroupCleanupService
from livedesk.impl.blog_collaborator import CollaboratorSpecification
from sched import scheduler
from threading import Thread
import time

# --------------------------------------------------------------------

SERVICES = 'livedesk.api.**.I*Service'
@ioc.entity
def binders(): return [bindSuperdeskSession]
@ioc.entity
def bindersService(): return list(chain((bindSuperdeskValidations,), binders()))

bind.bindToEntities('livedesk.impl.**.*Alchemy', IBlogCollaboratorGroupCleanupService, binders=binders)
support.createEntitySetup('livedesk.impl.**.*')
support.listenToEntities(SERVICES, listeners=addService(bindersService))
support.loadAllEntities(SERVICES)

# --------------------------------------------------------------------

@ioc.entity
def blogThemeCDM() -> ICDM: return contentDeliveryManager()

# --------------------------------------------------------------------

@ioc.entity
def collaboratorSpecification() -> CollaboratorSpecification:
    b = CollaboratorSpecification()
    b.collaborator_types = [NC_('collaborator type', 'Collaborator'), NC_('collaborator type', 'Administrator')]
    return b

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
