'''
Created on Sep 3, 2012

@package: superdesk security
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

The superdesk authentication implementation.
'''

from ..api.authentication import IAuthenticationService, Authentication
from acl.gateway.core.spec import IGatewayAclService, IAuthenticatedProvider
from acl.spec import Acl
from ally.api.operator.type import TypeProperty
from ally.container import wire
from ally.container.ioc import injected
from ally.container.support import setup
from ally.core.spec.resources import Node
from ally.exception import InputError, Ref
from ally.internationalization import _
from ally.support.sqlalchemy.session import SessionSupport, commitNow
from ally.support.sqlalchemy.util_service import handle
from datetime import timedelta
from os import urandom
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.sql.functions import current_timestamp
from superdesk.security.api.authentication import Login
from superdesk.security.api.user_rbac import IUserRbacService
from superdesk.security.core.spec import ICleanupService
from superdesk.security.meta.authentication import LoginMapped, TokenMapped
from superdesk.user.api.user import User
from superdesk.user.meta.user import UserMapped
import hashlib
import hmac
import logging

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

@injected
@setup(IAuthenticationService, ICleanupService)
class AuthenticationServiceAlchemy(SessionSupport, IAuthenticationService, ICleanupService):
    '''
    The service implementation that provides the authentication.
    '''

    gatewayAclService = IGatewayAclService; wire.entity('gatewayAclService')
    # The acl gateway service used for constructing the gateways
    acl = Acl; wire.entity('acl')
    # The acl repository.
    resourcesRoot = Node; wire.entity('resourcesRoot')
    # The root node to process the acl rights against.
    userRbacService = IUserRbacService; wire.entity('userRbacService')
    # The user rbac service.
    
    authentication_token_size = 5; wire.config('authentication_token_size', doc='''
    The number of characters that the authentication token should have.
    ''')
    session_token_size = 5; wire.config('session_token_size', doc='''
    The number of characters that the authentication token should have.
    ''')
    authentication_timeout = 10; wire.config('authentication_timeout', doc='''
    The number of seconds after which the login token expires.
    ''')
    session_timeout = 3600; wire.config('session_timeout', doc='''
    The number of seconds after which the session expires.
    ''')

    def __init__(self):
        '''
        Construct the authentication service.
        '''
        assert isinstance(self.gatewayAclService, IGatewayAclService), 'Invalid acl gateway service %s' % self.gatewayAclService
        assert isinstance(self.acl, Acl), 'Invalid acl repository %s' % self.acl
        assert isinstance(self.resourcesRoot, Node), 'Invalid root node %s' % self.resourcesRoot
        assert isinstance(self.userRbacService, IUserRbacService), 'Invalid user rbac service %s' % self.userRbacService
        assert isinstance(self.authentication_token_size, int), 'Invalid token size %s' % self.authentication_token_size
        assert isinstance(self.session_token_size, int), 'Invalid session token size %s' % self.session_token_size
        assert isinstance(self.authentication_timeout, int), \
        'Invalid authentication timeout %s' % self.authentication_timeout
        assert isinstance(self.session_timeout, int), 'Invalid session timeout %s' % self.session_timeout

        self._authenticationTimeOut = timedelta(seconds=self.authentication_timeout)
        self._sessionTimeOut = timedelta(seconds=self.session_timeout)

    def authenticate(self, session):
        '''
        @see: IAuthenticationService.authenticate
        '''
        # TODO: uncomment
