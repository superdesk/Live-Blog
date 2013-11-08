'''
Created on Nov 7, 2013

@package: content
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mugur Rus

Contains the services for content plugins.
'''

from ..plugin.registry import registerService
from .database import binders
from ally.container import support, bind

# --------------------------------------------------------------------

SERVICES = 'content.*.api.**.I*Service'

bind.bindToEntities('content.*.impl.**.*Alchemy', binders=binders)
support.createEntitySetup('content.*.impl.**.*')
support.listenToEntities(SERVICES, listeners=registerService)
support.loadAllEntities(SERVICES)
