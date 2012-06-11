'''
Created on Jun 11, 2012

@package: ally core http
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the content type header decoding.
'''

from ally.container.ioc import injected
from ally.core.http.spec.codes import INVALID_HEADER_VALUE
from ally.core.http.spec.extension import HTTPDecode, ContentType
from ally.core.http.spec.server import IDecoderHeader
from ally.core.spec.extension import CharSet
from ally.core.spec.server import Response, Content
from ally.design.processor import Handler, processor, Chain, mokup

# --------------------------------------------------------------------

@mokup(Content)
class _ContentRequest(Content, CharSet, ContentType):
    ''' Used as a mokup class '''

# --------------------------------------------------------------------

@injected
class ContentTypeDecodeHandler(Handler):
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

    @processor
    def process(self, chain, request:HTTPDecode, requestCnt:_ContentRequest, response:Response, **keyargs):
        '''
        Provides the content type decode for the request.
        '''
        assert isinstance(chain, Chain), 'Invalid processors chain %s' % chain
        assert isinstance(request, HTTPDecode), 'Invalid request %s' % request
        assert isinstance(response, Response), 'Invalid response %s' % response
        assert isinstance(requestCnt, _ContentRequest), 'Invalid request content %s' % requestCnt
        assert isinstance(request.decoderHeader, IDecoderHeader), 'Invalid header decoder %s' % request.decoderHeader

        value = request.decoderHeader.decode(self.nameContentType)
        if value:
            if len(value) > 1:
                response.code, response.text = INVALID_HEADER_VALUE, 'Invalid %s' % self.nameContentType
                response.message = 'Invalid value \'%s\' for header \'%s\''\
                ', expected only one value entry' % (value, self.nameContentType)
                return
            value, attributes = value[0]
            requestCnt.type = value
            requestCnt.typeAttr = attributes
            requestCnt.charSet = attributes.get(self.attrContentTypeCharSet, requestCnt.charSet)

        chain.proceed()
