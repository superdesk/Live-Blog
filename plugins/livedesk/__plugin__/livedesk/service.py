'''
Created on Jan 9, 2012

@package: livedesk
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Contains the services for livedesk.
'''

from ..cdm.local_cdm import contentDeliveryManager
from ..plugin.registry import addService
from ..superdesk.db_superdesk import bindSuperdeskSession, \
    bindSuperdeskValidations
from ally.container import support, ioc
from cdm.spec import ICDM
from livedesk.impl.blog_collaborator import CollaboratorSpecification
from ally.internationalization import NC_

# --------------------------------------------------------------------

SERVICES = 'livedesk.api.**.I*Service'

support.createEntitySetup('livedesk.impl.**.*')
support.bindToEntities('livedesk.impl.**.*Alchemy', binders=bindSuperdeskSession)
support.listenToEntities(SERVICES, listeners=addService(bindSuperdeskSession, bindSuperdeskValidations))
support.loadAllEntities(SERVICES)

# --------------------------------------------------------------------

@ioc.entity
def blogThemeCDM() -> ICDM: return contentDeliveryManager()

@ioc.entity
def collaboratorSpecification() -> CollaboratorSpecification:
    b = CollaboratorSpecification()
    b.collaborator_types = [NC_('collaborator type', 'Collaborator'), NC_('collaborator type', 'Administrator')]
    return b
