'''
Created on Aug 9, 2011

@package: ally authentication http
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the authentication header handling.
'''

from ally.api.operator.authentication.type import TypeAuthentication
from ally.api.type import Input
from ally.container.ioc import injected
from ally.core.http.impl.processor.header import HeaderHTTPBase, VALUE_NO_PARSE
from ally.core.http.spec import RequestHTTP, INVALID_HEADER_VALUE, UNAUTHORIZED
from ally.core.spec.resources import Invoker
from ally.core.spec.server import IProcessor, ProcessorsChain, Response
from ally.exception import DevelError
import logging

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

@injected
class AuthenticationHandler(HeaderHTTPBase, IProcessor):
    '''
    Provides the authentication handling.
    
    Provides on request: [arguments]
    Provides on response: NA
    
    Requires on request: headers, params, invoker
    Requires on response: NA
    '''

    nameAuthentication = 'Authorization'
    # The header name for the authentication.

    def __init__(self):
        super().__init__()
        assert isinstance(self.nameAuthentication, str), 'Invalid name authentication %s' % self.nameAuthentication

    def process(self, req, rsp, chain):
        '''
        @see: Processor.process
        '''
        assert isinstance(req, RequestHTTP), 'Invalid request %s' % req
        assert isinstance(chain, ProcessorsChain), 'Invalid processors chain %s' % chain
        assert isinstance(rsp, Response), 'Invalid response %s' % rsp
        assert isinstance(req.invoker, Invoker), 'Invalid request invoker %s' % req

        try: p = self._parse(self.nameAuthentication, req.headers, req.params, VALUE_NO_PARSE)
        except DevelError as e:
            assert isinstance(e, DevelError)
            rsp.setCode(INVALID_HEADER_VALUE, e.message)
            return

        typesAuth = [inp for inp in req.invoker.inputs if isinstance(inp.type, TypeAuthentication)]
        if typesAuth:
            if p:
                #TODO: implement properly
                id = int(p)
                for inp in typesAuth:
                    assert isinstance(inp, Input)
                    req.arguments[inp.name] = id
            else:
                rsp.setCode(UNAUTHORIZED, 'Unauthorized access')
                return

        chain.proceed()