#        olderThan = self.session().query(current_timestamp()).scalar()
#        olderThan -= self._sessionTimeOut
#        sql = self.session().query(LoginMapped)
#        sql = sql.filter(LoginMapped.Session == session)
#        sql = sql.filter(LoginMapped.AccessedOn > olderThan)
#        try: login = sql.one()
#        except NoResultFound: raise InputError(Ref(_('Invalid session'), ref=Login.Session))
#        assert isinstance(login, LoginMapped), 'Invalid login %s' % login
#        login.AccessedOn = current_timestamp()
#        self.session().flush((login,))
#        self.session().expunge(login)
#        commitNow()
        # We need to fore the commit because if there is an exception while processing the request we need to make
        # sure that the last access has been updated.
        userId = int(session)
        
        rights = (right.Name for right in self.userRbacService.getRights(userId))  # login.User
        rights = self.acl.activeRightsFor(self.resourcesRoot, rights)
        return self.gatewayAclService.gatewaysFor(rights, UserProvider(str(userId)))
        
    def requestLogin(self):
        '''
        @see: IAuthenticationService.requestLogin
        '''
        hash = hashlib.sha512()
        hash.update(urandom(self.authentication_token_size))

        token = TokenMapped()
        token.Token = hash.hexdigest()
        token.requestedOn = current_timestamp()

        try: self.session().add(token)
        except SQLAlchemyError as e: handle(e, token)

        return token

    def performLogin(self, authentication):
        '''
        @see: IAuthenticationService.performLogin
        '''
        assert isinstance(authentication, Authentication), 'Invalid authentication %s' % authentication

        if authentication.Token is None:
            raise InputError(Ref(_('The login token is required'), ref=Authentication.Token))
        if authentication.HashedToken is None:
            raise InputError(Ref(_('The hashed login token is required'), ref=Authentication.HashedToken))
        if authentication.UserName is None:
            raise InputError(Ref(_('A user name is required for authentication'), ref=Authentication.UserName))

        olderThan = self.session().query(current_timestamp()).scalar()
        olderThan -= self._authenticationTimeOut
        sql = self.session().query(TokenMapped)
        sql = sql.filter(TokenMapped.Token == authentication.Token)
        sql = sql.filter(TokenMapped.requestedOn > olderThan)
        if sql.delete() > 0:
            commitNow()  # We make sure that the delete has been performed

            try: user = self.session().query(UserMapped).filter(UserMapped.Name == authentication.UserName).filter(UserMapped.DeletedOn == None).one()
            except NoResultFound: user = None

            if user is not None:
                assert isinstance(user, UserMapped), 'Invalid user %s' % user

                hashedToken = hmac.new(bytes(user.Name, 'utf8'),
                                       bytes(user.password, 'utf8'), hashlib.sha512).hexdigest()
                hashedToken = hmac.new(bytes(hashedToken, 'utf8'),
                                       bytes(authentication.Token, 'utf8'), hashlib.sha512).hexdigest()

                if authentication.HashedToken == hashedToken:
                    hash = hashlib.sha512()
                    hash.update(urandom(self.authentication_token_size))

                    login = LoginMapped()
                    login.Session = hash.hexdigest()
                    login.User = user.Id
                    login.CreatedOn = login.AccessedOn = current_timestamp()

                    try: self.session().add(login)
                    except SQLAlchemyError as e: handle(e, login)

                    return login

        raise InputError(_('Invalid credentials'))

    # ----------------------------------------------------------------

    def cleanExpired(self):
        '''
        @see: ICleanupService.cleanExpired
        '''
        olderThan = self.session().query(current_timestamp()).scalar()

        # Cleaning the expired tokens.
        sql = self.session().query(TokenMapped)
        sql = sql.filter(TokenMapped.requestedOn <= olderThan - self._authenticationTimeOut)
        deleted = sql.delete()
        assert log.debug('Cleaned \'%s\' expired authentication requests', deleted) or True

        # Cleaning the expired sessions.
        sql = self.session().query(LoginMapped)
        sql = sql.filter(LoginMapped.AccessedOn <= olderThan - self._sessionTimeOut)
        deleted = sql.delete()
        assert log.debug('Cleaned \'%s\' expired sessions', deleted) or True

# --------------------------------------------------------------------

class UserProvider(IAuthenticatedProvider):
    '''
    Implementation for @see: IAuthenticatedProvider that provides the authenticated user id.
    '''
    __slots__ = ('userId',)
    
    def __init__(self, userId):
        '''
        Construct the provider for the user id.
        
        @param userId: string
            The user id.
        '''
        assert isinstance(userId, str), 'Invalid user id %s' % userId
        self.userId = userId
    
    def valueFor(self, propertyType):
        '''
        @see: IAuthenticatedProvider.valueFor
        '''
        assert isinstance(propertyType, TypeProperty), 'Invalid property type %s' % propertyType
        if propertyType.parent.clazz == User or issubclass(propertyType.parent.clazz, User): return self.userId
        
