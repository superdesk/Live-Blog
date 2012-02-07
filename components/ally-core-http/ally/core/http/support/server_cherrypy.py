'''
Created on Nov 23, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the cherry py web werver support.
'''

from ally.api.operator import UPDATE, INSERT, GET, DELETE
from ally.container.ioc import injected
from ally.core.http.spec import RequestHTTP, EncoderHeader, METHOD_OPTIONS
from ally.core.spec.server import Processors, ProcessorsChain, ContentRequest, \
    Response
from ally.support.util_io import keepOpen
from io import BytesIO
import cherrypy
import logging
import re

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

class ResponseHTTP(Response):
    '''
    Provides the dispatch functionality for an HTTP response.
    '''

    def __init__(self):
        ''''
        @see: Response.__init__
        '''
        super().__init__()
        self.isDispatched = False
        self.wfile = None

    def dispatch(self):
        '''
        @see: Response.dispatch
        '''
        assert self.code is not None, 'No code provided for dispatching.'
        assert not self.isDispatched, 'Already dispatched'
        self.isDispatched = True
        self.wfile = BytesIO()
        return keepOpen(self.wfile)

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
        req = RequestHTTP()
        req.method = self.methods.get(cherrypy.request.method, self.methodUnknown)
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
        else:
            cherrypy.response.status = 404
            return ''

        req.headers.update(cherrypy.request.headers)
        for name, value in params.items():
            if isinstance(value, list):
                req.params.extend([(name, v) for v in value])
            else:
                req.params.append((name, value));
        req.content = ContentRequest(cherrypy.request.rfile, True)
        rsp = ResponseHTTP()
        chain.process(req, rsp)
        if not rsp.isDispatched:
            rsp.dispatch()
        headers = cherrypy.response.headers
        headers.pop('Content-Type', None)
        headers['Server'] = self.serverVersion
        for headerEncoder in self.encodersHeader:
            assert isinstance(headerEncoder, EncoderHeader)
            headerEncoder.encode(headers, rsp)
        cherrypy.response.status = rsp.code.code
        assert log.debug('Finalized request: %s and response: %s' % (req.__dict__, rsp.__dict__)) or True

        if rsp.wfile is not None:
            return rsp.wfile.getvalue()
        return ''

# --------------------------------------------------------------------

def run(requestHandler, host='127.0.0.1', port=80, threadPool=10):
    cherrypy.config.update({
                            'server.socket_port': port,
                            'server.socket_host': host,
                            'server.thread_pool': threadPool
                            })
    print('=' * 50, 'Started HTTP REST API server...')
    cherrypy.quickstart(requestHandler, config={'global':{'engine.autoreload.on': False}})
