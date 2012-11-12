'''
Created on Jul 8, 2011

@package: ally core http
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the asyncore web server based on the python build in http server and asyncore package.
'''

from ally.api.config import GET, INSERT, UPDATE, DELETE
from ally.core.http.spec.server import METHOD_OPTIONS, RequestHTTP, ResponseHTTP, \
    RequestContentHTTP, ResponseContentHTTP
from ally.core.spec.codes import Code
from ally.design.context import optional
from ally.design.processor import Processing, Assembly, ONLY_AVAILABLE, \
    CREATE_REPORT, Chain
from ally.support.util_io import IOutputStream, readGenerator
from asyncore import dispatcher, loop
from collections import Callable, deque
from http.server import BaseHTTPRequestHandler
from io import BytesIO
from urllib.parse import urlparse, parse_qsl
import logging
import re
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

    methods = {
               'DELETE' : DELETE,
               'GET' : GET,
               'POST' : INSERT,
               'PUT' : UPDATE,
               'OPTIONS' : METHOD_OPTIONS
               }
    methodUnknown = -1
    # The available method for processing.

    def __init__(self, server, request, address):
        '''
        Construct the request handler.
        
        @param server: AsyncServer
            The server that created the request.
        @param request: socket
            The connection request socket.
        @param address: tuple(string, integer)
            The client address.
        '''
        assert isinstance(server, AsyncServer), 'Invalid server %s' % server
        assert isinstance(address, tuple), 'Invalid address %s' % address
        
        dispatcher.__init__(self, request, map=server.map)
        self.server = server
        self.client_address = address
        self.connection = request
        
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
            
            self._process(self.methods.get(self.command, self.methodUnknown))
            
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
        url = urlparse(self.path)
        path = url.path.lstrip('/')
        for regex, processing in self.server.pathProcessing:
            match = regex.match(path)
            if match:
                uriRoot = path[:match.end()]
                if not uriRoot.endswith('/'): uriRoot += '/'

                assert isinstance(processing, Processing), 'Invalid processing %s' % processing
                req, reqCnt = processing.contexts['request'](), processing.contexts['requestCnt']()
                rsp, rspCnt = processing.contexts['response'](), processing.contexts['responseCnt']()

                assert isinstance(req, RequestHTTP), 'Invalid request %s' % req
                assert isinstance(reqCnt, RequestContentHTTPAsyncore), 'Invalid request content %s' % reqCnt
                assert isinstance(rsp, ResponseHTTP), 'Invalid response %s' % rsp
                assert isinstance(rspCnt, ResponseContentHTTP), 'Invalid response content %s' % rspCnt

                req.scheme, req.uriRoot, req.uri = 'http', uriRoot, path[match.end():]
                req.parameters = parse_qsl(url.query, True, False)
                break
        else:
            self.send_response(404)
            self.end_headers()
            self.close()
            return

        req.method = method
        req.headers = dict(self.headers)

        def respond():
            assert isinstance(rsp.code, Code), 'Invalid response code %s' % rsp.code
    
            if ResponseHTTP.headers in rsp:
                for name, value in rsp.headers.items(): self.send_header(name, value)
    
            if ResponseHTTP.text in rsp: self.send_response(rsp.code.code, rsp.text)
            else: self.send_response(rsp.code.code)
    
            self.end_headers()
    
            if rspCnt.source is not None:
                if isinstance(rspCnt.source, IOutputStream): source = readGenerator(rspCnt.source, self.bufferSize)
                else: source = rspCnt.source
    
                self._writeq.append((WRITE_ITER, iter(source)))
            self._writeq.append((WRITE_CLOSE, None))
            
        chain = Chain(processing)
        chain.process(request=req, requestCnt=reqCnt, response=rsp, responseCnt=rspCnt)
        chain.callBack(respond)
        
        while True:
            if not chain.do():
                self._next(3)  # Now we proceed to write stage
                break
            if reqCnt.contentReader is not None:
                self._next(2)  # Now we proceed to read stage
                self._reader = reqCnt.contentReader
                break

# --------------------------------------------------------------------

class AsyncServer(dispatcher):
    '''
    The asyncore server handling the connection.
    '''
    timeout = 10.0
    # The timeout for select loop.

    def __init__(self, serverAddress, pathProcessing, requestHandlerFactory):
        '''
        Construct the server.
        
        @param serverAddress: tuple(string, integer)
            The server address host and port.
        @param pathProcessing: list[tuple(regex, Processing)] 
            A list that contains tuples having on the first position a regex for matching a path, and the second value 
            the processing for handling the path.
        @param requestHandlerFactory: callable(AsyncServer, socket, tuple(string, integer))
            The factory that provides request handlers, takes as arguments the server, request socket
            and client address.
        '''
        assert isinstance(serverAddress, tuple), 'Invalid server address %s' % serverAddress
        assert isinstance(pathProcessing, list), 'Invalid path processing %s' % pathProcessing
        assert callable(requestHandlerFactory), 'Invalid request handler factory %s' % requestHandlerFactory
        
        self.map = {}
        dispatcher.__init__(self, map=self.map)
        self.serverAddress = serverAddress
        self.pathProcessing = pathProcessing
        self.requestHandlerFactory = requestHandlerFactory
        
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind(serverAddress)
        self.listen(1024)  # lower this to 5 if your OS complains

    def handle_accept (self):
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
        self.requestHandlerFactory(self, request, address)
    
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

def run(pathAssemblies, server_version, host='', port=80):
    '''
    Run the basic server.
    
    @param pathAssemblies: list[(regex, Assembly)]
        A list that contains tuples having on the first position a string pattern for matching a path, and as a value 
        the assembly to be used for creating the context for handling the request for the path.
    '''
    assert isinstance(pathAssemblies, list), 'Invalid path assemblies %s' % pathAssemblies
    RequestHandler.server_version = server_version
    pathProcessing = []
    for pattern, assembly in pathAssemblies:
        assert isinstance(pattern, str), 'Invalid pattern %s' % pattern
        assert isinstance(assembly, Assembly), 'Invalid assembly %s' % assembly

        processing, report = assembly.create(ONLY_AVAILABLE, CREATE_REPORT,
                                             request=RequestHTTP, requestCnt=RequestContentHTTPAsyncore,
                                             response=ResponseHTTP, responseCnt=ResponseContentHTTP)

        log.info('Assembly report for pattern \'%s\':\n%s', pattern, report)
        pathProcessing.append((re.compile(pattern), processing))
        
    try:
        server = AsyncServer((host, port), pathProcessing, RequestHandler)
        print('=' * 50, 'Started Async REST API server...')
#        import profile
#        profile.runctx('server.serve_limited(1000)', globals(), locals(), 'profiler.data')
        server.serve_forever()
    except KeyboardInterrupt:
        print('=' * 50, '^C received, shutting down server')
        server.close()
    except:
        log.exception('=' * 50 + ' The server has stooped')
        try: server.close()
        except: pass
        
