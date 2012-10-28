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
from ally.design.processor import Processing, Chain, Assembly, ONLY_AVAILABLE, \
    CREATE_REPORT
from ally.support.util_io import IOutputStream, readGenerator
from asyncore import dispatcher, poll
from collections import deque
from http.server import BaseHTTPRequestHandler
from io import BytesIO
from urllib.parse import urlparse, parse_qsl
import abc
import logging
import re
import socket
import sys
import traceback

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# Constants used in indicating the write option. 
WRITE_IS = 1
WRITE_DATA = 2
WRITE_SENT = 3

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
    pathProcessing = list
    # A list that contains tuples having on the first position a regex for matching a path, and the second value 
    # the processing for handling the path.

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
        assert isinstance(self.pathProcessing, list), 'Invalid path processing %s' % self.pathProcessing
        
        dispatcher.__init__(self, request, map=server.map)
        self.server = server
        self.client_address = address
        self.connection = request
        
        self.request_version = 'HTTP/1.1'
        self.requestline = 0
        
        self.rfile = BytesIO()
        self._readCarry = None

        self.wfile = BytesIO()
        self._writePosition = 0
        self._writeFinalized = False
        self._writeContent = None

    def readable (self):
        '''
        Always able to read.
        @see: dispatcher.readable
        '''
        return True

    def handle_read(self):
        '''
        @see: dispatcher.handle_read
        '''
        try: data = self.recv(self.bufferSize)
        except socket.error:
            log.exception('Exception occurred while reading the connection \'%s\'' % self.connection)
            self.close()
            return
        self._handleReadData(data)

    # ----------------------------------------------------------------
    
    def writable(self):
        '''
        @see: dispatcher.writable
        '''
        return self._handleWriteData(WRITE_IS)
    
    def handle_write(self):
        '''
        @see: dispatcher.handle_write
        '''
        data = self._handleWriteData(WRITE_DATA)
        if data is not None:
            try: sent = self.send(data)
            except socket.error:
                log.exception('Exception occurred while writing to the connection \'%s\'' % self.connection)
                self.close()
                return
            self._handleWriteData(WRITE_SENT, sent)
        
    # ----------------------------------------------------------------
    
    def _handleReadData(self, data):
        '''
        Handle the data as being part of the request.
        '''
        if self._readCarry is not None: data = self._readCarry + data
        index = data.find(self.requestTerminator)
        requestTerminatorLen = len(self.requestTerminator)
        
        if index >= 0:
            self._handleReadData = self._handleReadDataForContent  # Now the read content is considered as content
            self.rfile.write(data[:index + requestTerminatorLen:])
            self.rfile.seek(0)
            self.raw_requestline = self.rfile.readline()
            self.parse_request()
            
            self.rfile.seek(0)
            self.rfile.truncate()
            self.rfile.write(data[index + requestTerminatorLen:])
            self._readCarry = None
            
            self._process(self.methods.get(self.command, self.methodUnknown))
        else:
            self._readCarry = data[-requestTerminatorLen:]
            self.rfile.write(data[:-requestTerminatorLen])
            
            if self.rfile.tell() > self.maximumRequestSize:
                self.send_response(400, 'Request to long')
                self.end_headers()
                self.close()

    def _handleReadDataForContent(self, data):
        '''
        Handle the data as being part of the request content.
        '''
        self.rfile.write(data)
    
    # ----------------------------------------------------------------

    def _handleWriteData(self, do, sent=None):
        '''
        Handle the data that forms the response.
        '''
        if do == WRITE_IS: return self.wfile.tell() - self._writePosition > 0
        elif do == WRITE_DATA:
            self.wfile.seek(self._writePosition)
            data = self.wfile.read(self.bufferSize)
            self.wfile.seek(0, 2)  # Go back to the end of the stream
            return data
        elif do == WRITE_SENT:
            if sent: self._writePosition += sent
            if self._writeFinalized and self._writePosition >= self.wfile.tell():
                self._handleWriteData = self._handleWriteDataForContent
                self._writePosition = 0
                self.wfile.seek(0)
                self.wfile.truncate()
                
    def _handleWriteDataForContent(self, do, sent=None):
        '''
        Handle the data that for the response content.
        '''
        if do == WRITE_IS: return self._writeContent is not None or self.wfile.tell() - self._writePosition > 0
        elif do == WRITE_DATA:
            if self._writePosition >= self.wfile.tell():
                self._writePosition = 0
                self.wfile.seek(0)
                self.wfile.truncate()
                try: data = next(self._writeContent)
                except StopIteration:
                    self._writeContent = None
                    self.close()
                    return
                self.wfile.write(data)
            else:
                self.wfile.seek(self._writePosition)
                data = self.wfile.read(self.bufferSize)
                self.wfile.seek(0, 2)  # Go back to the end of the stream
                return data
        elif do == WRITE_SENT:
            if sent: self._writePosition += sent
            if self._writeContent is None and self._writePosition >= self.wfile.tell(): self.close()

    # ----------------------------------------------------------------
    
    def _process(self, method):
        url = urlparse(self.path)
        path = url.path.lstrip('/')
        for regex, processing in self.pathProcessing:
            match = regex.match(path)
            if match:
                uriRoot = path[:match.end()]
                if not uriRoot.endswith('/'): uriRoot += '/'

                assert isinstance(processing, Processing), 'Invalid processing %s' % processing
                req, reqCnt = processing.contexts['request'](), processing.contexts['requestCnt']()
                rsp, rspCnt = processing.contexts['response'](), processing.contexts['responseCnt']()
                chain = processing.newChain()
                # TODO: make the chain be splited for processing calls

                assert isinstance(chain, Chain), 'Invalid chain %s' % chain
                assert isinstance(req, RequestHTTP), 'Invalid request %s' % req
                assert isinstance(reqCnt, RequestContentHTTP), 'Invalid request content %s' % reqCnt
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
        reqCnt.source = self.rfile

        chain.process(request=req, requestCnt=reqCnt, response=rsp, responseCnt=rspCnt)

        assert isinstance(rsp.code, Code), 'Invalid response code %s' % rsp.code

        if ResponseHTTP.headers in rsp:
            for name, value in rsp.headers.items(): self.send_header(name, value)

        if ResponseHTTP.text in rsp: self.send_response(rsp.code.code, rsp.text)
        else: self.send_response(rsp.code.code)

        self.end_headers()
        self._writeFinalized = True

        if rspCnt.source is not None:
            if isinstance(rspCnt.source, IOutputStream): source = readGenerator(rspCnt.source, self.bufferSize)
            else: source = rspCnt.source

            self._writeContent = iter(source)
        
    # ----------------------------------------------------------------

    def log_message(self, format, *args):
        # TODO: see for a better solution for this, check for next python release
        # This is a fix: whenever a message is logged there is an attempt to find some sort of host name which
        # creates a big delay whenever the request is made from a non localhost client.
        assert log.debug(format, *args) or True

