'''
Created on Mar 14, 2013

@package: content article
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: 

'''

from ..plugin.registry import addService
from ..superdesk.db_superdesk import bindSuperdeskSession, bindSuperdeskValidations
from ally.container import support, bind, ioc
from itertools import chain

# --------------------------------------------------------------------

SERVICES = 'content.desks.api.**.I*Service'
@ioc.entity
def binders(): return [bindSuperdeskSession]
@ioc.entity
def bindersService(): return list(chain((bindSuperdeskValidations,), binders()))

bind.bindToEntities('content.desks.impl.**.*Alchemy', binders=binders)
support.createEntitySetup('content.desks.impl.**.*')
support.listenToEntities(SERVICES, listeners=addService(bindersService))
support.loadAllEntities(SERVICES)
