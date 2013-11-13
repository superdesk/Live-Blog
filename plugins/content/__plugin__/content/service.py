'''
Created on Nov 7, 2013

@package: content
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mugur Rus

Contains the services for content plugins.
'''

from ally.container import support, bind, ioc
from content.base.api.item import IItemService
from content.base.core.spec import IItemHandler
from content.base.impl.item import ItemHandlersSetup

from ..plugin.registry import registerService
from .database import binders


# --------------------------------------------------------------------
SERVICES = 'content.*.api.**.I*Service'

bind.bindToEntities('content.*.impl.**.*Alchemy', binders=binders)
support.createEntitySetup('content.*.impl.**.*')
support.listenToEntities(SERVICES, listeners=registerService)
support.loadAllEntities(SERVICES)

# --------------------------------------------------------------------

bind.bindToEntities('content.*.core.impl.**.*Alchemy', binders=binders)
support.createEntitySetup('content.*.core.impl.**.*')

# --------------------------------------------------------------------

@ioc.entity
def itemHandlers() -> list: return support.entitiesFor(IItemHandler)

@ioc.entity
def itemBase() -> IItemService:
    return support.entityFor(ItemHandlersSetup).createService()

# --------------------------------------------------------------------