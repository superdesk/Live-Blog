'''
Created on Mar 14, 2013

@package: content publisher
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mugur Rus

Contains the services for content publisher.
'''

from ..plugin.registry import addService
from ..superdesk.db_superdesk import bindSuperdeskSession, bindSuperdeskValidations
from ally.container import support, bind, ioc
from itertools import chain

# --------------------------------------------------------------------

SERVICES = 'content.publisher.api.**.I*Service'
@ioc.entity
def binders(): return [bindSuperdeskSession]
@ioc.entity
def bindersService(): return list(chain((bindSuperdeskValidations,), binders()))

bind.bindToEntities('content.publisher.impl.**.*Alchemy', binders=binders)
support.createEntitySetup('content.publisher.impl.**.*')
support.listenToEntities(SERVICES, listeners=addService(bindersService))
support.loadAllEntities(SERVICES)