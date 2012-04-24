'''
Created on Apr 23, 2012

@package: ally core http
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the multipart content handling based on RFC1341.
@see: http://www.w3.org/Protocols/rfc1341/7_2_Multipart.html
'''

from .header import HeaderHTTPBase
from ally.container.ioc import injected
from ally.core.http.impl.processor.header import VALUE_ATTRIBUTES
from ally.core.http.spec import RequestHTTP, INVALID_HEADER_VALUE, \
    ContentRequestHTTP
from ally.core.spec.server import Processor, ProcessorsChain, Response
from ally.exception import DevelError
from collections import OrderedDict
from io import BytesIO
import codecs
import logging
import re

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

@injected
class DecodingMultiPartHandler(HeaderHTTPBase, Processor):
    '''
    Provides the multipart content handler processor.
    @see: http://www.w3.org/Protocols/rfc1341/7_2_Multipart.html
    
    Provides on request: req.content, req.content.contentType, req.content.contentTypeAttributes,
                         req.content.contentDisposition, req.content.contentDispositionAttributes
    Provides on response: NA
    
    Requires on request: req.content, req.content.contentType, req.content.contentTypeAttributes
    Requires on response: NA
    '''

    regexMultipart = '^multipart($|\/.)'
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
    nameContentDisposition = 'Content-Disposition'
    # The header name where the content disposition is set.
    nameContentType = 'Content-Type'
    # The header name where the content type is specified.
    attrContentTypeCharSet = 'charset'
    # The name of the content type attribute where the character set is provided.
    packageSize = 1024
    # The maximum package size to be read in one go.

    def __init__(self):
        super().__init__()
        assert isinstance(self.regexMultipart, str), 'Invalid multipart regex %s' % self.regexMultipart
        assert isinstance(self.attrBoundary, str), 'Invalid attribute boundary name %s' % self.attrBoundary
        assert isinstance(self.charSet, str), 'Invalid character set %s' % self.charSet
        assert isinstance(self.formatMarkSeparator, str), 'Invalid format separator %s' % self.formatMarkSeparator
        assert isinstance(self.formatMarkEnd, str), 'Invalid format end %s' % self.formatMarkEnd
        assert isinstance(self.markHeaderEnd, str), 'Invalid header end %s' % self.markHeaderEnd
        assert isinstance(self.trimBodyAtEnd, str), 'Invalid trim body at end %s' % self.trimBodyAtEnd
        assert isinstance(self.nameContentDisposition, str), \
        'Invalid content disposition header name %s' % self.nameContentDisposition
        assert isinstance(self.nameContentType, str), 'Invalid content type header name %s' % self.nameContentType
        assert isinstance(self.attrContentTypeCharSet, str), \
        'Invalid char set attribute name %s' % self.attrContentTypeCharSet
        self.readFromParams = False # We don't have any parameters for multipart content.
        self._reMultipart = re.compile(self.regexMultipart)

    def process(self, req, rsp, chain):
        '''
        @see: Processor.process
        '''
        assert isinstance(req, RequestHTTP), 'Invalid request %s' % req
        assert isinstance(chain, ProcessorsChain), 'Invalid processors chain %s' % chain
        assert isinstance(rsp, Response), 'Invalid response %s' % rsp
        content = req.content

        if isinstance(content, ContentRequestHTTP):
            assert isinstance(content, ContentRequestHTTP)
            if content.contentType and self._reMultipart.match(content.contentType):
                assert log.debug('Content type %s is multipart', content.contentType) or True
                boundary = content.contentTypeAttributes.pop(self.attrBoundary, None)
                if not boundary:
                    rsp.setCode(INVALID_HEADER_VALUE, 'Multipart boundary expected')
                    return

                req.content = self._createContentMultipart(content, boundary)

        chain.proceed()

    def _createContentMultipart(self, content, boundary):
        '''
        Create the multi part content.
        '''
        return ContentMultipart(self, content, boundary)

# --------------------------------------------------------------------

