'''
Created on Nov 23, 2011

@package: ally core http
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the cherry py web server support.
'''

from .server_basic import ContentRequestData
from ally.api.config import UPDATE, INSERT, GET, DELETE
from ally.container.ioc import injected
from ally.core.http.spec import RequestHTTP, EncoderHeader, METHOD_OPTIONS
from ally.core.spec.server import Processors, ProcessorsChain, Response
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

    requestPaths = list
    # The list[tuple(regex, Processor)] of path-processors chain tuples
    # The path is a regular expression
    # The processors is a Processors instance
    serverVersion = str
    # The server version name
    encodersHeader = list
    # The header encoders

    methods = {
               'DELETE' : DELETE,
               'GET' : GET,
               'POST' : INSERT,
               'PUT' : UPDATE,
               'OPTIONS' : METHOD_OPTIONS
               }
    methodUnknown = -1

    def __init__(self):
        assert isinstance(self.encodersHeader, list), 'Invalid header encoders list %s' % self.encodersHeader
        assert isinstance(self.serverVersion, str), 'Invalid server version %s' % self.serverVersion
        if __debug__:
            for reqPath in self.requestPaths:
                assert isinstance(reqPath, tuple), 'Invalid request paths %s' % self.requestPaths
                assert type(reqPath[0]) == type(re.compile('')), 'Invalid path regular expression %s' % reqPath[0]
                assert isinstance(reqPath[1], Processors), 'Invalid processors chain %s' % reqPath[1]

    @cherrypy.expose
    def default(self, *vpath, **params):
        request, response = cherrypy.request, cherrypy.response
        req = RequestHTTP()
        req.method = self.methods.get(request.method, self.methodUnknown)
        path = '/'.join(vpath)

        for pathRegex, processors in self.requestPaths:
            match = pathRegex.match(path)
            if match:
                chain = processors.newChain()
                assert isinstance(chain, ProcessorsChain)
                req.path = path[match.end():]
                req.rootURI = path[:match.end()]
                if not req.rootURI.endswith('/'): req.rootURI += '/'
                break
        else: raise cherrypy.HTTPError(404)

        req.headers.update(request.headers)
        for name, value in params.items():
            if isinstance(value, list):
                req.parameters.extend([(name, v) for v in value])
            else:
                req.parameters.append((name, value))

        req.content = ContentRequestData(request.rfile)

        rsp = Response()
        chain.process(req, rsp)

        response.headers.pop('Content-Type', None)
        response.headers['Server'] = self.serverVersion
        for headerEncoder in self.encodersHeader:
            assert isinstance(headerEncoder, EncoderHeader)
            headerEncoder.encode(response.headers, rsp)
        response.status = '%s %s' % (rsp.code.code, rsp.codeText)
        assert log.debug('Finalized request: %s and response: %s' % (req.__dict__, rsp.__dict__)) or True
        return rsp.content
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
