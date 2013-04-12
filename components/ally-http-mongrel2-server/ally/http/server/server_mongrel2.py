'''
Created on Nov 23, 2011

@package: ally http
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the mongrel2 web server support.
'''

from ..support import tnetstrings
from ally.container.ioc import injected
from ally.design.processor.assembly import Assembly
from ally.design.processor.execution import Chain, Processing
from ally.http.spec.server import RequestHTTP, ResponseHTTP, RequestContentHTTP, \
    ResponseContentHTTP, HTTP
from ally.support.util_io import IInputStream, IClosable
from collections import Iterable
from http.server import BaseHTTPRequestHandler
from io import BytesIO
from os import path, remove
from urllib.parse import parse_qsl
from uuid import uuid4
import json
import logging
import zmq

# --------------------------------------------------------------------

log = logging.getLogger(__name__)
    
# --------------------------------------------------------------------

@injected
class RequestHandler:
    '''
    The server class that handles the requests.
    '''
    
    serverVersion = str
    # The server version name
    scheme = HTTP
    # The server scheme
    assembly = Assembly
    # The assembly used for resolving the requests
 
    httpFormat = 'HTTP/1.1 %(code)s %(status)s\r\n%(headers)s\r\n\r\n'
    # The http format for the response.

    def __init__(self):
        assert isinstance(self.serverVersion, str), 'Invalid server version %s' % self.serverVersion
        assert isinstance(self.assembly, Assembly), 'Invalid assembly %s' % self.assembly
        assert isinstance(self.httpFormat, str), 'Invalid http format for the response %s' % self.httpFormat
        
        self.processing = self.assembly.create(request=RequestHTTP, requestCnt=RequestContentHTTP,
                                               response=ResponseHTTP, responseCnt=ResponseContentHTTP)
        self.defaultHeaders = {'Server':self.serverVersion, 'Content-Type':'text'}

    def __call__(self, req):
        '''
        Process the Mongrel2 call.
        
        @param req: Request
            The request to process.
        '''
        assert isinstance(req, Request), 'Invalid request %s' % req
        proc = self.processing
        assert isinstance(proc, Processing), 'Invalid processing %s' % proc
        
        request, requestCnt = proc.ctx.request(), proc.ctx.requestCnt()
        assert isinstance(request, RequestHTTP), 'Invalid request %s' % request
        assert isinstance(requestCnt, RequestContentHTTP), 'Invalid request content %s' % requestCnt
        
        request.scheme, request.method = self.scheme, req.headers.pop('METHOD').upper()
        request.headers = dict(req.headers)
        request.uri = req.path.lstrip('/')
        request.parameters = parse_qsl(req.headers.pop('QUERY', ''), True, False)
        
        if isinstance(req.body, IInputStream): requestCnt.source = req.body
        else: requestCnt.source = BytesIO(req.body)
        
        chain = Chain(proc)
        chain.process(request=request, requestCnt=requestCnt,
                      response=proc.ctx.response(), responseCnt=proc.ctx.responseCnt()).doAll()

        response, responseCnt = chain.arg.response, chain.arg.responseCnt
        assert isinstance(response, ResponseHTTP), 'Invalid response %s' % response
        assert isinstance(responseCnt, ResponseContentHTTP), 'Invalid response content %s' % responseCnt
        
        responseHeaders = dict(self.defaultHeaders)
        if ResponseHTTP.headers in response and response.headers is not None: responseHeaders.update(response.headers)
        
        assert isinstance(response.status, int), 'Invalid response status code %s' % response.status
        if ResponseHTTP.text in response and response.text: text = response.text
        elif ResponseHTTP.code in response and response.code: text = response.code
        else:
            try: text, _long = BaseHTTPRequestHandler.responses[response.status]
            except KeyError: text = '???'
        self._respond(req, response.status, text, responseHeaders)
        
        if ResponseContentHTTP.source in responseCnt and responseCnt.source is not None: req.push(responseCnt.source)
        self._end(req)

    # ----------------------------------------------------------------

    def _respond(self, request, code, status, headers):
        '''
        Respond with the HTTP response.
        '''
        assert isinstance(request, Request), 'Invalid request %s' % request
        
        msg = {'code': code, 'status': status, 'headers':'\r\n'.join('%s: %s' % entry for entry in headers.items())}
        msg = self.httpFormat % msg
        request.send(msg.encode())
        
    def _end(self, request):
        '''
        End the request response.
        '''
        assert isinstance(request, Request), 'Invalid request %s' % request
        request.send(b'')  # Send an empty body to finalize the response

# --------------------------------------------------------------------

