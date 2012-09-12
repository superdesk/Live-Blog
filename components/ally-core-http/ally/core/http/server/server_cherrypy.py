'''
Created on Nov 23, 2011

@package: ally core http
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the cherry py web server support.
'''

from ally.api.config import UPDATE, INSERT, GET, DELETE
from ally.support.util_io import IOutputStream
from ally.container.ioc import injected
from ally.core.http.spec.server import METHOD_OPTIONS, RequestHTTP, ResponseHTTP, \
    RequestContentHTTP, ResponseContentHTTP
from ally.core.spec.codes import Code
from ally.design.processor import Processing, Chain, Assembly, ONLY_AVAILABLE, \
    CREATE_REPORT
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

    pathAssemblies = list
    # A list that contains tuples having on the first position a string pattern for matching a path, and as a value 
    # the assembly to be used for creating the context for handling the request for the path.
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
        assert isinstance(self.pathAssemblies, list), 'Invalid path assemblies %s' % self.pathAssemblies
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

    @cherrypy.expose
    def default(self, *vpath, **params):
        request, response = cherrypy.request, cherrypy.response
        path = '/'.join(vpath)

        for regex, processing in self.pathProcessing:
            match = regex.match(path)
            if match:
                uriRoot = path[:match.end()]
                if not uriRoot.endswith('/'): uriRoot += '/'

                assert isinstance(processing, Processing), 'Invalid processing %s' % processing
                req, reqCnt = processing.contexts['request'](), processing.contexts['requestCnt']()
                rsp, rspCnt = processing.contexts['response'](), processing.contexts['responseCnt']()
                chain = processing.newChain()

                assert isinstance(chain, Chain), 'Invalid chain %s' % chain
                assert isinstance(req, RequestHTTP), 'Invalid request %s' % req
                assert isinstance(reqCnt, RequestContentHTTP), 'Invalid request content %s' % reqCnt
                assert isinstance(rsp, ResponseHTTP), 'Invalid response %s' % rsp
                assert isinstance(rspCnt, ResponseContentHTTP), 'Invalid response content %s' % rspCnt

                req.scheme, req.uriRoot, req.uri = 'http', uriRoot, path[match.end():]
                break
        else:
            raise cherrypy.HTTPError(404)

        req.method = self.methods.get(request.method, self.methodUnknown)
        req.headers = request.headers
        reqCnt.source = request.rfile

        parameters = []
        for name, value in params.items():
            if isinstance(value, list): parameters.extend([(name, v) for v in value])
            else: parameters.append((name, value))
        req.parameters = parameters

        chain.process(request=req, requestCnt=reqCnt, response=rsp, responseCnt=rspCnt)

        assert isinstance(rsp.code, Code), 'Invalid response code %s' % rsp.code

        response.headers.pop('Content-Type', None)
        response.headers['Server'] = self.serverVersion
        response.headers.update(rsp.headers)
        if ResponseHTTP.text in rsp: response.status = '%s %s' % (rsp.code.code, rsp.text)
        else: response.status = str(rsp.code.code)

        if isinstance(rspCnt.source, IOutputStream): return readGenerator(rspCnt.source)
        return rspCnt.source
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
