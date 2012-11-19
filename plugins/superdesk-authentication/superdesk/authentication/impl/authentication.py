'''
Created on Sep 3, 2012

@package: superdesk authentication
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

The superdesk authentication implementation.
'''

from ..api.authentication import IAuthenticationService, Authentication
from ally.api.operator.authentication.service import IAuthenticationSupport
from ally.api.type import typeFor, Type
from ally.container import wire
from ally.container.ioc import injected
from ally.container.support import setup
from ally.exception import InputError, Ref, DevelError
from ally.internationalization import _
from ally.support.sqlalchemy.session import SessionSupport, commitNow
from ally.support.sqlalchemy.util_service import handle
from datetime import timedelta
from os import urandom
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.sql.functions import current_timestamp
from superdesk.authentication.core.spec import ICleanupService
from superdesk.authentication.meta.authentication import LoginMapped, \
    TokenMapped
from superdesk.user.api.user import User
from superdesk.user.meta.user import UserMapped
import hashlib
import hmac
import logging

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

class IAuthenticationCompoundService(IAuthenticationService, IAuthenticationSupport, ICleanupService):
    '''
    Compound specification class formed from the authentication specifications.
    '''

@injected
@setup(IAuthenticationCompoundService)
class AuthenticationServiceAlchemy(SessionSupport, IAuthenticationCompoundService):
    '''
    The service implementation that provides the authentication.
    '''

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
        assert isinstance(self.authentication_token_size, int), 'Invalid token size %s' % self.authentication_token_size
        assert isinstance(self.session_token_size, int), 'Invalid session token size %s' % self.session_token_size
        assert isinstance(self.authentication_timeout, int), \
        'Invalid authentication timeout %s' % self.authentication_timeout
        assert isinstance(self.session_timeout, int), 'Invalid session timeout %s' % self.session_timeout

        self.authenticationTimeOut = timedelta(seconds=self.authentication_timeout)
        self.sessionTimeOut = timedelta(seconds=self.session_timeout)

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
        olderThan -= self.authenticationTimeOut
        sql = self.session().query(TokenMapped)
        sql = sql.filter(TokenMapped.Token == authentication.Token)
        sql = sql.filter(TokenMapped.requestedOn > olderThan)
        if sql.delete() > 0:
            commitNow() # We make sure that the delete has been performed

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

    def authenticate(self, identifier, attributes, arguments):
        '''
        @see: IAuthenticationSupport.authenticate
        '''
        assert isinstance(identifier, str), 'Invalid identifier %s' % identifier
        assert isinstance(attributes, dict), 'Invalid attributes %s' % attributes
        assert isinstance(arguments, dict), 'Invalid arguments %s' % arguments

        olderThan = self.session().query(current_timestamp()).scalar()
        olderThan -= self.sessionTimeOut
        sql = self.session().query(LoginMapped)
        sql = sql.filter(LoginMapped.Session == identifier)
        sql = sql.filter(LoginMapped.AccessedOn > olderThan)
        try: login = sql.one()
        except NoResultFound: return False
        assert isinstance(login, LoginMapped), 'Invalid login %s' % login
        login.AccessedOn = current_timestamp()
        self.session().flush((login,))
        self.session().expunge(login)
        commitNow()
        # We need to fore the commit because if there is an exception while processing the request we need to make
        # sure that the last access has been updated.

        for authType in arguments:
            assert isinstance(authType, Type), 'Invalid type %s' % authType

            if authType == typeFor(User.Id): arguments[authType] = login.User
            else: raise DevelError('Invalid authenticated type %s' % authType)

        return True

    # ----------------------------------------------------------------

    def cleanExpired(self):
        '''
        @see: ICleanupService.cleanExpired
        '''
        olderThan = self.session().query(current_timestamp()).scalar()

        # Cleaning the expired tokens.
        sql = self.session().query(TokenMapped)
        sql = sql.filter(TokenMapped.requestedOn <= olderThan - self.authenticationTimeOut)
        deleted = sql.delete()
        assert log.debug('Cleaned \'%s\' expired authentication requests', deleted) or True

        # Cleaning the expired sessions.
        sql = self.session().query(LoginMapped)
        sql = sql.filter(LoginMapped.AccessedOn <= olderThan - self.sessionTimeOut)
        deleted = sql.delete()
        assert log.debug('Cleaned \'%s\' expired sessions', deleted) or True
