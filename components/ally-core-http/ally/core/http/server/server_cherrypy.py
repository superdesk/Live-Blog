'''
Created on Nov 23, 2011

@package: ally core http
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the cherry py web server support.
'''

from ally.api.config import UPDATE, INSERT, GET, DELETE
from ally.container.ioc import injected
from ally.core.http.spec.server import METHOD_OPTIONS, RequestHTTP, ResponseHTTP
from ally.core.spec.codes import Code
from ally.core.spec.server import Content, IStream, ClassesServer
from ally.design.processor import Processing, Chain
from ally.support.util_io import readGenerator
import cherrypy
import logging
import re

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

@injected
class RequestHandler:
    '''
    The server class that handles the requests.
    '''

    pathHandlers = list
    # A list that contains tuples having on the first position a string pattern for matching a path, and as a value 
    # a list of handlers to be used for creating the context for handling the request for the path.
    serverVersion = str
    # The server version name

    methods = {
               'DELETE' : DELETE,
               'GET' : GET,
               'POST' : INSERT,
               'PUT' : UPDATE,
               'OPTIONS' : METHOD_OPTIONS
               }
    methodUnknown = -1

    def __init__(self):
        assert isinstance(self.serverVersion, str), 'Invalid server version %s' % self.serverVersion
        assert isinstance(self.pathHandlers, list), 'Invalid path handlers %s' % self.pathHandlers
        pathHandlers = []
        for pattern, handlers in self.pathHandlers:
            assert isinstance(pattern, str), 'Invalid pattern %s' % pattern
            classes = ClassesServer(RequestHTTP, ResponseHTTP)
            pathHandlers.append((re.compile(pattern), Processing(handlers, classes)))
        self.pathHandlers = pathHandlers

    @cherrypy.expose
    def default(self, *vpath, **params):
        request, response = cherrypy.request, cherrypy.response
        path = '/'.join(vpath)

        for regex, processing in self.pathHandlers:
            match = regex.match(path)
            if match:
                uriRoot = path[:match.end()]
                if not uriRoot.endswith('/'): uriRoot += '/'

                assert isinstance(processing, Processing), 'Invalid processing %s' % processing
                chain = processing.newChain()
                req, rsp = processing.classes.request(), processing.classes.response()
                cntReq, cntRsp = processing.classes.requestCnt(), processing.classes.responseCnt()
                assert isinstance(chain, Chain), 'Invalid chain %s' % chain
                assert isinstance(req, RequestHTTP), 'Invalid request %s' % req
                assert isinstance(rsp, ResponseHTTP), 'Invalid response %s' % rsp
                assert isinstance(cntReq, Content), 'Invalid request content %s' % cntReq
                assert isinstance(cntRsp, Content), 'Invalid response content %s' % cntRsp

                req, rsp = processing.Request(), processing.Response()
                #TODO: see from where to extract the scheme
                req.scheme, req.uriRoot, req.uri = 'http', uriRoot, path[match.end():]
                break
        else:
            raise cherrypy.HTTPError(404)

        req.method = self.methods.get(request.method, self.methodUnknown)
        req.headers.update(request.headers)
        cntReq.source = request.rfile

        for name, value in params.items():
            if isinstance(value, list): req.parameters.extend([(name, v) for v in value])
            else: req.parameters.append((name, value))

        chain.process(request=req, requestCnt=cntReq, response=rsp, responseCnt=cntRsp)

        assert isinstance(rsp.code, Code), 'Invalid response code %s' % rsp.code

        response.headers.pop('Content-Type', None)
        response.headers['Server'] = self.serverVersion
        response.headers.update(rsp.headers)
        response.status = '%s %s' % (rsp.code.code, rsp.text)

        assert log.debug('Finalized request: %s and response: %s' % (req, rsp)) or True

        if isinstance(cntRsp.source, IStream): return readGenerator(cntRsp.source)
        return cntRsp.source
    default._cp_config = {
                          'response.stream': True, # We make sure that streaming occurs and is not cached
                          'request.process_request_body': False
                          }

# --------------------------------------------------------------------

def run(requestHandler, host='127.0.0.1', port=80, threadPool=10):
    print('=' * 50, 'Started HTTP REST API server...')
    config = {
              'global':{
                        'engine.autoreload.on': False,
                        'server.socket_port': port,
                        'server.socket_host': host,
                        'server.thread_pool': threadPool,
                        },
              }
    cherrypy.quickstart(requestHandler, config=config)
