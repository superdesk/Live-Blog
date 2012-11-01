'''
Created on Aug 30, 2012

@package: ally core http
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the multipart content parsing based on RFC1341.
@see: http://www.w3.org/Protocols/rfc1341/7_2_Multipart.html
'''

from ally.container.ioc import injected
from ally.core.http.spec.codes import INVALID_HEADER_VALUE
from ally.core.impl.processor.parsing import ParsingHandler, Request, \
    RequestContent, Response
from ally.core.spec.codes import BAD_CONTENT
from ally.design.context import requires, defines, Context
from ally.design.processor import Chain, Assembly, Processing, \
    NO_MISSING_VALIDATION
from ally.exception import DevelError
from ally.support.util_io import IInputStream, IClosable
from collections import Callable
from io import BytesIO
import codecs
import logging
import re

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

# Flags used in describing the status of a multi part stream 
FLAG_CONTENT_END = 1 << 1
FLAG_MARK_START = 1 << 2
FLAG_MARK_END = 1 << 3
FLAG_HEADER_END = 1 << 4
FLAG_CLOSED = 1 << 5
FLAG_MARK = FLAG_MARK_START | FLAG_MARK_END
FLAG_END = FLAG_CONTENT_END | FLAG_MARK

# --------------------------------------------------------------------

class RequestPopulate(Context):
    '''
    The request context used in populating the request content.
    '''
    # ---------------------------------------------------------------- Defines
    headers = defines(dict, doc='''
    @rtype: dictionary{string, string}
    The raw headers.
    ''')

class RequestContentMultiPart(RequestContent):
    '''
    The request content context.
    '''
    # ---------------------------------------------------------------- Required
    typeAttr = requires(dict)
    source = requires(IInputStream)
    # ---------------------------------------------------------------- Defines
    fetchNextContent = defines(Callable, doc='''
    @rtype: callable()
    The callable used to fetch the next request content, only use this after you have finalized the work with the
    current request content. It will not take any argument.
    ''')
    previousContent = defines(object, doc='''
    @rtype: RequestContentMultiPart
    The reference to the previous content, this will be available only after the fetch method has been used.
    ''')

# --------------------------------------------------------------------

@injected
class DataMultiPart:
    '''
    Contains the data required by the multi part stream.
    '''
    charSet = 'ASCII'
    # The character set used in decoding the multi part header areas.
    formatMarkStart = '--%s\r\n'
    # The format used in constructing the separator marker between the multi part content.
    formatMarkEnd = '--%s--\r\n'
    # The format used in constructing the end marker for the content.
    markHeaderEnd = '\r\n\r\n'
    # Provides the marker for the end of the headers in a multi part body.
    trimBodyAtEnd = '\r\n'
    # Characters to be removed from the multi part body end, if found.
    separatorHeader = ':'
    # Mark used to separate the header from the value, only the first occurrence is considered.
    packageSize = 1024
    # The maximum package size to be read in one go.

    def __init__(self):
        assert isinstance(self.charSet, str), 'Invalid character set %s' % self.charSet
        assert isinstance(self.formatMarkStart, str), 'Invalid format mark start %s' % self.formatMarkStart
        assert isinstance(self.formatMarkEnd, str), 'Invalid format mark end %s' % self.formatMarkEnd
        assert isinstance(self.markHeaderEnd, str), 'Invalid header end %s' % self.markHeaderEnd
        assert isinstance(self.trimBodyAtEnd, str), 'Invalid trim body at end %s' % self.trimBodyAtEnd
        assert isinstance(self.separatorHeader, str), 'Invalid separator header %s' % self.separatorHeader
        assert isinstance(self.packageSize, int), 'Invalid package size %s' % self.packageSize

        self.markHeaderEnd = bytes(self.markHeaderEnd, self.charSet)
        self.trimBodyAtEnd = bytes(self.trimBodyAtEnd, self.charSet)

