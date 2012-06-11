'''
Created on Jun 11, 2012

Provides the content type header encoding.
'''

from ally.container.ioc import injected
from ally.core.http.spec.extension import HTTPEncode
from ally.core.http.spec.server import IEncoderHeader
from ally.core.spec.extension import CharSet
from ally.core.spec.server import Content
from ally.design.processor import Handler, processor

# --------------------------------------------------------------------

@injected
class ContentTypeEncodeHandler(Handler):
    '''
    Implementation for a processor that provides the encoding of content type HTTP response header.
    '''

    nameContentType = 'Content-Type'
    # The header name where the content type is specified.
    attrContentTypeCharSet = 'charset'
    # The name of the content type attribute where the character set is provided.

    def __init__(self):
        assert isinstance(self.nameContentType, str), 'Invalid content type header name %s' % self.nameContentType
        assert isinstance(self.attrContentTypeCharSet, str), \
        'Invalid char set attribute name %s' % self.attrContentTypeCharSet

    @processor
    def process(self, chain, response:HTTPEncode, responseCnt:Content, **keyargs):
        '''
        Encodes the content type for the response.
        '''
        assert isinstance(response, HTTPEncode), 'Invalid response %s' % response
        assert isinstance(response.encoderHeader, IEncoderHeader), \
        'Invalid header encoder %s' % response.encoderHeader
        assert isinstance(responseCnt, Content), 'Invalid response content %s' % responseCnt

        if responseCnt.type:
            value = responseCnt.type
            if isinstance(responseCnt, CharSet):
                assert isinstance(responseCnt, CharSet)
                if responseCnt.charSet: value = (value, (self.attrContentTypeCharSet, responseCnt.charSet))

            response.encoderHeader.encode(self.nameContentType, value)

        chain.proceed()
