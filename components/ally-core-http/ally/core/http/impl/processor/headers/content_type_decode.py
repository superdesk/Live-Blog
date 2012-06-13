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
from ally.core.http.spec.server import IDecoderHeader
from ally.design.processor import Handler, processor, Chain
from ally.design.context import Context, requires, defines
from ally.core.spec.codes import Code

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
    typeAttr = defines(str, doc='''
    @rtype: dictionary{string, string}
    The content request type attributes.
    ''')
    charSet = defines(str, doc='''
    @rtype: string
    The character set for the text content.
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
    def process(self, chain, request:Request, requestCnt:RequestContent, response:Response, **keyargs):
        '''
        Provides the content type decode for the request.
        '''
        assert isinstance(chain, Chain), 'Invalid processors chain %s' % chain
        assert isinstance(request, Request), 'Invalid request %s' % request
        assert isinstance(response, Response), 'Invalid response %s' % response
        assert isinstance(requestCnt, RequestContent), 'Invalid request content %s' % requestCnt
        assert isinstance(request.decoderHeader, IDecoderHeader), 'Invalid header decoder %s' % request.decoderHeader

        value = request.decoderHeader.decode(self.nameContentType)
        if value:
            if len(value) > 1:
                response.code, response.text = INVALID_HEADER_VALUE, 'Invalid %s' % self.nameContentType
                response.message = 'Invalid value \'%s\' for header \'%s\''\
                ', expected only one type entry' % (value, self.nameContentType)
                return
            value, attributes = value[0]
            requestCnt.type = value
            requestCnt.typeAttr = attributes
            requestCnt.charSet = attributes.get(self.attrContentTypeCharSet, requestCnt.charSet)

        chain.proceed()
