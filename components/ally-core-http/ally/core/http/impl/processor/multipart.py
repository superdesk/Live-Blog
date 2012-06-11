'''
Created on Apr 23, 2012

@package: ally core http
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the multipart content handling based on RFC1341.
@see: http://www.w3.org/Protocols/rfc1341/7_2_Multipart.html
'''

from ally.container.ioc import injected
from ally.core.http.spec.codes import INVALID_HEADER_VALUE
from ally.core.http.spec.extension import HTTPDecode, ContentType, \
    ContentDisposition
from ally.core.http.spec.server import IDecoderHeader
from ally.core.spec.server import Response, Request, Content, \
    IStream
from ally.exception import DevelError
from io import BytesIO
import codecs
import logging
import re
from ally.design.processor import Handler, Chain, mokup

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

@mokup(Content, ContentType)
class _RequestContent(Content, ContentType, ContentDisposition):
    ''' Used as a mokup class '''

# --------------------------------------------------------------------

@injected
class MultiPartHandler(Handler):
    '''
    Provides the multipart content handler processor.
    @see: http://www.w3.org/Protocols/rfc1341/7_2_Multipart.html
    '''

    patternMultipart = '^multipart($|\/.)'
    # The regex for the content type value that dictates that the content is multipart.
    attrBoundary = 'boundary'
    # The attribute name that contains the boundary for the multipart.
    charSet = 'ASCII'
    # The character set used in decoding the multipart header areas.
    formatMarkSeparator = '--%s\r\n'
    # The format used in constructing the separator marker between the multipart content.
    formatMarkEnd = '--%s--\r\n'
    # The format used in constructing the end marker for the content.
    markHeaderEnd = '\r\n\r\n'
    # Provides the marker for the end of the headers in a multipart body.
    trimBodyAtEnd = '\r\n'
    # Characters to be removed from the multipart body end, if found.

    separatorHeader = ':'
    # Mark used to separate the header from the value, only the first occurrence is considered.
    packageSize = 1024
    # The maximum package size to be read in one go.

    def __init__(self):
        super().__init__()
        assert isinstance(self.patternMultipart, str), 'Invalid multipart pattern %s' % self.patternMultipart
        assert isinstance(self.attrBoundary, str), 'Invalid attribute boundary name %s' % self.attrBoundary
        assert isinstance(self.charSet, str), 'Invalid character set %s' % self.charSet
        assert isinstance(self.formatMarkSeparator, str), 'Invalid format separator %s' % self.formatMarkSeparator
        assert isinstance(self.formatMarkEnd, str), 'Invalid format end %s' % self.formatMarkEnd
        assert isinstance(self.markHeaderEnd, str), 'Invalid header end %s' % self.markHeaderEnd
        assert isinstance(self.trimBodyAtEnd, str), 'Invalid trim body at end %s' % self.trimBodyAtEnd

        self.reMultipart = re.compile(self.patternMultipart)

    def process(self, chain, requestCnt:_RequestContent, response:Response, **keyargs):
        '''
        Process the multipart request.
        '''
        assert isinstance(chain, Chain), 'Invalid processors chain %s' % chain
        assert isinstance(requestCnt, _RequestContent), 'Invalid request %s' % requestCnt
        assert isinstance(response, Response), 'Invalid response %s' % response

        if requestCnt.type and requestCnt.source is not None and self.reMultipart.match(requestCnt.type):
                assert log.debug('Content type %s is multipart', requestCnt.type) or True

                boundary = requestCnt.typeAttr.get(self.attrBoundary)
                if not boundary:
                    response.code, response.text = INVALID_HEADER_VALUE, 'Multipart boundary expected'
                    response.message = 'The multipart boundary is missing for header \'%s\'' % self.nameContentType
                    return

                requestCnt.source = self.createMultiPart(requestCnt.source, boundary)

        chain.proceed()

    def createMultiPart(self, source, boundary):
        '''
        Create the multipart content.
        '''
        return StreamMultipart(self, content, boundary)

