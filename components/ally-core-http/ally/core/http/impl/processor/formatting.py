'''
Created on Feb 1, 2012

@package: ally core http
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the formatting from the http headers for the converters.
'''

from .header import HeaderHTTPBase, VALUE_NO_PARSE
from ally.api.type import formattedType
from ally.container.ioc import injected
from ally.core.http.spec import RequestHTTP, EncoderHeader, INVALID_HEADER_VALUE
from ally.core.spec.server import IProcessor, ProcessorsChain, Response, \
    ContentRequest
from ally.exception import DevelError

# --------------------------------------------------------------------

@injected
class FormattingProviderHandler(HeaderHTTPBase, IProcessor, EncoderHeader):
    '''
    Reads from the header the formating (object format) used in the response, the decoding 
    of HTTP request header 'X-Format-*' and 'X-FormatContent-*'. Also provides the encoding
    of the formating used in the response header.
    
    Provides on request: content.objFormat
    Provides on response: objFormat
    
    Requires on request: headers, parameters, content
    Requires on response: NA
    '''

    nameXFormat = 'X-Format-%s'
    nameXFormatContent = 'X-FormatContent-%s'

    def __init__(self):
        super().__init__()
        assert isinstance(self.nameXFormat, str), 'Invalid name format %s' % self.nameXFormat
        assert isinstance(self.nameXFormatContent, str), 'Invalid name content format %s' % self.nameXFormatContent

    def process(self, req, rsp, chain):
        '''
        @see: Processor.process
        '''
        assert isinstance(req, RequestHTTP), 'Invalid request %s' % req
        assert isinstance(chain, ProcessorsChain), 'Invalid processors chain %s' % chain
        assert isinstance(rsp, Response), 'Invalid response %s' % rsp
        assert isinstance(req.content, ContentRequest), 'Invalid content on request %s' % req.content

        try:

            for clsTyp in formattedType:
                p = self._parse(self.nameXFormat % clsTyp.__name__, req.headers, req.parameters, VALUE_NO_PARSE)
                if p: rsp.objFormat[clsTyp] = p
                p = self._parse(self.nameXFormatContent % clsTyp.__name__, req.headers, req.parameters, VALUE_NO_PARSE)
                if p: req.content.objFormat[clsTyp] = p

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

        for clsTyp, value in rsp.objFormat.items():
            headers[self.nameXFormat % clsTyp.__name__] = value
