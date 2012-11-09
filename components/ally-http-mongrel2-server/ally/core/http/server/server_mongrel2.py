'''
Created on Nov 23, 2011

@package: ally core http
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the mongrel2 web server support.
'''

from ally.api.config import UPDATE, INSERT, GET, DELETE
from ally.container.ioc import injected
from ally.core.http.spec.server import METHOD_OPTIONS, RequestHTTP, ResponseHTTP, \
    RequestContentHTTP, ResponseContentHTTP
from ally.core.http.support import tnetstrings
from ally.core.spec.codes import Code
from ally.design.processor import Processing, Assembly, ONLY_AVAILABLE, \
    CREATE_REPORT, Chain
from ally.support.util_io import IInputStream, IClosable
from collections import Iterable
from io import BytesIO
from os import path, remove
from urllib.parse import parse_qsl
from uuid import uuid4
import json
import logging
import re
import zmq

# --------------------------------------------------------------------

log = logging.getLogger(__name__)
    
# --------------------------------------------------------------------

@injected
class RequestHandler:
    '''
    The server class that handles the requests.
    '''
    
    pathAssemblies = list
    # A list that contains tuples having on the first position a string pattern for matching a path, and as a value 
    # the assembly to be used for creating the context for handling the request for the path.
    serverVersion = str
    # The server version name
 
    httpFormat = 'HTTP/1.1 %(code)s %(status)s\r\n%(headers)s\r\n\r\n'
    # The http format for the response.
    methods = {
               'DELETE' : DELETE,
               'GET' : GET,
               'POST' : INSERT,
               'PUT' : UPDATE,
               'OPTIONS' : METHOD_OPTIONS
               }
    methodUnknown = -1

    def __init__(self):
        assert isinstance(self.pathAssemblies, list), 'Invalid path assemblies %s' % self.pathAssemblies
        assert isinstance(self.serverVersion, str), 'Invalid server version %s' % self.serverVersion
        assert isinstance(self.httpFormat, str), 'Invalid http format for the response %s' % self.httpFormat
        assert isinstance(self.methods, dict), 'Invalid methods %s' % self.methods
        assert isinstance(self.methodUnknown, int), 'Invalid unknwon method %s' % self.methodUnknown
        
        pathProcessing = []
        for pattern, assembly in self.pathAssemblies:
            assert isinstance(pattern, str), 'Invalid pattern %s' % pattern
            assert isinstance(assembly, Assembly), 'Invalid assembly %s' % assembly

            processing, report = assembly.create(ONLY_AVAILABLE, CREATE_REPORT,
                                                 request=RequestHTTP, requestCnt=RequestContentHTTP,
                                                 response=ResponseHTTP, responseCnt=ResponseContentHTTP)

            log.info('Assembly report for pattern \'%s\':\n%s', pattern, report)
            pathProcessing.append((re.compile(pattern), processing))
        self.pathProcessing = pathProcessing
        self.defaultHeaders = {'Server':self.serverVersion, 'Content-Type':'text'}
        self.scheme = 'http'

    def __call__(self, request):
        '''
        Process the Mongrel2 call.
        
        @param request: Request
            The request to process.
        '''
        assert isinstance(request, Request), 'Invalid request %s' % request
        
        path = request.path
        responseHeaders = dict(self.defaultHeaders)
        if path.startswith('/'): path = path[1:]

        for regex, processing in self.pathProcessing:
            match = regex.match(path)
            if match:
                uriRoot = path[:match.end()]
                if not uriRoot.endswith('/'): uriRoot += '/'

                assert isinstance(processing, Processing), 'Invalid processing %s' % processing
                req, reqCnt = processing.contexts['request'](), processing.contexts['requestCnt']()
                rsp, rspCnt = processing.contexts['response'](), processing.contexts['responseCnt']()

                assert isinstance(req, RequestHTTP), 'Invalid request %s' % req
                assert isinstance(reqCnt, RequestContentHTTP), 'Invalid request content %s' % reqCnt
                assert isinstance(rsp, ResponseHTTP), 'Invalid response %s' % rsp
                assert isinstance(rspCnt, ResponseContentHTTP), 'Invalid response content %s' % rspCnt

                req.scheme, req.uriRoot, req.uri = self.scheme, uriRoot, path[match.end():]
                break
        else:
            self._respond(request, 404, 'Not Found', responseHeaders)
            request.send(b'')  # Send an empty body to finalize the response
            return

        req.method = self.methods.get(request.headers.pop('METHOD'), self.methodUnknown)
        req.parameters = parse_qsl(request.headers.pop('QUERY', ''), True, False)
        req.headers = request.headers
        if isinstance(request.body, IInputStream): reqCnt.source = request.body
        else: reqCnt.source = BytesIO(request.body)

        Chain(processing).process(request=req, requestCnt=reqCnt, response=rsp, responseCnt=rspCnt).doAll()

        assert isinstance(rsp.code, Code), 'Invalid response code %s' % rsp.code

        responseHeaders.update(rsp.headers)
        self._respond(request, rsp.code.code, rsp.text, responseHeaders)
        if rspCnt.source is not None: request.push(rspCnt.source)

    # ----------------------------------------------------------------

    def _respond(self, request, code, status, headers):
        assert isinstance(request, Request), 'Invalid request %s' % request
        
        msg = {'code': code, 'status': status, 'headers':'\r\n'.join('%s: %s' % entry for entry in headers.items())}
        msg = self.httpFormat % msg
        request.send(msg.encode())

