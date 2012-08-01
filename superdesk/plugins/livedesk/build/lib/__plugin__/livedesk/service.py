'''
Created on Jan 9, 2012

@package: livedesk
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Contains the services for livedesk.
'''

from ..plugin.registry import addService
from ally.container import support
from ..superdesk.db_superdesk import bindSuperdeskSession, bindSuperdeskValidations

# --------------------------------------------------------------------

API, IMPL = 'livedesk.api.**.I*Service', 'livedesk.impl.**.*'

support.createEntitySetup(API, IMPL)
support.bindToEntities(IMPL, binders=bindSuperdeskSession)
support.listenToEntities(IMPL, listeners=addService(bindSuperdeskSession, bindSuperdeskValidations))
support.loadAllEntities(API)

# --------------------------------------------------------------------
