'''
Created on Jan 9, 2012

@package: superdesk
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Contains the services for superdesk.
'''

from ..plugin.registry import addService
from .db_superdesk import bindSuperdeskSession, bindSuperdeskValidations
from ally.container import support

# --------------------------------------------------------------------

SERVICES = 'superdesk.*.api.**.I*Service'

support.createEntitySetup('superdesk.*.impl.**.*')
support.bindToEntities('superdesk.*.impl.**.*Alchemy', binders=bindSuperdeskSession)
support.listenToEntities(SERVICES, listeners=addService(bindSuperdeskSession, bindSuperdeskValidations))
support.loadAllEntities(SERVICES)

# --------------------------------------------------------------------
