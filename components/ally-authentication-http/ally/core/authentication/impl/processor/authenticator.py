'''
Created on Aug 9, 2011

@package: ally authentication http
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the authentication header handling.
'''

from ally.api.operator.authentication.type import TypeAuthentication
from ally.container.ioc import injected
from ally.core.http.impl.processor.header import HeaderHTTPBase, VALUE_NO_PARSE
from ally.core.http.spec import RequestHTTP, INVALID_HEADER_VALUE, UNAUTHORIZED
from ally.core.spec.resources import Invoker
from ally.core.spec.server import Processor, ProcessorsChain, Response
from ally.exception import DevelError, InputError
import logging
from ally.core.impl.node import NodePath
from ally.core.impl.invoker import InvokerFunction
from ally.api.config import GET, INSERT
from ally.api.type import Input, typeFor, String
import hashlib
from datetime import datetime, timedelta
from ally.core.authentication.api.authentication import IAuthenticate
import hmac
from collections import deque
from os import urandom
from random import randint

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

class Session:
    '''
    Holds session data
    '''
    __slots__ = ('sessionId', 'userName', 'createTime', 'expireTime')

    def __init__(self, sessionId, userName, createTime, expireTime=None):
        self.sessionId = sessionId
        self.userName = userName
        self.createTime = createTime
        self.expireTime = expireTime

@injected
class AuthenticationHandler(HeaderHTTPBase, Processor):
    '''
    Provides the authentication handling.

    Provides on request: [arguments]
    Provides on response: NA

    Requires on request: headers, params, invoker
    Requires on response: NA
    '''

    sessionName = 'SessionId'
    # The header name for the session identifier.

    loginTokenTimeout = 5
    # The number of seconds after which the login token expires.

    userKeyGenerator = IAuthenticate
    # The implementation of IAuthenticate that permits the retrieval of the user secret key

    sessionTokenTimeout = 3600
    # The number of seconds after which the session expires.

    def __init__(self):
        super().__init__()
        assert isinstance(self.nameAuthentication, str), 'Invalid name authentication %s' % self.nameAuthentication
        node = NodePath(self.resourcesRegister.getRoot(), True, 'Authentication')
        node.get = InvokerFunction(GET, self.getLoginToken, typeFor(String),
                                   [
                                    Input('userName', typeFor(String)),
                                    ], {})
        node.post = InvokerFunction(INSERT, self.login, typeFor(String),
                                   [
                                    Input('userName', typeFor(String)),
                                    Input('loginToken', typeFor(String)),
                                    Input('hashedLoginToken', typeFor(String)),
                                    ], {})

        self._sessions = {}
        self._sessionsExpirations = deque()

    def getLoginToken(self, userName):
        '''
        Return a token for the client to encrypt using the user key.

        @param userName: string
            The user login name for which to generate the token.
        @return: string
            The token for the client to encrypt.
        '''
        # check if the user exists
        self.userKeyGenerator.getUserKey(userName)
        return self._createSession(userName, self.loginTokenTimeout)

    def login(self, userName, loginToken, hashedLoginToken):
        '''
        Process a login request.

        @param userName: string
            The user login name which requests the login process.
        @param loginToken: string
            The login token received by the client.
        @param hashedLoginToken: string
            The hashed login token
        @return: string|None
            The new session identifier if the login was successful.
        '''
        self._cleanExpiredSessions()
        if loginToken not in self._sessions:
            raise InputError('Invalid login token %s' % loginToken)
        userKey = self.userKeyGenerator.getUserKey(userName)
        verifyToken = hmac.new(userName + userKey, loginToken, hashlib.sha512())
        if verifyToken != hashedLoginToken:
            raise InputError('Invalid credentials')
        return self._createSession(userName, self.loginTokenTimeout)

    def process(self, req, rsp, chain):
        '''
        @see: Processor.process
        '''
        assert isinstance(req, RequestHTTP), 'Invalid request %s' % req
        assert isinstance(chain, ProcessorsChain), 'Invalid processors chain %s' % chain
        assert isinstance(rsp, Response), 'Invalid response %s' % rsp
        assert isinstance(req.invoker, Invoker), 'Invalid request invoker %s' % req

        self._cleanExpiredSessions()
        try: sessionId = str(self._parse(self.sessionName, req.headers, req.params, VALUE_NO_PARSE))
        except DevelError as e:
            assert isinstance(e, DevelError)
            rsp.setCode(INVALID_HEADER_VALUE, e.message)
            return

        typesAuth = [inp for inp in req.invoker.inputs if isinstance(inp.type, TypeAuthentication)]
        if typesAuth:
            if sessionId and sessionId in self._sessions:
                for inp in typesAuth:
                    assert isinstance(inp, Input)
                    req.arguments[inp.name] = sessionId
            else:
                rsp.setCode(UNAUTHORIZED, 'Unauthorized access')
                return

        chain.proceed()

    def _cleanExpiredSessions(self):
        '''
        Deletes the sessions that expired.
        '''
        now = str(datetime.utcnow())
        while len(self._sessionsExpirations):
            expireTime, sessionId = self._sessionsExpirations[0]
            if expireTime <= now:
                self._sessionsExpirations.popleft()
                self._sessions.pop(sessionId)
            else:
                break

    def _createSession(self, userName, timeout=None):
        '''
        Creates a session and returns the session identifier.

        @param userName: string
            The user login name for which to create the session.
        @param timeout: timedelta
            The number of seconds after the session expires.
        @return: string
            The session identifier
        '''
        assert timeout is None or isinstance(timeout, timedelta), 'Invalid time delta %s' % timeout
        h = hashlib.sha512()
        h.update(urandom(len(userName) + randint(10, 20)))
        sessionId = h.hexdigest()
        s = Session(sessionId, userName, datetime.utcnow())
        if timeout:
            s.expireTime = s.createTime + timeout
            self._sessionsExpirations.append((s.expireTime, sessionId))
        self._sessions[sessionId] = s
        return sessionId
