'''
Created on April 26, 2013

@package: livedesk
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mugur Rus

Contains the services for livedesk sync.
'''

from ..plugin.registry import addService
from ..superdesk.db_superdesk import bindSuperdeskSession, bindSuperdeskValidations
from ally.container import support, bind, ioc
from itertools import chain
from livedesk.core.spec import IBlogCollaboratorGroupCleanupService

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
