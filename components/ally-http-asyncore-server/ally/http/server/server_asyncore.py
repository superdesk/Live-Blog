'''
Created on Jul 8, 2011

@package: ally http
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the asyncore web server based on the python build in http server and asyncore package.
'''

from ally.container.ioc import injected
from ally.design.processor.assembly import Assembly
from ally.design.processor.attribute import optional
from ally.design.processor.execution import Chain, Processing
from ally.http.spec.server import RequestHTTP, ResponseHTTP, RequestContentHTTP, \
    ResponseContentHTTP, HTTP
from ally.support.util_io import IInputStream, readGenerator
from asyncore import dispatcher, loop
from collections import Callable, deque
from http.server import BaseHTTPRequestHandler
from io import BytesIO
from urllib.parse import urlparse, parse_qsl
import logging
import socket

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# Constants used in indicating the write option. 
WRITE_BYTES = 1
WRITE_ITER = 2
WRITE_CLOSE = 3

# --------------------------------------------------------------------

class RequestContentHTTPAsyncore(RequestContentHTTP):
    '''
    The request content context.
    '''
    # ---------------------------------------------------------------- Optional
    contentReader = optional(Callable, doc='''
    @rtype: Callable
    The content reader callable used for pushing data from the asyncore read. Once the reader is finalized it will
    return a chain that is used for further request processing.
    ''')

# --------------------------------------------------------------------

