'''
Created on April 29, 2013

@package: frontline
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Martin Saturka

Contains the services for frontline.
'''

from ..plugin.registry import addService
from ..superdesk.db_superdesk import bindSuperdeskSession, \
    bindSuperdeskValidations
from ally.container import support, bind, ioc
from itertools import chain

# --------------------------------------------------------------------

SERVICES = 'frontline.*.api.**.I*Service'
@ioc.entity
def binders(): return [bindSuperdeskSession]
@ioc.entity
def bindersService(): return list(chain((bindSuperdeskValidations,), binders()))

bind.bindToEntities('frontline.*.impl.**.*Alchemy', binders=binders)
support.createEntitySetup('frontline.*.impl.**.*')
support.listenToEntities(SERVICES, listeners=addService(bindersService))
support.loadAllEntities(SERVICES)

# --------------------------------------------------------------------