# --------------------------------------------------------------------

class AsyncServer(dispatcher):
    '''
    The asyncore server handling the connection.
    '''
    timeout = 10.0
    # The timeout for select loop.
    
    def __init__ (self, serverAddress, requestHandlerFactory):
        '''
        Construct the server.
        
        @param serverAddress: tuple(string, integer)
            The server address host and port.
        @param requestHandlerFactory: callable(AsyncServer, socket, tuple(string, integer))
            The factory that provides request handlers, takes as arguments the server, request socket
            and client address.
        '''
        assert isinstance(serverAddress, tuple), 'Invalid server address %s' % serverAddress
        assert callable(requestHandlerFactory), 'Invalid request handler factory %s' % requestHandlerFactory
        
        self.calls = deque()
        self.map = {}
        dispatcher.__init__(self, map=self.map)
        self.serverAddress = serverAddress
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
        while self.map:
            if self.calls:
                call, *args = self.calls.popleft()
                call(*args)
                poll(map=self.map)
            else: poll(self.timeout, map=self.map)

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
    RequestHandler.pathProcessing = []
    for pattern, assembly in pathAssemblies:
        assert isinstance(pattern, str), 'Invalid pattern %s' % pattern
        assert isinstance(assembly, Assembly), 'Invalid assembly %s' % assembly

        processing, report = assembly.create(ONLY_AVAILABLE, CREATE_REPORT,
                                             request=RequestHTTP, requestCnt=RequestContentHTTP,
                                             response=ResponseHTTP, responseCnt=ResponseContentHTTP)

        log.info('Assembly report for pattern \'%s\':\n%s', pattern, report)
        RequestHandler.pathProcessing.append((re.compile(pattern), processing))
    
    try:
        server = AsyncServer((host, port), RequestHandler)
        print('=' * 50, 'Started Async REST API server...')
        server.serve_forever()
    except KeyboardInterrupt:
        print('=' * 50, '^C received, shutting down server')
        server.close()
    except:
        log.exception('=' * 50 + ' The server has stooped')
        try: server.close()
        except: pass
