'''
Created on Sep 3, 2012

@package: superdesk authentication
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

The API specifications for the user authentication.
'''

from ally.api.config import service, call, INSERT
from datetime import datetime
from superdesk.api.domain_superdesk import modelSuperDesk
from superdesk.user.api.user import User

# --------------------------------------------------------------------

@modelSuperDesk(name='Authentication', id='Token')
class Token:
    '''
    Model for the authentication request.
    '''
    Token = str

@modelSuperDesk
class Authentication(Token):
    '''
    Model for the authentication data.
    '''
    HashedToken = str
    UserName = str

@modelSuperDesk(id='Session')
class Login:
    '''
    The login model.
    '''
    Session = str
    User = User
    CreatedOn = datetime
    AccessedOn = datetime

# --------------------------------------------------------------------

@service
class IAuthenticationService:
    '''
    The service that provides the authentication.
    '''

    @call(method=INSERT)
    def requestLogin(self) -> Token:
        '''
        Create a token in order to authenticate.
        '''

    @call(method=INSERT)
    def performLogin(self, authentication:Authentication) -> Login:
        '''
        Called in order to authenticate
        '''