@injected
class ParsingMultiPartHandler(ParsingHandler, DataMultiPart):
    '''
    Provides the multipart content handler parsing.
    @see: http://www.w3.org/Protocols/rfc1341/7_2_Multipart.html
    '''

    regexMultipart = '^multipart($|\/.)'
    # The regex for the content type value that dictates that the content is multi part.
    attrBoundary = 'boundary'
    # The attribute name that contains the boundary for the multi part.

    populateAssembly = Assembly
    # The processors used for the populating the next request content.

    def __init__(self):
        assert isinstance(self.regexMultipart, str), 'Invalid multi part regex %s' % self.regexMultipart
        assert isinstance(self.attrBoundary, str), 'Invalid attribute boundary name %s' % self.attrBoundary
        assert isinstance(self.populateAssembly, Assembly), 'Invalid populate assembly %s' % self.populateAssembly
        DataMultiPart.__init__(self)
        populateProcessing = self.populateAssembly.create(NO_MISSING_VALIDATION, request=RequestPopulate,
                                                          requestCnt=RequestContentMultiPart, response=Response)
        assert isinstance(populateProcessing, Processing), 'Invalid processing %s' % populateProcessing
        ParsingHandler.__init__(self, requestCnt=populateProcessing.contexts['requestCnt'])
        self.populateProcessing = populateProcessing

        self._reMultipart = re.compile(self.regexMultipart)

    def process(self, chain, request, requestCnt, response, **keyargs):
        '''
        Parse the request content.
        '''
        assert isinstance(chain, Chain), 'Invalid processors chain %s' % chain
        assert isinstance(request, Request), 'Invalid request %s' % request
        assert isinstance(requestCnt, RequestContentMultiPart), 'Invalid request content %s' % requestCnt
        assert isinstance(response, Response), 'Invalid response %s' % response

        chain.proceed()

        if Response.code in response and not response.code.isSuccess: return # Skip in case the response is in error

        isMultipart = requestCnt.type and self._reMultipart.match(requestCnt.type)
        if isMultipart:
            assert log.debug('Content type %s is multi part', requestCnt.type) or True
            boundary = requestCnt.typeAttr.pop(self.attrBoundary, None)
            if not boundary:
                response.code, response.text = INVALID_HEADER_VALUE, 'Multi part boundary expected'
                return

            assert isinstance(requestCnt.source, IInputStream), 'Invalid request content source %s' % requestCnt.source
            stream = StreamMultiPart(self, requestCnt.source, boundary)
            requestCnt = NextContent(requestCnt, response, self.populateProcessing, self, stream)()
            if requestCnt is None:
                response.code, response.text = BAD_CONTENT, 'No boundary found in multi part content'
                return

        if Request.decoder not in request:
            if isMultipart: chain.update(requestCnt=requestCnt)
            return # Skip if there is no decoder.

        if self.processParsing(request=request, requestCnt=requestCnt, response=response, **keyargs):
            # We process the chain without the request content anymore
            if RequestContentMultiPart.fetchNextContent in requestCnt:
                nextContent = requestCnt.fetchNextContent()
                if nextContent is not None:
                    assert isinstance(nextContent, RequestContentMultiPart), 'Invalid request content %s' % nextContent
                    chain.update(requestCnt=nextContent)
        else: chain.update(requestCnt=requestCnt)

# --------------------------------------------------------------------

class StreamMultiPart(IInputStream, IClosable):
    '''
    Provides the muti part stream content.
    '''
    __slots__ = ('_data', '_stream', '_markStart', '_markEnd', '_extraSize', '_flag', '_buffer')

    def __init__(self, data, stream, boundary):
        '''
        Constructs the multi part content stream.
        
        @param data: DataMultiPart
            The data used for multi part content processing.
        @param stream: IInputStream
            The stream that contains the multi part.
        @param boundary: string
            The boundary used for identifying the multi part bodies.
        '''
        assert isinstance(data, DataMultiPart), 'Invalid data %s' % data
        assert isinstance(stream, IInputStream), 'Invalid content stream %s' % stream
        assert isinstance(boundary, str), 'Invalid boundary %s' % boundary

        self._data = data
        self._stream = stream

        self._markStart = bytes(data.formatMarkStart % boundary, data.charSet)
        self._markEnd = bytes(data.formatMarkEnd % boundary, data.charSet)
        self._extraSize = max(len(self._markStart), len(self._markEnd), len(data.markHeaderEnd))

        self._flag = 0
        self._buffer = bytearray()

    def read(self, nbytes=None):
        '''
        @see: IInputStream.read
        '''
        if self._flag & FLAG_CLOSED: raise ValueError('I/O operation on a closed content file')
        if self._flag & FLAG_END: return b''

        if nbytes:
            if nbytes <= self._data.packageSize:
                return self._readToMark(nbytes)
            else:
                data = bytearray()
                while True:
                    data.extend(self._readToMark(min(nbytes - len(data), self._data.packageSize)))
                    if len(data) >= nbytes or self._flag & FLAG_END: break
        else:
            data = bytearray()
            while True:
                data.extend(self._readToMark(self._data.packageSize))
                if self._flag & FLAG_END: break

        return bytes(data)

    def close(self):
        '''
        @see: IClosable.close
        '''
        self._flag |= FLAG_CLOSED

    # ----------------------------------------------------------------

    def _readInBuffer(self, nbytes):
        '''
        Reads in the instance buffer the specified number of bytes, always when reading it will read in the buffer
        additional bytes for the mark processing. It will adjust the flags if END is encountered.
        '''
        assert not self._flag & FLAG_CONTENT_END, 'End reached, cannot read anymore'
        data = self._stream.read(nbytes + self._extraSize - len(self._buffer))
        if data: self._buffer.extend(data)
        if not self._buffer: self._flag |= FLAG_CONTENT_END

    def _readToMark(self, nbytes):
        '''
        Read the provided number of bytes or read until a mark separator is encountered (including the end separator).
        It will adjust the flags according to the findings.
        
        @return: bytes
            The bytes read.
        '''
        assert not self._flag & FLAG_MARK, 'Already at a mark, cannot read until flag is reset'

        self._readInBuffer(nbytes)

        if not self._buffer: return b''
        indexSep = self._buffer.find(self._markStart)
        if indexSep >= 0:
            self._flag |= FLAG_MARK_START
            indexBody = indexSep - len(self._data.trimBodyAtEnd)
            if not self._buffer.endswith(self._data.trimBodyAtEnd, indexBody, indexSep): indexBody = indexSep
            data = self._buffer[:indexBody]
            del self._buffer[:indexSep + len(self._markStart)]
        else:
            nbytes = max(len(self._buffer), nbytes)
            data = self._buffer[:nbytes]
            del self._buffer[:nbytes]

        indexEnd = data.find(self._markEnd)
        if indexEnd >= 0:
            self._flag |= FLAG_MARK_END
            indexBody = indexEnd - len(self._data.trimBodyAtEnd)
            if not data.endswith(self._data.trimBodyAtEnd, indexBody, indexEnd): indexBody = indexEnd
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
        assert not self._flag & FLAG_HEADER_END, 'Already at header end, cannot read until flag is reset'

        self._readInBuffer(nbytes)

        if not self._buffer: return b''
        indexHeader = self._buffer.find(self._data.markHeaderEnd)
        if indexHeader >= 0:
            self._flag |= FLAG_HEADER_END
            data = self._buffer[:indexHeader]
            del self._buffer[:indexHeader + len(self._data.markHeaderEnd)]
        else:
            nbytes = max(len(self._buffer), nbytes)
            data = self._buffer[:nbytes]
            del self._buffer[:nbytes]

        return data

    def _pullHeaders(self):
        '''
        Pull the multi part headers, it will leave the content stream attached to the header reader at the body begin.
        
        @return: dictionary{string, string}
            The multi part headers.
        '''
        assert self._flag & FLAG_MARK_START, 'Not at a separator mark position, cannot process headers'

        data = bytearray()
        while True:
            data.extend(self._readToHeader(self._data.packageSize))
            if self._flag & FLAG_HEADER_END:
                self._flag ^= FLAG_HEADER_END # Clearing the header flag
                break
            if self._flag & FLAG_CONTENT_END: raise DevelError('No empty line after multi part header')

        reader = codecs.getreader(self._data.charSet)(BytesIO(data))
        headers = {}
        while True:
            line = reader.readline()
            if line == '':  break
            hindex = line.find(self._data.separatorHeader)
            if hindex < 0: raise DevelError('Invalid multi part header \'%s\'' % line)
            headers[line[:hindex]] = line[hindex + 1:].strip()

        self._flag ^= FLAG_MARK_START
        return headers

