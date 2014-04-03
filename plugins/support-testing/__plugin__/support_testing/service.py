'''
Created on April 1, 2014

@package: support testing
@copyright: 2014 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Ioan v. Pocol

Contains the service setups.
'''

from ally.container import support, ioc, bind
from __plugin__.superdesk.db_superdesk import bindSuperdeskSession,\
    bindSuperdeskValidations
from itertools import chain    
from __plugin__.plugin.registry import addService

# --------------------------------------------------------------------

@ioc.entity
def binders(): return [bindSuperdeskSession]

@ioc.entity
def bindersService(): return list(chain((bindSuperdeskValidations,), binders()))

SERVICES = 'support_testing.api.**.I*Service'
bind.bindToEntities('support_testing.impl.**.*Service', binders=binders)
support.createEntitySetup('support_testing.impl.**.*')
support.listenToEntities(SERVICES, listeners=addService(bindersService))
support.loadAllEntities(SERVICES)


# --------------------------------------------------------------------

