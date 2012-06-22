'''
Created on Jun 11, 2012

@package: ally core http
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the content type header decoding/encoding.
'''

from ally.container.ioc import injected
from ally.core.http.spec.codes import INVALID_HEADER_VALUE
from ally.core.http.spec.server import IDecoderHeader, IEncoderHeader
from ally.core.spec.codes import Code
from ally.design.context import Context, requires, defines, optional
from ally.design.processor import HandlerProcessorProceed

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
    type = defines(str, doc='''
    @rtype: string
    The request content type.
    ''')
    charSet = defines(str, doc='''
    @rtype: string
    The character set for the text content.
    ''')
    typeAttr = defines(dict, doc='''
    @rtype: dictionary{string, string}
    The content request type attributes.
    ''')

class ResponseDecode(Context):
    '''
    The response context.
    '''
    # ---------------------------------------------------------------- Defined
    code = defines(Code)
    text = defines(str)
    message = defines(str)

# --------------------------------------------------------------------

@injected
class ContentTypeDecodeHandler(HandlerProcessorProceed):
    '''
    Implementation for a processor that provides the decoding of content type HTTP request header.
    '''

    nameContentType = 'Content-Type'
    # The header name where the content type is specified.
    attrContentTypeCharSet = 'charset'
    # The name of the content type attribute where the character set is provided.

    def __init__(self):
        assert isinstance(self.nameContentType, str), 'Invalid content type header name %s' % self.nameContentType
        assert isinstance(self.attrContentTypeCharSet, str), \
        'Invalid char set attribute name %s' % self.attrContentTypeCharSet
        super().__init__()

    def process(self, request:Request, requestCnt:RequestContent, response:ResponseDecode, **keyargs):
        '''
        @see: HandlerProcessorProceed.process
        
        Decode the content type for the request.
        '''
        assert isinstance(request, Request), 'Invalid request %s' % request
        assert isinstance(response, ResponseDecode), 'Invalid response %s' % response
        assert isinstance(requestCnt, RequestContent), 'Invalid request content %s' % requestCnt
        assert isinstance(request.decoderHeader, IDecoderHeader), 'Invalid header decoder %s' % request.decoderHeader

        value = request.decoderHeader.decode(self.nameContentType)
        if value:
            if len(value) > 1:
                if ResponseDecode.code in response and not response.code.isSuccess: return
                response.code, response.text = INVALID_HEADER_VALUE, 'Invalid %s' % self.nameContentType
                response.message = 'Invalid value \'%s\' for header \'%s\''\
                ', expected only one type entry' % (value, self.nameContentType)
                return
            value, attributes = value[0]
            requestCnt.type = value
            requestCnt.charSet = attributes.get(self.attrContentTypeCharSet, None)
            requestCnt.typeAttr = attributes

# --------------------------------------------------------------------

class ResponseEncode(Context):
    '''
    The response context.
    '''
    # ---------------------------------------------------------------- Required
    encoderHeader = requires(IEncoderHeader)

class ResponseContent(Context):
    '''
    The response content context.
    '''
    # ---------------------------------------------------------------- Required
    type = requires(str)
    # ---------------------------------------------------------------- Optional
    charSet = optional(str)

# --------------------------------------------------------------------

@injected
class ContentTypeEncodeHandler(HandlerProcessorProceed):
    '''
    Implementation for a processor that provides the encoding of content type HTTP request header.
    '''

    nameContentType = 'Content-Type'
    # The header name where the content type is specified.
    attrContentTypeCharSet = 'charset'
    # The name of the content type attribute where the character set is provided.

    def __init__(self):
        assert isinstance(self.nameContentType, str), 'Invalid content type header name %s' % self.nameContentType
        assert isinstance(self.attrContentTypeCharSet, str), \
        'Invalid char set attribute name %s' % self.attrContentTypeCharSet
        super().__init__()

    def process(self, response:ResponseEncode, responseCnt:ResponseContent, **keyargs):
        '''
        @see: HandlerProcessorProceed.process
        
        Encodes the content type for the response.
        '''
        assert isinstance(response, ResponseEncode), 'Invalid response %s' % response
        assert isinstance(responseCnt, ResponseContent), 'Invalid response content %s' % responseCnt
        assert isinstance(response.encoderHeader, IEncoderHeader), \
        'Invalid header encoder %s' % response.encoderHeader

        if ResponseContent.type in responseCnt:
            value = responseCnt.type
            if ResponseContent.charSet in responseCnt:
                if responseCnt.charSet: value = (value, (self.attrContentTypeCharSet, responseCnt.charSet))

            response.encoderHeader.encode(self.nameContentType, value)

