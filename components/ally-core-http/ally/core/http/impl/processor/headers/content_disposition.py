'''
Created on Jun 11, 2012

@package: ally core http
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the content disposition header decoding.
'''

from ally.container.ioc import injected
from ally.design.processor.attribute import requires, defines
from ally.design.processor.context import Context
from ally.design.processor.handler import HandlerProcessorProceed
from ally.http.spec.codes import HEADER_ERROR
from ally.http.spec.server import IDecoderHeader

# --------------------------------------------------------------------

class Request(Context):
    '''
    The request context.
    '''
    # ---------------------------------------------------------------- Required
    decoderHeader = requires(IDecoderHeader)

class RequestContent(Context):
    '''
    The request content context.
    '''
    # ---------------------------------------------------------------- Defined
    name = defines(str, doc='''
    @rtype: string
    The content name.
    ''')
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
    code = defines(str)
    status = defines(int)
    isSuccess = defines(bool)
    text = defines(str)
    errorMessage = defines(str)

# --------------------------------------------------------------------

@injected
class ContentDispositionDecodeHandler(HandlerProcessorProceed):
    '''
    Implementation for a processor that provides the decoding of content disposition HTTP request header.
    '''

    uploadFilename = 'filename'
    # The filename parameter from a multipart form
    nameContentDisposition = 'Content-Disposition'
    # The header name where the content disposition is set.

    def __init__(self):
        assert isinstance(self.uploadFilename, str), 'Invalid upload file name %s' % self.uploadFilename
        assert isinstance(self.nameContentDisposition, str), \
        'Invalid content disposition header name %s' % self.nameContentDisposition
        super().__init__()

    def process(self, request:Request, requestCnt:RequestContent, response:Response, **keyargs):
        '''
        @see: HandlerProcessorProceed.process

        Provides the content type decode for the request.
        '''
        assert isinstance(request, Request), 'Invalid request %s' % request
        assert isinstance(requestCnt, RequestContent), 'Invalid request content %s' % requestCnt
        assert isinstance(response, Response), 'Invalid response %s' % response
        assert isinstance(request.decoderHeader, IDecoderHeader), 'Invalid header decoder %s' % request.decoderHeader

        value = request.decoderHeader.decode(self.nameContentDisposition)
        if value:
            if len(value) > 1:
                if response.isSuccess is False: return  # Skip in case the response is in error
                response.code, response.status, response.isSuccess = HEADER_ERROR
                response.text = 'Invalid \'%s\'' % self.nameContentDisposition
                response.errorMessage = 'Invalid value \'%s\' for header \'%s\''\
                ', expected only one value entry' % (value, self.nameContentDisposition)
                return
            value, attributes = value[0]
            requestCnt.disposition = value
            requestCnt.dispositionAttr = attributes
            if self.uploadFilename in attributes:
                requestCnt.name = attributes[self.uploadFilename]
