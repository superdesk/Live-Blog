'''
Created on Aug 9, 2011

@package: ally authentication http
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the authentication header handling.
'''

from ally.api.operator.authentication.service import IAuthenticationSupport
from ally.api.operator.authentication.type import TypeAuthentication
from ally.api.type import Input
from ally.container.ioc import injected
from ally.core.http.spec.codes import UNAUTHORIZED
from ally.core.http.spec.server import IDecoderHeader
from ally.core.spec.codes import Code
from ally.core.spec.resources import Invoker
from ally.design.context import Context, requires, defines
from ally.design.processor import HandlerProcessorProceed
import logging

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

class Request(Context):
    '''
    The request context.
    '''
    # ---------------------------------------------------------------- Required
    decoderHeader = requires(IDecoderHeader)
    invoker = requires(Invoker)
    arguments = requires(dict)

class Response(Context):
    '''
    The response context.
    '''
    # ---------------------------------------------------------------- Defined
    code = defines(Code)
    text = defines(str)

# --------------------------------------------------------------------

@injected
class AuthenticationHandler(HandlerProcessorProceed):
    '''
    Provides the authentication handling.
    '''
    nameAuthorization = 'Authorization'
    # The header name for the session identifier.
    alwaysAuthenticate = False
    # Flag indicating that the authentication should not be made only when there is a authentication data type required
    # but the authentication should be made for all requests
    authenticators = list
    # The IAuthenticationSupport used for authentication.

    def __init__(self):
        assert isinstance(self.nameAuthorization, str), 'Invalid authorization name %s' % self.nameAuthorization
        assert isinstance(self.alwaysAuthenticate, bool), 'Invalid authenticate flag %s' % self.alwaysAuthenticate
        assert isinstance(self.authenticators, list), 'Invalid authenticators %s' % self.authenticators
        if __debug__:
            for authenticator in self.authenticators:
                assert isinstance(authenticator, IAuthenticationSupport), 'Invalid authenticator %s' % authenticator
        super().__init__()

    def process(self, request:Request, response:Response, **keyargs):
        '''
        @see: HandlerProcessorProceed.process
        
        Decode the authentication for the request.
        '''
        assert isinstance(request, Request), 'Invalid request %s' % request
        assert isinstance(response, Response), 'Invalid response %s' % response

        if Response.code in response and not response.code.isSuccess: return # Skip in case the response is in error
        
        assert isinstance(request.decoderHeader, IDecoderHeader), 'Invalid decoder header %s' % request.decoderHeader
        assert isinstance(request.invoker, Invoker), 'Invalid invoker %s' % request.invoker

        arguments, typesNames = {}, {}
        for inp in request.invoker.inputs:
            assert isinstance(inp, Input), 'Invalid input %s' % inp
            if isinstance(inp.type, TypeAuthentication):
                assert isinstance(inp.type, TypeAuthentication)
                authType = typesNames[inp.name] = inp.type.type
                if inp.hasDefault: arguments[authType] = inp.default
                elif authType not in arguments: arguments[authType] = None

        if arguments or self.alwaysAuthenticate:
            authentication = request.decoderHeader.decode(self.nameAuthorization)
            if not authentication:
                response.code, response.text = UNAUTHORIZED, 'Unauthorized access'
                return

            for identifier, attributes in authentication:
                for authenticator in self.authenticators:
                    assert isinstance(authenticator, IAuthenticationSupport), 'Invalid authenticator %s' % authenticator
                    if authenticator.authenticate(identifier, attributes, arguments):
                        for name, authType in typesNames.items(): request.arguments[name] = arguments[authType]
                        return

            response.code, response.text = UNAUTHORIZED, 'Invalid authorization'
            return
