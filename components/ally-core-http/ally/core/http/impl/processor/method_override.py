'''
Created on Aug 9, 2011

@package: ally core http
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the method override header handling.
'''

from .header import HeaderHTTPBase, VALUE_NO_PARSE
from ally.api.config import DELETE, GET, INSERT, UPDATE
from ally.container.ioc import injected
from ally.core.http.spec import RequestHTTP, INVALID_HEADER_VALUE
from ally.core.spec.server import IProcessor, ProcessorsChain, Response, \
    ContentRequest
from ally.exception import DevelError
import logging

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

@injected
class MethodOverrideHandler(HeaderHTTPBase, IProcessor):
    '''
    Provides the method override processor: it changes the request method to the one
    specified by the parameter named in "self.nameXMethodOverride". This is needed
    because PUT requests can not be made from Javascript running in a browser and
    also for development (debugging/testing).
    
    Provides on request: method
    Provides on response: NA
    
    Requires on request: headers, parameters, method
    Requires on response: NA
    '''

    nameXMethodOverride = 'X-HTTP-Method-Override'
    # The header name for the method override.
    methods = {
              'DELETE' : DELETE,
              'GET' : GET,
              'POST' : INSERT,
              'PUT' : UPDATE,
              }
    methodsOverride = {
                       GET:{GET, DELETE},
                       INSERT:{INSERT, UPDATE},
                       }
    # A dictionary containing as a key the original method and as a value the methods that are allowed for override.

    def __init__(self):
        super().__init__()
        assert isinstance(self.nameXMethodOverride, str), 'Invalid method override name %s' % self.nameXMethodOverride
        assert isinstance(self.methods, dict), 'Invalid methods %s' % self.methods
        assert isinstance(self.methodsOverride, dict), 'Invalid methods override %s' % self.methodsOverride

    def process(self, req, rsp, chain):
        '''
        @see: IProcessor.process
        '''
        assert isinstance(req, RequestHTTP), 'Invalid request %s' % req
        assert isinstance(chain, ProcessorsChain), 'Invalid processors chain %s' % chain
        assert isinstance(rsp, Response), 'Invalid response %s' % rsp
        assert isinstance(req.content, ContentRequest), 'Invalid content on request %s' % req.content

        try:
            p = self._parse(self.nameXMethodOverride, req.headers, req.parameters, VALUE_NO_PARSE)
        except DevelError as e:
            assert isinstance(e, DevelError)
            rsp.setCode(INVALID_HEADER_VALUE, e.message)
            return

        if p:
            over = self.methods.get(p.upper())
            if not over:
                rsp.setCode(INVALID_HEADER_VALUE, 'Invalid method \'%s\'' % p)
                return

            allowed = self.methodsOverride.get(req.method)
            if not allowed:
                rsp.setCode(INVALID_HEADER_VALUE, 'The current method cannot be overridden')
                return

            if over not in allowed:
                rsp.setCode(INVALID_HEADER_VALUE, 'The current method cannot be overridden by \'%s\'' % p)
                return

            assert log.debug('Successfully overridden method %s with %s', req.method, over) or True
            req.method = over

        chain.proceed()