class RequestHandler(dispatcher, BaseHTTPRequestHandler):
    '''
    Request handler implementation based on @see: async_chat and @see: BaseHTTPRequestHandler.
    The async chat request handler. It relays for the HTTP processing on the @see: BaseHTTPRequestHandler,
    and uses the async_chat to asynchronous communication.
    '''
    
    bufferSize = 10 * 1024
    # The buffer size used for reading and writing.
    maximumRequestSize = 100 * 1024
    # The maximum request size, 100 kilobytes
    requestTerminator = b'\r\n\r\n'
    # Terminator that signals the http request is complete 

    def __init__(self, request, address, server):
        '''
        Construct the request handler.
        
        @param request: socket
            The connection request socket.
        @param address: tuple(string, integer)
            The client address.
        @param server: AsyncServer
            The server that created the request.
        '''
        assert isinstance(server, AsyncServer), 'Invalid server %s' % server
        assert isinstance(address, tuple), 'Invalid address %s' % address
        dispatcher.__init__(self, request, map=server.map)
        
        self.client_address = address
        self.request = self.connection = request
        self.server = server
        
        self.server_version = server.serverVersion
        self.request_version = 'HTTP/1.1'
        self.requestline = 0
        
        self._stage = 1
        self.rfile = BytesIO()
        self._readCarry = None
        self._reader = None

        self.wfile = BytesIO()
        self._writeq = deque()
        
        self._next(1)
        
    def handle_read(self):
        '''
        @see: dispatcher.handle_read
        '''
        try: data = self.recv(self.bufferSize)
        except socket.error:
            log.exception('Exception occurred while reading the content from \'%s\'' % self.connection)
            self.close()
            return
        self.handle_data(data)
    
    def handle_error(self):
        log.exception('A problem occurred in the server')
    
    def end_headers(self):
        '''
        @see: BaseHTTPRequestHandler.end_headers
        '''
        super().end_headers()
        self._writeq.append((WRITE_BYTES, memoryview(self.wfile.getvalue())))
        self.wfile = None

    def log_message(self, format, *args):
        '''
        @see: BaseHTTPRequestHandler.log_message
        '''
        # TODO: see for a better solution for this, check for next python release
        # This is a fix: whenever a message is logged there is an attempt to find some sort of host name which
        # creates a big delay whenever the request is made from a non localhost client.
        assert log.debug(format, *args) or True
        
    # ----------------------------------------------------------------
    
    def _next(self, stage):
        '''
        Proceed to next stage.
        '''
        assert isinstance(stage, int), 'Invalid stage %s' % stage
        self.readable = getattr(self, '_%s_readable' % stage, None)
        self.handle_data = getattr(self, '_%s_handle_data' % stage, None)
        self.writable = getattr(self, '_%s_writable' % stage, None)
        self.handle_write = getattr(self, '_%s_handle_write' % stage, None)
          
    # ----------------------------------------------------------------
    
    def _1_readable(self):
        '''
        @see: dispatcher.readable
        '''
        return True
    
    def _1_handle_data(self, data):
        '''
        Handle the data as being part of the request.
        '''
        if self._readCarry is not None: data = self._readCarry + data
        index = data.find(self.requestTerminator)
        requestTerminatorLen = len(self.requestTerminator)
        
        if index >= 0:
            index += requestTerminatorLen 
            self.rfile.write(data[:index])
            self.rfile.seek(0)
            self.raw_requestline = self.rfile.readline()
            self.parse_request()
            self.rfile = None
            
            self._process(self.command or '')
            
            if index < len(data) and self.handle_data: self.handle_data(data[index:])
        else:
            self._readCarry = data[-requestTerminatorLen:]
            self.rfile.write(data[:-requestTerminatorLen])
            
            if self.rfile.tell() > self.maximumRequestSize:
                self.send_response(400, 'Request to long')
                self.end_headers()
                self.close()
                
    def _1_writable(self):
        '''
        @see: dispatcher.writable
        '''
        return False
        
    # ----------------------------------------------------------------
    
    def _2_readable(self):
        '''
        @see: dispatcher.readable
        '''
        return self._reader is not None
    
    def _2_handle_data(self, data):
        '''
        Handle the data as being part of the request.
        '''
        assert self._reader is not None, 'No reader available'
        chain = self._reader(data)
        if chain is not None:
            assert isinstance(chain, Chain), 'Invalid chain %s' % chain
            self._reader = None
            self._next(3)  # Now we proceed to write stage
            chain.doAll()
            
    def _2_writable(self):
        '''
        @see: dispatcher.writable
        '''
        return False
            
    # ----------------------------------------------------------------

    def _3_readable(self):
        '''
        @see: dispatcher.readable
        '''
        return False
            
    def _3_writable(self):
        '''
        @see: dispatcher.writable
        '''
        return bool(self._writeq)
    
    def _3_handle_write(self):
        '''
        @see: dispatcher.handle_write
        '''
        assert self._writeq, 'Nothing to write'
        
        what, content = self._writeq[0]
        assert what in (WRITE_ITER, WRITE_BYTES, WRITE_CLOSE), 'Invalid what %s' % what
        if what == WRITE_ITER:
            try: data = memoryview(next(content))
            except StopIteration:
                del self._writeq[0]
                return
        elif what == WRITE_BYTES: data = content
        elif what == WRITE_CLOSE:
            self.close()
            return
        
        dataLen = len(data)
        try:
            if dataLen > self.bufferSize: sent = self.send(data[:self.bufferSize])
            else: sent = self.send(data)
        except socket.error:
            log.exception('Exception occurred while writing to the connection \'%s\'' % self.connection)
            self.close()
            return
        if sent < dataLen:
            if what == WRITE_ITER: self._writeq.appendleft((WRITE_BYTES, data[sent:]))
            elif what == WRITE_BYTES: self._writeq[0] = (WRITE_BYTES, data[sent:])
        else:
            if what == WRITE_BYTES: del self._writeq[0]
        
    # ----------------------------------------------------------------
    
    def _process(self, method):
        assert isinstance(method, str), 'Invalid method %s' % method
        proc = self.server.processing
        assert isinstance(proc, Processing), 'Invalid processing %s' % proc
        
        request, requestCnt = proc.ctx.request(), proc.ctx.requestCnt()
        assert isinstance(request, RequestHTTP), 'Invalid request %s' % request
        assert isinstance(requestCnt, RequestContentHTTP), 'Invalid request content %s' % requestCnt
        
        url = urlparse(self.path)
        request.scheme, request.method = HTTP, method.upper()
        request.headers = dict(self.headers)
        request.uri = url.path.lstrip('/')
        request.parameters = parse_qsl(url.query, True, False)
        
        requestCnt.source = self.rfile
        
        chain = Chain(proc)
        chain.process(request=request, requestCnt=requestCnt,
                      response=proc.ctx.response(), responseCnt=proc.ctx.responseCnt())
        
        def respond():
            response, responseCnt = chain.arg.response, chain.arg.responseCnt
            assert isinstance(response, ResponseHTTP), 'Invalid response %s' % response
            assert isinstance(responseCnt, ResponseContentHTTP), 'Invalid response content %s' % responseCnt
    
            if ResponseHTTP.headers in response and response.headers is not None:
                for name, value in response.headers.items(): self.send_header(name, value)
    
            assert isinstance(response.status, int), 'Invalid response status code %s' % response.status
            if ResponseHTTP.text in response and response.text: text = response.text
            elif ResponseHTTP.code in response and response.code: text = response.code
            else: text = None
            self.send_response(response.status, text)
            self.end_headers()
    
            if ResponseContentHTTP.source in responseCnt and responseCnt.source is not None:
                if isinstance(responseCnt.source, IInputStream): source = readGenerator(responseCnt.source, self.bufferSize)
                else: source = responseCnt.source
                self._writeq.append((WRITE_ITER, iter(source)))
                
            self._writeq.append((WRITE_CLOSE, None))
            
        chain.callBack(respond)
        
        while True:
            if not chain.do():
                self._next(3)  # Now we proceed to write stage
                break
            if RequestContentHTTPAsyncore.contentReader in requestCnt and requestCnt.contentReader is not None:
                self._next(2)  # Now we proceed to read stage
                self._reader = requestCnt.contentReader
                break

