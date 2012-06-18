'''
Created on Jun 11, 2012

@package: ally core http
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the content disposition header decoding.
'''

from ally.container.ioc import injected
from ally.core.http.spec.codes import INVALID_HEADER_VALUE
from ally.core.http.spec.server import IDecoderHeader
from ally.core.spec.codes import Code
from ally.design.context import Context, requires, defines
from ally.design.processor import Chain, HandlerProcessor

# --------------------------------------------------------------------

class Request(Context):
    '''
    The request context.
    '''
    # ---------------------------------------------------------------- Required
    decoderHeader = requires(IDecoderHeader)

class RequestContent(Context):
    '''
    The response content context.
    '''
    # ---------------------------------------------------------------- Defined
    disposition = defines(str, doc='''
    @rtype: string
    The content disposition.
    ''')
    dispositionAttr = defines(dict, doc='''
    @rtype: dictionary{string, string}
    The content disposition attributes.
    ''')

class Response(Context):
    '''
    The response context.
    '''
    # ---------------------------------------------------------------- Defined
    code = defines(Code)
    text = defines(str)
    message = defines(str)

# --------------------------------------------------------------------

@injected
class ContentDispositionDecodeHandler(HandlerProcessor):
    '''
    Implementation for a processor that provides the decoding of content disposition HTTP request header.
    '''

    nameContentDisposition = 'Content-Disposition'
    # The header name where the content disposition is set.

    def __init__(self):
        assert isinstance(self.nameContentDisposition, str), \
        'Invalid content disposition header name %s' % self.nameContentDisposition
        super().__init__()

    def process(self, chain, request:Request, requestCnt:RequestContent, response:Response, **keyargs):
        '''
        @see: HandlerProcessor.process
        
        Provides the content type decode for the request.
        '''
        assert isinstance(chain, Chain), 'Invalid processors chain %s' % chain
        assert isinstance(request, Request), 'Invalid request %s' % request
        assert isinstance(response, Response), 'Invalid response %s' % response
        assert isinstance(requestCnt, RequestContent), 'Invalid request content %s' % requestCnt
        assert isinstance(request.decoderHeader, IDecoderHeader), 'Invalid header decoder %s' % request.decoderHeader

        value = request.decoderHeader.decode(self.nameContentDisposition)
        if value:
            if len(value) > 1:
                response.code, response.text = INVALID_HEADER_VALUE, 'Invalid %s' % self.nameContentDisposition
                response.message = 'Invalid value \'%s\' for header \'%s\''\
                ', expected only one value entry' % (value, self.nameContentDisposition)
                return
            value, attributes = value[0]
            requestCnt.disposition = value
            requestCnt.dispositionAttr = attributes

        chain.proceed()