@injected
class Mongrel2Server:
    '''
    The mongrel2 server handling the connection.
    Made based on the mongrel2.handler
    '''
    
    workspacePath = str
    # The workspace path where the uploads can be located, this is basically the mongrel2 workspace path this should not
    # include the relative, for example "mongrel2/tmp"
    sendIdent = None
    # The send ident to use in communication with Mongrel2, if not specified one will be created
    sendSpec = str
    # The send address to use in communication with Mongrel2, something like:
    # "tcp://127.0.0.1:9997" - for using sockets that allow communication between computers
    # "ipc:///tmp/send" - for using in processes that allow communication on the same computer processes
    recvIdent = None
    # The receive ident to use in communication with Mongrel2, if not specified one will be created
    recvSpec = str
    # The receive address to use in communication with Mongrel2, see more details at "address_request" configuration
    requestHandler = RequestHandler
    # The request handler callable instance to be used.
    
    def __init__(self):
        '''
        Construct the mongrel2 server.
        Your addresses should be the same as what you configured
        in the config.sqlite for Mongrel2 and are usually like 
        tcp://127.0.0.1:9998
        '''
        assert isinstance(self.workspacePath, str), 'Invalid path workspace %s' % self.workspacePath
        assert self.sendIdent is None or isinstance(self.sendIdent, str), 'Invalid send ident %s' % self.sendIdent
        assert isinstance(self.sendSpec, str), 'Invalid send spec %s' % self.sendSpec
        assert self.recvIdent is None or isinstance(self.recvIdent, str), 'Invalid receive ident %s' % self.recvIdent
        assert isinstance(self.recvSpec, str), 'Invalid receive spec %s' % self.recvSpec
        assert callable(self.requestHandler), 'Invalid request handler %s' % self.requestHandler
        
        if self.sendIdent is None: self.sendIdent = uuid4().hex.encode('utf8')
        elif isinstance(self.sendIdent, str): self.sendIdent = self.sendIdent.encode('utf8')
        if self.recvIdent is None: self.recvIdent = uuid4().hex.encode('utf8')
        elif isinstance(self.recvIdent, str): self.recvIdent = self.recvIdent.encode('utf8')
        
        self.context = zmq.Context()
        
        self.reqs = self.context.socket(zmq.PULL)
        self.reqs.setsockopt(zmq.IDENTITY, self.recvIdent)
        self.reqs.connect(self.sendSpec)

        self.resp = self.context.socket(zmq.PUB)
        self.resp.setsockopt(zmq.IDENTITY, self.sendIdent)
        self.resp.connect(self.recvSpec)
        
    def accept(self):
        '''
        Receives a raw Mongrel2 object that you can then work with.
        '''
        data = self.reqs.recv()
        sender, connId, path, rest = data.split(b' ', 3)
        headers, rest = tnetstrings.parse(rest)
        body, rest = tnetstrings.parse(rest)

        if type(headers) is bytes: headers = json.loads(str(headers, 'utf8'))
        else: headers = {str(name, 'utf8'): str(value, 'utf8') for name, value in headers.items()}
        
        return Request(self, sender, connId, str(path, 'utf8'), headers, body)
    
    def serve_forever(self):
        '''
        Serve forever.
        '''
        while True:
            upload = None
            request = self.accept()
            if request.isDisconnect:
                assert log.debug('Request disconnected') or True
                continue
            else:
                started = request.headers.get('x-mongrel2-upload-start', None)
                done = request.headers.get('x-mongrel2-upload-done', None)
                
                if done:
                    assert log.debug('Upload done in file %s' % done) or True
                    if started != done:
                        assert log.debug('Got the wrong target file \'%s\' expected \'%s\'' % (done, started)) or True
                        continue
                    pathUpload = path.join(self.workspacePath, done)
                    request.body = open(pathUpload, 'rb')
                    upload = pathUpload, request.body
                elif started:
                    assert log.debug('Upload starting in file %s' % started) or True
                    continue

            try: self.requestHandler(request)
            finally:
                if upload is not None:
                    # Remove the uploaded file.
                    pathUpload, stream = upload
                    try: stream.close()
                    except: pass
                    remove(pathUpload)
                    assert log.debug('Removed upload file %s' % pathUpload) or True

class Request:
    '''
    Simple container for request data.
    '''
    __slots__ = ('server', 'sender', 'connId', 'path', 'headers', 'body', 'data', 'isDisconnect', '_header')
    
    def __init__(self, server, sender, connId, path, headers, body):
        '''
        Construct the request.
        '''
        assert isinstance(server, Mongrel2Server), 'Invalid server %s' % server
        assert isinstance(sender, bytes), 'Invalid sender %s' % sender
        assert isinstance(connId, bytes), 'Invalid connection id %s' % connId
        assert isinstance(path, str), 'Invalid path %s' % path
        assert isinstance(headers, dict), 'Invalid headers %s' % headers
        assert isinstance(body, bytes), 'Invalid body %s' % body
        self.server = server
        self.sender = sender
        self.connId = connId
        self.path = path
        self.headers = headers
        self.body = body
        
        if headers.get('METHOD') == 'JSON':
            self.data = json.loads(str(self.body, 'utf8'))
            self.isDisconnect = self.data['type'] == 'disconnect'
        else:
            self.isDisconnect = False
        
        if not self.isDisconnect:
            self._header = b''.join((self.sender, b' ', str(len(self.connId)).encode(), b':', self.connId, b', '))
        
    def send(self, msg):
        '''
        Send the bytes message.
        '''
        self.server.resp.send(self._header + msg)
        
    def push(self, content):
        '''
        Push the stream data as a response.
        '''
        assert isinstance(content, (IInputStream, Iterable)), 'Invalid content %s' % content
        if isinstance(content, IInputStream):
            assert isinstance(content, IInputStream)
            self.send(content.read())
            if isinstance(content, IClosable):
                assert isinstance(content, IClosable)
                content.close()
        else:
            cache = BytesIO()
            for data in content: cache.write(data)
            self.send(cache.getvalue())
            cache.close()

# --------------------------------------------------------------------

def run(server):
    '''
    Run the mongrel2 server.
    
    @param server: Mongrel2Server
        The server to run.
    '''
    assert isinstance(server, Mongrel2Server), 'Invalid server %s' % server
    try:
        log.info('=' * 50 + ' Started Mongrel2 server...')
        server.serve_forever()
    except KeyboardInterrupt:
        log.info('=' * 50 + ' ^C received, shutting down server')
        server.server_close()
    except:
        log.exception('=' * 50 + ' The server has stooped')
        try: server.server_close()
        except: pass
