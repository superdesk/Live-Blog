'''
Created on Aug 9, 2011

@package: ally core http
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the X headers handling.
'''

from .header import HeaderHTTPBase, VALUES, VALUE_NO_PARSE
from ally.api.operator.container import Model
from ally.api.operator.type import TypeModel
from ally.api.type import formattedType, Iter
from ally.container.ioc import injected
from ally.core.http.spec import RequestHTTP, INVALID_HEADER_VALUE
from ally.core.spec.resources import Normalizer
from ally.core.spec.server import Processor, ProcessorsChain, Response, \
    ContentRequest
from ally.exception import DevelError

# --------------------------------------------------------------------

@injected
class MethodOverrideHandler(HeaderHTTPBase, Processor):
    '''
    Provides the method override processor.
    
    Provides on request: method
    Provides on response: NA
    
    Requires on request: headers, params, method
    Requires on response: NA
    '''

    normalizer = Normalizer
    # The normalizer used for matching property names with header values.
    nameXMethodOverride = 'X-HTTP-Method-Override'
    # The header name for the method override.

    def __init__(self):
        super().__init__()
        assert isinstance(self.normalizer, Normalizer), 'Invalid normalizer %s' % self.normalizer
        assert isinstance(self.nameXMethodOverride, str), 'Invalid method override name %s' % self.nameXMethodOverride

    def process(self, req, rsp, chain):
        '''
        @see: Processor.process
        '''
        assert isinstance(req, RequestHTTP), 'Invalid request %s' % req
        assert isinstance(chain, ProcessorsChain), 'Invalid processors chain %s' % chain
        assert isinstance(rsp, Response), 'Invalid response %s' % rsp
        assert isinstance(req.content, ContentRequest), 'Invalid content on request %s' % req.content

        try:
            p = self._parse(self.nameXMethodOverride, req.headers, req.params, VALUES)
            if p:
                if req.method:
                    m =

        except DevelError as e:
            assert isinstance(e, DevelError)
            rsp.setCode(INVALID_HEADER_VALUE, e.message)
            return
        chain.proceed()

    def encode(self, headers, rsp):
        '''
        @see: EncoderHeader.encode
        '''
        assert isinstance(headers, dict), 'Invalid headers dictionary %s' % headers
        assert isinstance(rsp, Response), 'Invalid response %s' % rsp

        if rsp.objInclude:
            headers[self.nameXFilter] = self._encode(*[self.normalizer.normalize(prop) for prop in rsp.objInclude])

        for clsTyp, value in rsp.objFormat.items():
            headers[self.nameXFormat % clsTyp.__name__] = value
