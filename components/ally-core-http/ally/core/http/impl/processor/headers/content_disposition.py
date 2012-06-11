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
from ally.core.http.spec.extension import HTTPDecode, ContentDisposition
from ally.core.http.spec.server import IDecoderHeader
from ally.core.spec.server import Response
from ally.design.processor import Handler, processor, Chain, ext

# --------------------------------------------------------------------

@injected
class ContentDispositionHandler(Handler):
    '''
    Implementation for a processor that provides the decoding of content disposition HTTP request header.
    '''

    nameContentDisposition = 'Content-Disposition'
    # The header name where the content disposition is set.

    def __init__(self):
        assert isinstance(self.nameContentDisposition, str), \
        'Invalid content disposition header name %s' % self.nameContentDisposition

    @processor
    def process(self, chain, request:HTTPDecode, requestCnt:ext(ContentDisposition), response:Response, **keyargs):
        '''
        Provides the content type decode for the request.
        '''
        assert isinstance(chain, Chain), 'Invalid processors chain %s' % chain
        assert isinstance(request, HTTPDecode), 'Invalid request %s' % request
        assert isinstance(response, Response), 'Invalid response %s' % response
        assert isinstance(requestCnt, ContentDisposition), 'Invalid request content %s' % requestCnt
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
