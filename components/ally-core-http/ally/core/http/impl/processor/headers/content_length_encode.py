'''
Created on Jun 11, 2012

@package: ally core http
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the encoding for the content length header.
'''

from ally.container.ioc import injected
from ally.core.http.spec.extension import HTTPEncode
from ally.core.http.spec.server import IEncoderHeader
from ally.core.spec.server import Content
from ally.design.processor import Handler, Chain, processor

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
    def process(self, chain, response:HTTPEncode, responseCnt:Content, **keyargs):
        '''
        Encodes the content length.
        '''
        assert isinstance(chain, Chain), 'Invalid processors chain %s' % chain
        assert isinstance(response, HTTPEncode), 'Invalid response %s' % response
        assert isinstance(responseCnt, Content), 'Invalid response content %s' % responseCnt
        assert isinstance(response.encoderHeader, IEncoderHeader), \
        'Invalid response header encoder %s' % response.encoderHeader

        if responseCnt.length is not None:
            response.encoderHeader.encode(self.nameContentLength, str(responseCnt.length))

        chain.proceed()
