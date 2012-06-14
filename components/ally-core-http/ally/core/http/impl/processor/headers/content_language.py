'''
Created on Jun 12, 2012

@package: ally core http
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the content language header decoding.
'''

from ally.api.type import Locale
from ally.container.ioc import injected
from ally.core.http.spec.server import IDecoderHeader, IEncoderHeader
from ally.design.context import Context, requires, defines, optional
from ally.design.processor import Handler, processor, Chain

# --------------------------------------------------------------------

class Request(Context):
    '''
    The request context.
    '''
    # ---------------------------------------------------------------- Required
    decoderHeader = requires(IDecoderHeader)
    # ---------------------------------------------------------------- Optional
    argumentsOfType = optional(dict)

class RequestContent(Context):
    '''
    The request content context.
    '''
    # ---------------------------------------------------------------- Defined
    language = defines(str, doc='''
    @rtype: string
    The language for the content.
    ''')

class Response(Context):
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
    language = requires(str)

# --------------------------------------------------------------------

@injected
class ContentLanguageHandler(Handler):
    '''
    Implementation for a processor that provides the decoding of content language HTTP request header.
    '''

    nameContentLanguage = 'Content-Language'
    # The header name for the content language.

    def __init__(self):
        assert isinstance(self.nameContentLanguage, str), 'Invalid content language name %s' % self.nameContentLanguage

    @processor
    def decode(self, chain, request:Request, requestCnt:RequestContent, **keyargs):
        '''
        Provides the content language decode for the request.
        '''
        assert isinstance(chain, Chain), 'Invalid processors chain %s' % chain
        assert isinstance(request, Request), 'Invalid request %s' % request
        assert isinstance(requestCnt, RequestContent), 'Invalid request content %s' % requestCnt
        assert isinstance(request.decoderHeader, IDecoderHeader), 'Invalid header decoder %s' % request.decoderHeader

        value = request.decoderHeader.retrieve(self.nameContentLanguage)
        if value:
            requestCnt.language = value
            if Request.argumentsOfType in request: request.argumentsOfType[Locale] = value

        chain.proceed()

    @processor
    def encode(self, chain, response:Response, responseCnt:ResponseContent, **keyargs):
        '''
        Encodes the content language.
        '''
        assert isinstance(chain, Chain), 'Invalid processors chain %s' % chain
        assert isinstance(response, Response), 'Invalid response %s' % response
        assert isinstance(responseCnt, ResponseContent), 'Invalid response content %s' % responseCnt
        assert isinstance(response.encoderHeader, IEncoderHeader), \
        'Invalid response header encoder %s' % response.encoderHeader

        if ResponseContent.language in responseCnt:
            response.encoderHeader.encode(self.nameContentLanguage, responseCnt.language)

        chain.proceed()
