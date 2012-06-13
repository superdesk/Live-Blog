'''
Created on Jun 11, 2012

@package: ally core http
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the encoding for the content length header.
'''

from ally.container.ioc import injected
from ally.core.http.spec.server import IEncoderHeader
from ally.design.context import Context, requires
from ally.design.processor import Handler, Chain, processor

# --------------------------------------------------------------------

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
    length = requires(int)

# --------------------------------------------------------------------

@injected
class ContentLengthEncodeHandler(Handler):
    '''
    Implementation for a processor that provides the encoding of content length HTTP response header.
    '''

    nameContentLength = 'Content-Length'
    # The name for the content length header

    def __init__(self):
        assert isinstance(self.nameContentLength, str), 'Invalid content length name %s' % self.nameContentLength

    @processor
    def process(self, chain, response:Response, responseCnt:ResponseContent, **keyargs):
        '''
        Encodes the content length.
        '''
        assert isinstance(chain, Chain), 'Invalid processors chain %s' % chain
        assert isinstance(response, Response), 'Invalid response %s' % response
        assert isinstance(responseCnt, ResponseContent), 'Invalid response content %s' % responseCnt
        assert isinstance(response.encoderHeader, IEncoderHeader), \
        'Invalid response header encoder %s' % response.encoderHeader

        if responseCnt.length is not None:
            response.encoderHeader.encode(self.nameContentLength, str(responseCnt.length))

        chain.proceed()
