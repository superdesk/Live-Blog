'''
Created on Jan 9, 2012

@@package: development support
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Contains the services for the development support.
'''

from ally.container import ioc
from ally.container.support import entityFor
from development.request.api.request import IRequestService

# --------------------------------------------------------------------

@ioc.entity
def requestService() -> IRequestService:
    import ally_deploy_application
    return entityFor(IRequestService, ally_deploy_application.assembly)
