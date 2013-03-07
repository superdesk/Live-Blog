'''
Created on Sep 3, 2012

@package: superdesk security
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

The superdesk authentication implementation.
'''

from ..api.authentication import IAuthenticationService, Authentication
from acl.spec import Acl
from ally.container import wire
from ally.container.ioc import injected
from ally.container.support import setup
from ally.design.processor.assembly import Assembly
from ally.design.processor.attribute import defines, requires
from ally.design.processor.context import Context
from ally.design.processor.execution import Processing, Chain
from ally.exception import InputError, Ref
from ally.internationalization import _
from ally.support.sqlalchemy.session import SessionSupport, commitNow
from ally.support.sqlalchemy.util_service import handle
from collections import Iterable
from datetime import timedelta
from os import urandom
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.sql.functions import current_timestamp
from superdesk.security.api.authentication import Login
from superdesk.security.core.spec import ICleanupService
from superdesk.security.meta.authentication import LoginMapped, TokenMapped
from superdesk.user.meta.user import UserMapped
import hashlib
import hmac
import logging

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

class Solicitation(Context):
    '''
    The solicitation context.
    '''
    # ---------------------------------------------------------------- Defined
    userId = defines(int, doc='''
    @rtype: integer
    The id of the user to create gateways for.
    ''')
    types = defines(Iterable, doc='''
    @rtype: Iterable(TypeAcl)
    The ACL types to create gateways for.
    ''')

class Reply(Context):
    '''
    The reply context.
    '''
    # ---------------------------------------------------------------- Required
    gateways = requires(Iterable, doc='''
    @rtype: Iterable(Gateway)
    The generated gateways.
    ''')
    
# --------------------------------------------------------------------

@injected
@setup(IAuthenticationService, ICleanupService, name='authenticationService')
class AuthenticationServiceAlchemy(SessionSupport, IAuthenticationService, ICleanupService):
    '''
    The service implementation that provides the authentication.
    '''

    acl = Acl; wire.entity('acl')
    # The acl repository.
    assemblyGateways = Assembly; wire.entity('assemblyGateways')
    # The assembly to be used for generating gateways
    
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
        assert isinstance(self.acl, Acl), 'Invalid acl repository %s' % self.acl
        assert isinstance(self.assemblyGateways, Assembly), 'Invalid assembly gateways %s' % self.assemblyGateways
        assert isinstance(self.authentication_token_size, int), 'Invalid token size %s' % self.authentication_token_size
        assert isinstance(self.session_token_size, int), 'Invalid session token size %s' % self.session_token_size
        assert isinstance(self.authentication_timeout, int), \
        'Invalid authentication timeout %s' % self.authentication_timeout
        assert isinstance(self.session_timeout, int), 'Invalid session timeout %s' % self.session_timeout

        self._authenticationTimeOut = timedelta(seconds=self.authentication_timeout)
        self._sessionTimeOut = timedelta(seconds=self.session_timeout)
        self._processing = self.assemblyGateways.create(solicitation=Solicitation, reply=Reply)

    def authenticate(self, session):
        '''
        @see: IAuthenticationService.authenticate
        '''
        olderThan = self.session().query(current_timestamp()).scalar()
        olderThan -= self._sessionTimeOut
        sql = self.session().query(LoginMapped)
        sql = sql.filter(LoginMapped.Session == session)
        sql = sql.filter(LoginMapped.AccessedOn > olderThan)
        try: login = sql.one()
        except NoResultFound: raise InputError(Ref(_('Invalid session'), ref=Login.Session))
        assert isinstance(login, LoginMapped), 'Invalid login %s' % login
        login.AccessedOn = current_timestamp()
        self.session().flush((login,))
        self.session().expunge(login)
        commitNow()
        
        # We need to fore the commit because if there is an exception while processing the request we need to make
        # sure that the last access has been updated.
        proc = self._processing
        assert isinstance(proc, Processing), 'Invalid processing %s' % proc
        
        solicitation = proc.ctx.solicitation()
        assert isinstance(solicitation, Solicitation), 'Invalid solicitation %s' % solicitation
        solicitation.userId = login.User
        solicitation.types = self.acl.types
        
        chain = Chain(proc)
        chain.process(**proc.fillIn(solicitation=solicitation, reply=proc.ctx.reply())).doAll()
        
        reply = chain.arg.reply
        assert isinstance(reply, Reply), 'Invalid reply %s' % reply
        if Reply.gateways not in reply: return ()
        
        return sorted(reply.gateways, key=lambda gateway: (gateway.Pattern, gateway.Methods))
        
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

