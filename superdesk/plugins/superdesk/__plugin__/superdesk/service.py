'''
Created on Jan 9, 2012

@package: superdesk
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Contains the services for superdesk.
'''

from ..ally_authentication_http.authentication import registerAuthentication
from ..plugin.registry import addService
from .db_superdesk import bindSuperdeskSession, bindSuperdeskValidations
from ally.api.operator.authentication.service import IAuthenticationSupport
from ally.container import support

# --------------------------------------------------------------------

API, IMPL = 'superdesk.*.api.**.I*Service', 'superdesk.*.impl.**.*'

support.createEntitySetup(API, IMPL)
support.bindToEntities(IMPL, binders=bindSuperdeskSession)
support.listenToEntities(IMPL, listeners=addService(bindSuperdeskSession, bindSuperdeskValidations))
support.listenToEntities(IAuthenticationSupport, listeners=registerAuthentication, beforeBinding=False)
support.loadAllEntities(API)

# --------------------------------------------------------------------
