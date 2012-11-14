'''
Created on Nov 1, 2012

@package: ally core http
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the asyncore handling of content.
'''

from ally.api.config import INSERT, UPDATE
from ally.container.ioc import injected
from ally.core.spec.codes import Code
from ally.design.context import Context, defines, requires
from ally.design.processor import HandlerProcessor, Chain
from ally.support.util_io import IInputStream
from ally.zip.util_zip import normOSPath
from collections import Callable
from genericpath import isdir
from io import BytesIO
import os
import time

# --------------------------------------------------------------------

class Request(Context):
    '''
    The request context.
    '''
    # ---------------------------------------------------------------- Required
    method = requires(int) 
    
class RequestContent(Context):
    '''
    The request content context.
    '''
    # ---------------------------------------------------------------- Required
    length = requires(int)
    # ---------------------------------------------------------------- Defined
    contentReader = defines(Callable)
    source = defines(IInputStream)

class Response(Context):
    '''
    The response context.
    '''
    # ---------------------------------------------------------------- Defined
    code = defines(Code)
    
# --------------------------------------------------------------------

@injected
class AsyncoreContentHandler(HandlerProcessor):
    '''
    Provides asyncore content handling, basically this handler buffers up the async data received in order to be
    used by the other handlers.
    '''
    contentMethods = {INSERT, UPDATE}
    # The methods that have content.

    dumpRequestsSize = 1024 * 1024
    # The minimum size of the request length to be dumped on the file system.
    dumpRequestsPath = str
    # The path where the requests are dumped when they are to big to keep in memory.
    
    def __init__(self):
        assert isinstance(self.dumpRequestsSize, int), 'Invalid dump size %s' % self.dumpRequestsSize
        assert isinstance(self.dumpRequestsPath, str), 'Invalid dump path %s' % self.dumpRequestsPath
        self.dumpRequestsPath = normOSPath(self.dumpRequestsPath)
        if not os.path.exists(self.dumpRequestsPath): os.makedirs(self.dumpRequestsPath)
        assert isdir(self.dumpRequestsPath) and os.access(self.dumpRequestsPath, os.W_OK), \
        'Unable to access the dump directory %s' % self.dumpRequestsPath
        super().__init__()
        
        self._count = 0

    def process(self, chain, request:Request, requestCnt:RequestContent, response:Response, **keyargs):
        '''
        @see: HandlerProcessor.process
        
        Provide the headers encoders and decoders.
        '''
        assert isinstance(chain, Chain), 'Invalid chain %s' % chain
        assert isinstance(request, Request), 'Invalid request %s' % request
        assert isinstance(requestCnt, RequestContent), 'Invalid request content %s' % requestCnt
        assert isinstance(response, Response), 'Invalid response %s' % response

        if Response.code in response and not response.code.isSuccess: return  # Skip in case the response is in error
        chain.proceed()
        
        if request.method in self.contentMethods:
            if RequestContent.length in requestCnt:
                if requestCnt.length == 0: return
                
                if requestCnt.length > self.dumpRequestsSize:
                    requestCnt.contentReader = ReaderInFile(self._path(), chain, requestCnt)
                else:
                    requestCnt.contentReader = ReaderInMemory(chain, requestCnt)
            else:
                requestCnt.contentReader = ReaderInFile(self._path(), chain, requestCnt)

    # ----------------------------------------------------------------
    
    def _path(self):
        '''
        Provide the path for the request file.
        '''
        tm_year, tm_mon, tm_mday, tm_hour, tm_min, tm_sec, *_rest = time.localtime()
        path = 'request_%s_%s-%s-%s_%s-%s-%s' % (self._count, tm_year, tm_mon, tm_mday, tm_hour, tm_min, tm_sec)
        self._count += 1
        return path

# --------------------------------------------------------------------

class ReaderInMemory:
    '''
    Provides the reader in memory.
    '''
    __slots__ = ('_chain', '_requestCnt', '_stream', '_size')
    
    def __init__(self, chain, requestCnt):
        '''
        Construct the reader.
        
        @param chain: Chain
            The chain that is used for further processing.
        @param requestCnt: RequestContent
            The request content to use the reader with.
        '''
        assert isinstance(chain, Chain), 'Invalid chain %s' % chain
        assert isinstance(requestCnt, RequestContent), 'Invalid request content %s' % requestCnt
        self._chain = chain
        self._requestCnt = requestCnt

        self._stream = BytesIO()
        self._size = 0
        
    def __call__(self, data):
        '''
        Push data into the reader.
        '''
        assert self._stream is not None, 'Reader is finalized'
        if data != b'':
            self._size += len(data)
            length = self._requestCnt.length
            if length is not None:
                if self._size > length:
                    dif = self._size - length
                    self._size = length
                    data = memoryview(data)[:dif]
                self._stream.write(data)
                if self._size == length: data = b''
            else: self._stream.write(data)
            
        if data == b'':
            self._stream.seek(0)
            self._requestCnt.source = self._stream
            self._requestCnt.contentReader = None
            self._stream = None
            return self._chain

class ReaderInFile:
    '''
    Provides the reader in file.
    '''
    __slots__ = ('_chain', '_path', '_requestCnt', '_file', '_size')
    
    def __init__(self, path, chain, requestCnt):
        '''
        Construct the reader.
        
        @param chain: Chain
            The chain that is used for further processing.
        @param requestCnt: RequestContent
            The request content to use the reader with.
        '''
        assert isinstance(path, str), 'Invalid path %s' % path
        assert isinstance(chain, Chain), 'Invalid chain %s' % chain
        assert isinstance(requestCnt, RequestContent), 'Invalid request content %s' % requestCnt
        self._path = path
        self._chain = chain
        self._requestCnt = requestCnt

        self._file = open(path, mode='wb')
        self._size = 0
        
    def __call__(self, data):
        '''
        Push data into the reader.
        '''
        assert self._file is not None, 'Reader is finalized'
        if data != b'':
            self._size += len(data)
            length = self._requestCnt.length
            if length is not None:
                if self._size > length:
                    dif = self._size - length
                    self._size = length
                    data = memoryview(data)[:dif]
                self._file.write(data)
                if self._size == length: data = b''
            else: self._file.write(data)
            
        if data == b'':
            self._file.close()
            self._requestCnt.source = open(self._path, mode='rb')
            self._requestCnt.contentReader = None
            self._file = None
            
            self._chain.callBack(lambda: os.remove(self._path))
            return self._chain
