'''
Created on Jun 11, 2012

@package: ally http
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the content type header decoding/encoding.
'''

from ally.container.ioc import injected
from ally.core.http.spec.codes import CONTENT_TYPE_ERROR
from ally.design.processor.attribute import requires, optional, defines
from ally.design.processor.context import Context
from ally.design.processor.handler import HandlerProcessorProceed
from ally.http.spec.server import IDecoderHeader, IEncoderHeader
        
# --------------------------------------------------------------------

class Response(Context):
    '''
    The response context.
    '''
    # ---------------------------------------------------------------- Defined
    code = defines(str)
    status = defines(int)
    isSuccess = defines(bool)
    text = defines(str)

# --------------------------------------------------------------------

class ContentTypeConfigurations:
    '''
    Provides the configurations for content type HTTP request header.
    '''

    nameContentType = 'Content-Type'
    # The header name where the content type is specified.
    attrContentTypeCharSet = 'charset'
    # The name of the content type attribute where the character set is provided.

    def __init__(self):
        assert isinstance(self.nameContentType, str), 'Invalid content type header name %s' % self.nameContentType
        assert isinstance(self.attrContentTypeCharSet, str), 'Invalid char set attribute name %s' % self.attrContentTypeCharSet

# --------------------------------------------------------------------

class RequestDecode(Context):
    '''
    The request context decode.
    '''
    # ---------------------------------------------------------------- Required
    decoderHeader = requires(IDecoderHeader)

class RequestContentDecode(Context):
    '''
    The request content context decode.
    '''
    # ---------------------------------------------------------------- Defined
    type = defines(str, doc='''
    @rtype: string
    The request content type.
    ''')
    charSet = defines(str, doc='''
    @rtype: string
    The request character set for the text content.
    ''')
    typeAttr = defines(dict, doc='''
    @rtype: dictionary{string, string}
    The content request type attributes.
    ''')
    
# --------------------------------------------------------------------

@injected
class ContentTypeRequestDecodeHandler(HandlerProcessorProceed, ContentTypeConfigurations):
    '''
    Implementation for a processor that provides the decoding of content type HTTP request header.
    '''

    def __init__(self):
        ContentTypeConfigurations.__init__(self)
        HandlerProcessorProceed.__init__(self)

    def process(self, request:RequestDecode, requestCnt:RequestContentDecode, response:Response, **keyargs):
        '''
        @see: HandlerProcessorProceed.process
        
        Decode the content type for the request.
        '''
        assert isinstance(request, RequestDecode), 'Invalid request %s' % request
        assert isinstance(requestCnt, RequestContentDecode), 'Invalid request content %s' % requestCnt
        assert isinstance(response, Response), 'Invalid response %s' % response
        assert isinstance(request.decoderHeader, IDecoderHeader), 'Invalid header decoder %s' % request.decoderHeader

        value = request.decoderHeader.decode(self.nameContentType)
        if value:
            if len(value) > 1:
                if response.isSuccess is False: return  # Skip in case the response is in error
                response.code, response.status, response.isSuccess = CONTENT_TYPE_ERROR
                response.text = 'Invalid value \'%s\' for header \'%s\''\
                ', expected only one type entry' % (value, self.nameContentType)
                return
            value, attributes = value[0]
            requestCnt.type = value
            requestCnt.charSet = attributes.get(self.attrContentTypeCharSet, None)
            requestCnt.typeAttr = attributes

# --------------------------------------------------------------------

class ResponseDecode(Response):
    '''
    The response context decode.
    '''
    # ---------------------------------------------------------------- Required
    decoderHeader = requires(IDecoderHeader)

class ResponseContentDecode(Context):
    '''
    The request content context decode.
    '''
    # ---------------------------------------------------------------- Defined
    type = defines(str, doc='''
    @rtype: string
    The response content type.
    ''')
    charSet = defines(str, doc='''
    @rtype: string
    The response character set for the text content.
    ''')
    typeAttr = defines(dict, doc='''
    @rtype: dictionary{string, string}
    The content response type attributes.
    ''')
    
# --------------------------------------------------------------------

@injected
class ContentTypeResponseDecodeHandler(HandlerProcessorProceed, ContentTypeConfigurations):
    '''
    Implementation for a processor that provides the decoding of content type HTTP response header.
    '''

    def __init__(self):
        ContentTypeConfigurations.__init__(self)
        HandlerProcessorProceed.__init__(self)

    def process(self, response:ResponseDecode, responseCnt:ResponseContentDecode, **keyargs):
        '''
        @see: HandlerProcessorProceed.process
        
        Decode the content type for the response.
        '''
        assert isinstance(response, ResponseDecode), 'Invalid response %s' % response
        assert isinstance(responseCnt, ResponseContentDecode), 'Invalid response content %s' % responseCnt
        if response.isSuccess is False: return  # Skip in case the response is in error
        
        assert isinstance(response.decoderHeader, IDecoderHeader), 'Invalid header decoder %s' % response.decoderHeader
        value = response.decoderHeader.decode(self.nameContentType)
        if value:
            if len(value) > 1:
                if response.isSuccess is False: return  # Skip in case the response is in error
                response.code, response.status, response.isSuccess = CONTENT_TYPE_ERROR
                response.text = 'Invalid value \'%s\' for header \'%s\''\
                ', expected only one type entry' % (value, self.nameContentType)
                return
            value, attributes = value[0]
            responseCnt.type = value
            responseCnt.charSet = attributes.get(self.attrContentTypeCharSet, None)
            responseCnt.typeAttr = attributes

# --------------------------------------------------------------------

class ResponseEncode(Context):
    '''
    The response context.
    '''
    # ---------------------------------------------------------------- Required
    encoderHeader = requires(IEncoderHeader)

class ResponseContentEncode(Context):
    '''
    The response content context.
    '''
    # ---------------------------------------------------------------- Required
    type = requires(str)
    # ---------------------------------------------------------------- Optional
    charSet = optional(str)

# --------------------------------------------------------------------

@injected
class ContentTypeResponseEncodeHandler(HandlerProcessorProceed, ContentTypeConfigurations):
    '''
    Implementation for a processor that provides the encoding of content type HTTP request header.
    '''

    def __init__(self):
        ContentTypeConfigurations.__init__(self)
        HandlerProcessorProceed.__init__(self)

    def process(self, response:ResponseEncode, responseCnt:ResponseContentEncode, **keyargs):
        '''
        @see: HandlerProcessorProceed.process
        
        Encodes the content type for the response.
        '''
        assert isinstance(response, ResponseEncode), 'Invalid response %s' % response
        assert isinstance(responseCnt, ResponseContentEncode), 'Invalid response content %s' % responseCnt
        assert isinstance(response.encoderHeader, IEncoderHeader), 'Invalid header encoder %s' % response.encoderHeader

        if responseCnt.type:
            value = responseCnt.type
            if ResponseContentEncode.charSet in responseCnt and responseCnt.charSet:
                if responseCnt.charSet: value = (value, (self.attrContentTypeCharSet, responseCnt.charSet))

            response.encoderHeader.encode(self.nameContentType, value)