# --------------------------------------------------------------------

class Mongrel2Server:
    '''
    The mongrel2 server handling the connection.
    Made based on the mongrel2.handler
    '''
    
    def __init__(self, workspacePath, sendIdent, sendSpec, recvIdent, recvSpec, requestHandler):
        '''
        Your addresses should be the same as what you configured
        in the config.sqlite for Mongrel2 and are usually like 
        tcp://127.0.0.1:9998
        '''
        assert isinstance(workspacePath, str), 'Invalid path workspace %s' % workspacePath
        assert callable(requestHandler), 'Invalid request handler %s' % requestHandler
        self.workspacePath = workspacePath
        self.context = zmq.Context()
        self.reqs = self.context.socket(zmq.PULL)

        if recvIdent: self.reqs.setsockopt(zmq.IDENTITY, recvIdent)
        self.reqs.connect(sendSpec)

        self.resp = self.context.socket(zmq.PUB)
        if sendIdent: self.resp.setsockopt(zmq.IDENTITY, sendIdent)
        self.resp.connect(recvSpec)
        
        self.requestHandler = requestHandler
        
    def accept(self):
        '''
        Receives a raw Mongrel2 object that you can then work with.
        '''
        data = self.reqs.recv()
        sender, connId, path, rest = data.split(b' ', 3)
        headers, rest = tnetstrings.parse(rest)
        body, rest = tnetstrings.parse(rest)

        if type(headers) is bytes: headers = json.loads(str(headers, 'utf8'))

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

def run(workspacePath, requestHandler, sendIdent, sendSpec, recvIdent, recvSpec):
    assert isinstance(workspacePath, str), 'Invalid path workspace %s' % workspacePath
    assert callable(requestHandler), 'Invalid request handler %s' % requestHandler
    if sendIdent is None: sendIdent = uuid4().hex.encode('utf8')
    elif isinstance(sendIdent, str): sendIdent = sendIdent.encode('utf8')
    if recvIdent is None: recvIdent = uuid4().hex.encode('utf8')
    elif isinstance(recvIdent, str): recvIdent = recvIdent.encode('utf8')
    
    server = Mongrel2Server(workspacePath, sendIdent, sendSpec, recvIdent, recvSpec, requestHandler)
    try:
        print('=' * 50, 'Started Mongrel2 REST API server...')
        server.serve_forever()
    except KeyboardInterrupt:
        print('=' * 50, '^C received, shutting down server')
        server.server_close()
    except:
        log.exception('=' * 50 + ' The server has stooped')
        try: server.server_close()
        except: pass
