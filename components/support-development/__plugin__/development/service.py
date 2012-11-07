'''
Created on Jan 9, 2012

@@package: development support
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Contains the services for the development support.
'''

from __setup__.development.service import publish_development, requestService
from ally.container import ioc
from ally.container.ioc import SetupError
from development.request.api.request import IRequestService

# --------------------------------------------------------------------

@ioc.entity
def requestService() -> IRequestService:
    try: import application
    except ImportError: raise SetupError('Cannot access the application module')
    ioc.activate(application.assembly)
    value = requestService()
    ioc.deactivate()
    return value

def publish_development():
    '''
    If true the development services will be published.
    '''
    try: import application
    except ImportError: raise SetupError('Cannot access the application module')
    ioc.activate(application.assembly)
    value = publish_development()
    ioc.deactivate()
    return value
