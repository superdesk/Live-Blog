'''
Created on Jan 9, 2012

@@package: development support
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Contains the services for the development support.
'''

from ally.container import ioc
from development.request.api.request import IRequestService

# --------------------------------------------------------------------

@ioc.entity
def requestService() -> IRequestService:
    import ally_deploy_application
    ioc.activate(ally_deploy_application.assembly)
    from __setup__.development.service import requestService
    value = requestService()
    ioc.deactivate()
    return value

def publish_development():
    '''
    If true the development services will be published.
    '''
    import ally_deploy_application
    ioc.activate(ally_deploy_application.assembly)
    from __setup__.development.service import publish_development
    value = publish_development()
    ioc.deactivate()
    return value
