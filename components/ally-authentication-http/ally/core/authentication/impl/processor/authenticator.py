'''
Created on Aug 9, 2011

@package: ally authentication http
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the authentication header handling.
'''

import logging
import hashlib
import hmac
from collections import deque
from os import urandom
from random import randint
from sys import getdefaultencoding
from ally.api.operator.authentication.type import TypeAuthentication
from ally.container.ioc import injected
from ally.core.http.impl.processor.header import HeaderHTTPBase, VALUE_NO_PARSE
from ally.core.http.spec import RequestHTTP, INVALID_HEADER_VALUE, UNAUTHORIZED
from ally.core.spec.resources import Invoker, IResourcesRegister
from ally.core.spec.server import Processor, ProcessorsChain, Response
from ally.exception import DevelError, InputError
from ally.core.impl.node import NodePath
from ally.core.impl.invoker import InvokerFunction
from ally.api.config import GET, INSERT
from ally.api.type import Input, typeFor, String
from datetime import datetime, timedelta
from ally.core.authentication.api.authentication import IAuthenticate
import threading

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
    sessionName = 'Authorization'
    # The header name for the session identifier.
    login_token_timeout = timedelta(seconds=10)
    # The number of seconds after which the login token expires.
    session_token_timeout = timedelta(seconds=3600)
    # The number of seconds after which the session expires.
    userKeyGenerator = IAuthenticate
    # The implementation of IAuthenticate that permits the retrieval of the user secret key
    resourcesRegister = IResourcesRegister
    # The resources register used in getting the node structure.

    def __init__(self):
        assert isinstance(self.sessionName, str), 'Invalid session name %s' % self.sessionName
        assert isinstance(self.login_token_timeout, timedelta), \
        'Invalid login token timeout value %s' % self.login_token_timeout
        assert isinstance(self.session_token_timeout, timedelta), \
        'Invalid session token timeout value %s' % self.session_token_timeout
        assert isinstance(self.resourcesRegister, IResourcesRegister), \
        'Invalid resources manager %s' % self.resourcesManager
        super().__init__()

        node = NodePath(self.resourcesRegister.getRoot(), True, 'Authentication')
        node.get = InvokerFunction(GET, self.loginToken, typeFor(String),
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

    def loginToken(self, userName):
        '''
        Return a token for the client to encrypt using the user key.

        @param userName: string
            The user login name for which to generate the token.
        @return: string
            The token for the client to encrypt.
        '''
        assert isinstance(self.userKeyGenerator, IAuthenticate), 'Invalid user key generator %s' % self.userKeyGenerator

        # check if the user exists
        self.userKeyGenerator.getUserKey(userName)
        return self._createSession(userName, self.login_token_timeout)

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
        assert isinstance(self.userKeyGenerator, IAuthenticate), 'Invalid user key generator %s' % self.userKeyGenerator

        self._cleanExpiredSessions()
        if loginToken not in self._sessions:
            raise InputError('Invalid login token %s' % loginToken)
        userKey = self.userKeyGenerator.getUserKey(userName)
        verifyToken = hmac.new(bytes(userName + userKey, getdefaultencoding()),
                               bytes(loginToken, getdefaultencoding()), hashlib.sha512).hexdigest()
        if verifyToken != hashedLoginToken:
            raise InputError('Invalid credentials')
        return self._createSession(userName, self.session_token_timeout)

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
        now = datetime.utcnow()
        while len(self._sessionsExpirations):
            expireTime, sessionId = self._sessionsExpirations[0]
            if expireTime <= now:
                m = threading.Lock()
                m.acquire()
                try:
                    self._sessionsExpirations.popleft()
                    self._sessions.pop(sessionId)
                finally: m.release()
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
        m = threading.Lock()
        m.acquire()
        try:
            if timeout:
                s.expireTime = s.createTime + timeout
                self._sessionsExpirations.append((s.expireTime, sessionId))
            self._sessions[sessionId] = s
        finally: m.release()
        return sessionId
