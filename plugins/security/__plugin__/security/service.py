'''
Created on Jan 9, 2012

@package: security
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Contains the services for security.
'''
    
from ..plugin.registry import addService
from .db_security import bindSecuritySession, bindSecurityValidations
from ally.container import support, ioc, bind
from itertools import chain

# --------------------------------------------------------------------

SERVICES = 'security.api.**.I*Service', 'security.**.api.**.I*Service'
@ioc.entity
def binders(): return [bindSecuritySession]
@ioc.entity
def bindersService(): return list(chain((bindSecurityValidations,), binders()))

bind.bindToEntities('security.impl.**.*Alchemy', 'security.**.impl.**.*Alchemy', binders=binders)
support.createEntitySetup('security.impl.**.*', 'security.**.impl.**.*')
support.listenToEntities(*SERVICES, listeners=addService(bindersService))
support.loadAllEntities(*SERVICES)