class ContentMultipart(ContentRequestHTTP):
    '''
    Provides the mutipart content.
    '''

    FLAG_CONTENT_END = 1 << 0
    FLAG_MARK_SEPARATOR = 1 << 1
    FLAG_MARK_END = 1 << 2
    FLAG_HEADER_END = 1 << 3
    FLAG_CLOSED = 1 << 4

    FLAG_MARK = FLAG_MARK_SEPARATOR | FLAG_MARK_END
    FLAG_END = FLAG_CONTENT_END | FLAG_MARK

    def __init__(self, handler, content, boundary):
        '''
        Constructs the multipart content instance.
        
        @see: ContentRequestHTTP.__init__
        
        @param handler: DecodingMultiPartHandler
            The handler from where the multipart content originated.
        @param content: ContentRequestHTTP
            The content that contains the multipart.
        @param boundary: string
            The boundary used for identifying the multipart bodies.
        '''
        assert isinstance(handler, DecodingMultiPartHandler), 'Invalid handler %s' % handler
        assert isinstance(content, ContentRequestHTTP), 'Invalid content %s' % content
        assert isinstance(boundary, str), 'Invalid boundary %s' % boundary
        super().__init__()
        self.contentLanguage = content.contentLanguage
        self.contentConverter = content.contentConverter
        self.objFormat = content.objFormat

        self.contentDisposition = None
        self.contentDispositionAttributes = OrderedDict()

        self._handler = handler
        self._content = content

        self._markSeparator = bytes(handler.formatMarkSeparator % boundary, handler.charSet)
        self._markEnd = bytes(handler.formatMarkEnd % boundary, handler.charSet)
        self._markHeader = bytes(handler.markHeaderEnd, handler.charSet)
        self._trimBody = bytes(handler.trimBodyAtEnd, handler.charSet)
        self._extraSize = max(len(self._markSeparator), len(self._markEnd), len(self._markHeader))

        self._flag = 0
        self._buffer = bytearray()

        while True:
            self._readToSeparator(handler.packageSize)
            if self._flag & self.FLAG_MARK_SEPARATOR: break
            if self._flag & self.FLAG_END:
                raise DevelError('No boundary found in multipart content')

        self._processHeaders()
        self._flag ^= self.FLAG_MARK_SEPARATOR

    def read(self, nbytes=None):
        '''
        @see: ContentRequestHTTP.read
        '''
        handler = self._handler
        assert isinstance(handler, DecodingMultiPartHandler)

        if self._flag & self.FLAG_CLOSED: raise ValueError('I/O operation on a closed content file')
        if self._flag & self.FLAG_END: return b''

        if nbytes:
            if nbytes <= handler.packageSize:
                return self._readToSeparator(nbytes)
            else:
                data = bytearray()
                while True:
                    data.extend(self._readToSeparator(min(nbytes - len(data), handler.packageSize)))
                    if len(data) >= nbytes or self._flag & self.FLAG_END: break
        else:
            data = bytearray()
            while True:
                data.extend(self._readToSeparator(handler.packageSize))
                if self._flag & self.FLAG_END: break

        return data

    def close(self):
        '''
        @see: ContentRequestHTTP.close
        '''
        self._flag |= self.FLAG_CLOSED

    def next(self):
        '''
        @see: ContentRequestHTTP.next
        '''
        if not self._flag & (self.FLAG_CONTENT_END | self.FLAG_MARK_END):
            if not self._flag | self.FLAG_MARK_SEPARATOR:
                handler = self._handler
                assert isinstance(handler, DecodingMultiPartHandler)
                while True:
                    self._readToSeparator(handler.packageSize)
                    if self._flag & self.FLAG_MARK_SEPARATOR: break
                    if self._flag & self.FLAG_END: return
            self._processHeaders()
            self._flag ^= self.FLAG_MARK_SEPARATOR
            if self._flag & self.FLAG_CLOSED: self._flag ^= self.FLAG_CLOSED
            return self

    # ----------------------------------------------------------------

    def _readInBuffer(self, nbytes):
        '''
        Reads in the instance buffer the specified number of bytes, always when reading it will read in the buffer
        additional bytes for the mark processing. It will adjust the flags if END is encountered.
        '''
        assert not self._flag & self.FLAG_CONTENT_END, 'End reached, cannot read anymore'
        data = self._content.read(nbytes + self._extraSize - len(self._buffer))
        if not data: self._flag |= self.FLAG_CONTENT_END
        else: self._buffer.extend(data)

    def _readToSeparator(self, nbytes):
        '''
        Read the provided number of bytes or read until a mark separator is encountered (including the end separator).
        It will adjust the flags according to the findings.
        
        @return: bytes
            The bytes read.
        '''
        assert not self._flag & self.FLAG_MARK, 'Already at a mark, cannot read until flag is reset'

        self._readInBuffer(nbytes)

        buffer = self._buffer
        if not buffer: return b''
        indexSep = buffer.find(self._markSeparator)
        if indexSep >= 0:
            self._flag |= self.FLAG_MARK_SEPARATOR
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
            self._flag |= self.FLAG_MARK_END
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
        assert not self._flag & self.FLAG_HEADER_END, 'Already at header end, cannot read until flag is reset'

        self._readInBuffer(nbytes)

        buffer = self._buffer
        if not buffer: return b''
        indexHeader = buffer.find(self._markHeader)
        if indexHeader >= 0:
            self._flag |= self.FLAG_HEADER_END
            data = buffer[:indexHeader]
            del buffer[:indexHeader + len(self._markHeader)]
        else:
            nbytes = max(len(self._buffer), nbytes)
            data = buffer[:nbytes]
            del buffer[:nbytes]

        return data

    def _processHeaders(self):
        '''
        Processes the multipart headers and update the content with them, it will leave the content stream attached to
        the header reader at the body begin.
        '''
        assert self._flag & self.FLAG_MARK_SEPARATOR, 'Not at a separator mark position, cannot process headers'
        handler = self._handler
        assert isinstance(handler, DecodingMultiPartHandler)

        data = bytearray()
        while True:
            data.extend(self._readToHeader(handler.packageSize))
            if self._flag & self.FLAG_HEADER_END:
                self._flag ^= self.FLAG_HEADER_END # Clearing the header flag
                break
            if self._flag & self.FLAG_CONTENT_END: raise DevelError('No empty line after multipart header')

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
            self.charSet = attributes.pop(handler.attrContentTypeCharSet, self._content.charSet)
            self.contentTypeAttributes.update(attributes)
        else:
            self.contentType = None
            self.charSet = self._content.charSet