class NextContent:
    '''
    Callable used for processing the next request content.
    '''
    __slots__ = ('_requestCnt', '_response', '_processing', '_data', '_stream', '_nextCnt')

    def __init__(self, requestCnt, response, processing, data, stream):
        '''
        Construct the next callable.
        
        @param requestCnt: RequestContentMultiPart
            The current request content.
        @param response: Response
            The response context.
        @param processing: Processing
            The processing used for populating the next request content.
        @param data: DataMultiPart
            The multi part data.
        @param stream: StreamMultiPart
            The stream that contains the multi part.
        @return: RequestContent
            The next content.
        '''
        assert isinstance(requestCnt, RequestContentMultiPart), 'Invalid request content %s' % requestCnt
        assert isinstance(response, Response), 'Invalid response %s' % response
        assert isinstance(processing, Processing), 'Invalid processing %s' % processing
        assert isinstance(data, DataMultiPart), 'Invalid data %s' % data
        assert isinstance(stream, StreamMultiPart), 'Invalid stream %s' % stream

        self._requestCnt = requestCnt
        self._response = response
        self._processing = processing
        self._data = data
        self._stream = stream

        self._nextCnt = None

    def __call__(self):
        '''
        Provides the next multi part request content based on the provided multi part stream.
        '''
        if self._nextCnt is not None: return self._nextCnt

        stream, processing = self._stream, self._processing
        assert isinstance(stream, StreamMultiPart), 'Invalid stream %s' % stream
        assert isinstance(processing, Processing), 'Invalid processing %s' % processing

        if not stream._flag & (FLAG_CONTENT_END | FLAG_MARK_END):
            if not stream._flag & FLAG_MARK_START:
                while True:
                    stream._readToMark(self._data.packageSize)
                    if stream._flag & FLAG_MARK_START: break
                    if stream._flag & FLAG_END: return

            req = processing.contexts['request']()
            self._nextCnt = reqCnt = processing.contexts['requestCnt']()
            assert isinstance(req, RequestPopulate), 'Invalid request %s' % req
            assert isinstance(reqCnt, RequestContentMultiPart), 'Invalid request content %s' % reqCnt

            req.headers = stream._pullHeaders()
            if stream._flag & FLAG_CLOSED: stream._flag ^= FLAG_CLOSED

            reqCnt.source = stream
            reqCnt.fetchNextContent = NextContent(reqCnt, self._response, self._processing, self._data, stream)
            reqCnt.previousContent = self._requestCnt
            Chain(self._processing).process(request=req, requestCnt=reqCnt, response=self._response).doAll()

            return reqCnt