# --------------------------------------------------------------------

class MultiPart:
    '''
    The class that provides the multipart processing.
    '''
    CONTENT_END = 1 << 0
    MARK_SEPARATOR = 1 << 1
    MARK_END = 1 << 2
    HEADER_END = 1 << 3
    CLOSED = 1 << 4

    MARK = MARK_SEPARATOR | MARK_END
    END = CONTENT_END | MARK

    def __init__(self, handler, stream, boundary):
        '''
        Constructs the multipart content instance.
        
        @param handler: MultiPartHandler
            The handler from where the multipart content originated.
        @param stream: IStream
            The stream that contains the multipart.
        @param boundary: string
            The boundary used for identifying the multipart bodies.
        '''
        assert isinstance(handler, MultiPartHandler), 'Invalid handler %s' % handler
        assert isinstance(stream, IStream), 'Invalid stream %s' % stream
        assert isinstance(boundary, str), 'Invalid boundary %s' % boundary

        self._handler = handler
        self._stream = stream

        self._markSeparator = bytes(handler.formatMarkSeparator % boundary, handler.charSet)
        self._markEnd = bytes(handler.formatMarkEnd % boundary, handler.charSet)
        self._markHeader = bytes(handler.markHeaderEnd, handler.charSet)
        self._trimBody = bytes(handler.trimBodyAtEnd, handler.charSet)
        self._extraSize = max(len(self._markSeparator), len(self._markEnd), len(self._markHeader))

        self._flag = 0
        self._buffer = bytearray()

        while True:
            self._readToSeparator(handler.packageSize)
            if self._flag & self.MARK_SEPARATOR: break
            if self._flag & self.END: raise DevelError('No boundary found in multipart content')

        self._processHeaders()

    def read(self, nbytes=None):
        '''
        @see: IStream.read
        '''
        packageSize = self._handler.packageSize

        if self._flag & self.CLOSED: raise ValueError('I/O operation on a closed content file')
        if self._flag & self.END: return b''

        if nbytes:
            if nbytes <= packageSize:
                return self._readToSeparator(nbytes)
            else:
                data = bytearray()
                while True:
                    data.extend(self._readToSeparator(min(nbytes - len(data), packageSize)))
                    if len(data) >= nbytes or self._flag & self.END: break
        else:
            data = bytearray()
            while True:
                data.extend(self._readToSeparator(packageSize))
                if self._flag & self.END: break

        return data

    def close(self):
        '''
        @see: IStream.close
        '''
        self._flag |= self.CLOSED

    # ----------------------------------------------------------------

    def processNext(self):
        '''
        Process the next content.
        '''
        if not self._flag & (self.CONTENT_END | self.MARK_END):
            if not self._flag | self.MARK_SEPARATOR:
                packageSize = self._handler.packageSize

                while True:
                    self._readToSeparator(packageSize)
                    if self._flag & self.MARK_SEPARATOR: break
                    if self._flag & self.END: return
            self._processHeaders()
            self._flag ^= self.MARK_SEPARATOR
            if self._flag & self.CLOSED: self._flag ^= self.CLOSED
            return self

    def processHeaders(self, decoder, content):
        '''
        Processes the multipart headers and update the content with them, it will leave the content stream attached to
        the header reader at the body begin.
        
        @param decoder: IDecoderHeader
            The header decoder to use for parsing the headers in the multipart.
        @param content: Content
            The content to process the headers in.
        '''
        assert self._flag & self.MARK_SEPARATOR, 'Not at a separator mark position, cannot process headers'
        assert isinstance(decoder, IDecoderHeader), 'Invalid decoder %s' % decoder
        assert isinstance(content, Content), 'Invalid content %s' % content
        handler = self._handler
        assert isinstance(handler, MultiPartHandler)

        data = bytearray()
        while True:
            data.extend(self._readToHeader(handler.packageSize))
            if self._flag & self.HEADER_END:
                self._flag ^= self.HEADER_END # Clearing the header flag
                break
            if self._flag & self.CONTENT_END: raise DevelError('No empty line after multipart header')

        reader = codecs.getreader(handler.charSet)(BytesIO(data))
        headers = {}
        while True:
            line = reader.readline()
            if line == '':  break
            hindex = line.find(handler.separatorHeader)
            if hindex < 0: raise DevelError('Invalid multipart header \'%s\'' % line)
            headers[line[:hindex]] = line[hindex + 1:].strip()

        p = handler._parse(handler.nameContentDisposition, headers, (), VALUE_ATTRIBUTES)
        self.contentDispositionAttributes.clear()
        if p:
            self.contentDisposition, attributes = p
            self.contentDispositionAttributes.update(attributes)
        else:
            self.contentDisposition = None

        # Parsing the content headers
        p = handler._parse(handler.nameContentType, headers, (), VALUE_ATTRIBUTES)
        self.contentTypeAttributes.clear()
        if p:
            self.contentType, attributes = p
            self.charSet = attributes.pop(handler.attrContentTypeCharSet, self._stream.charSet)
            self.contentTypeAttributes.update(attributes)
        else:
            self.contentType = None
            self.charSet = self._stream.charSet

        self._flag ^= self.MARK_SEPARATOR

    # ----------------------------------------------------------------

    def _readInBuffer(self, nbytes):
        '''
        Reads in the instance buffer the specified number of bytes, always when reading it will read in the buffer
        additional bytes for the mark processing. It will adjust the flags if END is encountered.
        '''
        assert not self._flag & self.CONTENT_END, 'End reached, cannot read anymore'
        data = self._stream.read(nbytes + self._extraSize - len(self._buffer))
        if not data: self._flag |= self.CONTENT_END
        else: self._buffer.extend(data)

    def _readToSeparator(self, nbytes):
        '''
        Read the provided number of bytes or read until a mark separator is encountered (including the end separator).
        It will adjust the flags according to the findings.
        
        @param nbytes: integer
            The number of bytes to read.
        @return: bytes
            The bytes read.
        '''
        assert isinstance(nbytes, int), 'Invalid number of bytes %s' % nbytes
        assert not self._flag & self.MARK, 'Already at a mark, cannot read until flag is reset'

        self._readInBuffer(nbytes)

        buffer = self._buffer
        if not buffer: return b''
        indexSep = buffer.find(self._markSeparator)
        if indexSep >= 0:
            self._flag |= self.MARK_SEPARATOR
            indexBody = indexSep - len(self._trimBody)
            if not buffer.endswith(self._trimBody, indexBody, indexSep): indexBody = indexSep
            data = buffer[:indexBody]
            del buffer[:indexSep + len(self._markSeparator)]
        else:
            nbytes = max(len(buffer), nbytes)
            data = buffer[:nbytes]
            del buffer[:nbytes]

        indexEnd = data.find(self._markEnd)
        if indexEnd >= 0:
            self._flag |= self.MARK_END
            indexBody = indexEnd - len(self._trimBody)
            if not data.endswith(self._trimBody, indexBody, indexEnd): indexBody = indexEnd
            data = data[:indexBody]
            self._buffer = data[indexEnd + len(self._markEnd):]

        return data

    def _readToHeader(self, nbytes):
        '''
        Read the provided number of bytes or read until the mark header is encountered.
        It will adjust the flags according to the findings.
        
        @return: bytes
            The bytes read.
        '''
        assert not self._flag & self.HEADER_END, 'Already at header end, cannot read until flag is reset'

        self._readInBuffer(nbytes)

        buffer = self._buffer
        if not buffer: return b''
        indexHeader = buffer.find(self._markHeader)
        if indexHeader >= 0:
            self._flag |= self.HEADER_END
            data = buffer[:indexHeader]
            del buffer[:indexHeader + len(self._markHeader)]
        else:
            nbytes = max(len(self._buffer), nbytes)
            data = buffer[:nbytes]
            del buffer[:nbytes]

        return data