# --------------------------------------------------------------------

@injected
class AsyncServer(dispatcher):
    '''
    The asyncore server handling the connection.
    '''
    
    serverVersion = str
    # The server version name
    serverHost = str
    # The server address host
    serverPort = int
    # The server port
    requestHandlerFactory = RequestHandler
    # The factory that provides request handlers, takes as arguments the server, request socket
    # and client address.
    assembly = Assembly
    # The assembly used for resolving the requests
    
    timeout = 10.0
    # The timeout for select loop.

    def __init__(self):
        '''
        Construct the server.
        '''
        assert isinstance(self.serverVersion, str), 'Invalid server version %s' % self.serverVersion
        assert isinstance(self.serverHost, str), 'Invalid server host %s' % self.serverHost
        assert isinstance(self.serverPort, int), 'Invalid server port %s' % self.serverPort
        assert callable(self.requestHandlerFactory), 'Invalid request handler factory %s' % self.requestHandlerFactory
        assert isinstance(self.assembly, Assembly), 'Invalid assembly %s' % self.assembly
        assert isinstance(self.timeout, float), 'Invalid timeout %s' % self.timeout
        self.map = {}
        dispatcher.__init__(self, map=self.map)

        self.processing = self.assembly.create(request=RequestHTTP, requestCnt=RequestContentHTTPAsyncore,
                                               response=ResponseHTTP, responseCnt=ResponseContentHTTP)
        
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind((self.serverHost, self.serverPort))
        self.listen(1024)  # lower this to 5 if your OS complains

    def handle_accept(self):
        '''
        @see: dispatcher.handle_accept
        '''
        try:
            request, address = self.accept()
        except socket.error:
            log.exception('A problem occurred while waiting connections')
            return
        except TypeError:
            log.exception('A EWOULDBLOCK problem occurred while waiting connections')
            return
        # creates an instance of the handler class to handle the request/response
        # on the incoming connection
        self.requestHandlerFactory(request, address, self)
    
    def serve_forever(self):
        '''
        Loops and servers the connections.
        '''
        loop(self.timeout, map=self.map)
            
    def serve_limited(self, count):
        '''
        For profiling purposes.
        Loops the provided amount of times and servers the connections.
        '''
        loop(self.timeout, True, self.map, count)

# --------------------------------------------------------------------

def run(server):
    '''
    Run the asyncore server.
    
    @param server: AsyncServer
        The asyncore server to run.
    '''
    assert isinstance(server, AsyncServer), 'Invalid server %s' % server
        
    try:
        log.info('=' * 50 + ' Started Async HTTP server...')
        server.serve_forever()
    except KeyboardInterrupt:
        log.info('=' * 50 + ' ^C received, shutting down server')
        server.close()
    except:
        log.exception('=' * 50 + ' The server has stooped')
        try: server.close()
        except: pass
        
