'''
Created on July 10, 2012

@package: ally authentication
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mugur Rus

Provides authentication register function.
'''

# --------------------------------------------------------------------

from ally.container import ioc
from __plugin__.ally_authentication_http.authentication import registerAuthentication
from superdesk.user.api.user import IUserService
from ..superdesk import service
from superdesk.user.impl.user import UserServiceAlchemy

# --------------------------------------------------------------------

@ioc.replace(ioc.getEntity(IUserService, service))
def userService() -> IUserService:
    b = UserServiceAlchemy()

    return b

# --------------------------------------------------------------------

@ioc.start
def register():
    registerAuthentication(userService())
