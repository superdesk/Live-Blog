'''
Created on April 29, 2013

@package: frontline
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Martin Saturka

Contains the services for frontline.
'''

from ..plugin.registry import registerService
from ally.container import support, bind
from ..superdesk.database import binders

# --------------------------------------------------------------------

SERVICES = 'frontline.*.api.**.I*Service'

bind.bindToEntities('frontline.*.impl.**.*Alchemy', binders=binders)
support.createEntitySetup('frontline.*.impl.**.*')
support.listenToEntities(SERVICES, listeners=registerService)
support.loadAllEntities(SERVICES)
