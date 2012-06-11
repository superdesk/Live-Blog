'''
Created on Jun 11, 2012

@package: ally core http
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the decoding for the content length header.
'''

from ally.container.ioc import injected
from ally.core.http.spec.codes import INVALID_HEADER_VALUE
from ally.core.http.spec.extension import HTTPDecode
from ally.core.http.spec.server import IDecoderHeader
from ally.core.spec.server import Response, Content, IStream
from ally.design.processor import Handler, Chain, processor

# --------------------------------------------------------------------

@injected
class ContentLengthDecodeHandler(Handler):
    '''
    Implementation for a processor that provides the decoding of content length HTTP request header, also wraps
    the source stream in order to enforce the length when reading the source stream.
    '''

    nameContentLength = 'Content-Length'
    # The name for the content length header

    def __init__(self):
        assert isinstance(self.nameContentLength, str), 'Invalid content length name %s' % self.nameContentLength

    @processor
    def process(self, chain, request:HTTPDecode, requestCnt:Content, response:Response, **keyargs):
        '''
        Decodes the request content length also wraps the content source if is the case.
        '''
        assert isinstance(chain, Chain), 'Invalid processors chain %s' % chain
        assert isinstance(request, HTTPDecode), 'Invalid request %s' % request
        assert isinstance(requestCnt, Content), 'Invalid request content %s' % requestCnt
        assert isinstance(response, Response), 'Invalid response %s' % response
        assert isinstance(request.decoderHeader, IDecoderHeader), \
        'Invalid header decoder %s' % request.decoderHeader

        value = request.decoderHeader.retrieve(self.nameContentLength)
        if value:
            try: requestCnt.length = int(value)
            except ValueError:
                response.code, response.text = INVALID_HEADER_VALUE, 'Invalid %s' % self.nameContentLength
                response.message = 'Invalid value \'%s\' for header \'%s\''\
                ', expected an integer value' % (value, self.nameContentLength)
                return
            else: requestCnt.source = StreamLengthLimited(requestCnt.source, requestCnt.length)

        chain.proceed()

# --------------------------------------------------------------------

class StreamLengthLimited(IStream):
    '''
    Provides a class that implements the @see: IStream that limits the reading from another stream based on the
    provided length.
    '''

    def __init__(self, stream, length):
        '''
        Constructs the length limited stream.
        
        @param stream: IStream
            The stream to wrap and provide limited reading from.
        @param length: integer
            The number of bytes to allow the read from the wrapped stream.
        '''
        assert isinstance(stream, IStream), 'Invalid stream %s' % stream
        assert isinstance(length, int), 'Invalid length %s' % length

        self._stream = stream
        self._length = length
        self._closed = False
        self._offset = 0

    def read(self, nbytes=None):
        '''
        @see: IStream.read
        '''
        if self._closed: raise ValueError('I/O operation on a closed content file')
        count = nbytes
        if self._length is not None:
            if self._offset >= self._length:
                return b''
            delta = self._length - self._offset
            if count is None:
                count = delta
            elif count > delta:
                count = delta
        bytes = self._stream.read(count)
        self._offset += len(bytes)
        return bytes

    def close(self):
        '''
        @see: IStream.close
        '''
        self._closed = True
