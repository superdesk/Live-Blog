'''
Created on Jan 9, 2012

@package: superdesk
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Contains the services for superdesk.
'''

from ..plugin.registry import registerService
from .database import binders
from ally.container import support, bind

# --------------------------------------------------------------------

SERVICES = 'superdesk.*.api.**.I*Service'

bind.bindToEntities('superdesk.*.impl.**.*Alchemy', binders=binders)
support.createEntitySetup('superdesk.*.impl.**.*')
support.listenToEntities(SERVICES, listeners=registerService)
support.loadAllEntities(SERVICES)
