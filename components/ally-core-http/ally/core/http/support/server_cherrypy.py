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
from io import BytesIO
import cherrypy
import logging

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
        return self.wfile
        
# --------------------------------------------------------------------

@injected
class RequestHandler:
    '''
    The server class that handles the requests.
    '''
    
    processors = Processors
    # The processors used by the request handler
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
        assert isinstance(self.processors, Processors), 'Invalid processors object %s' % self.processors
        assert isinstance(self.encodersHeader, list), 'Invalid header encoders list %s' % self.encodersHeader
        
    @cherrypy.expose
    def default(self, *vpath, **params):
        chain = self.processors.newChain()
        assert isinstance(chain, ProcessorsChain)
        req = RequestHTTP()
        req.method = self.methods.get(cherrypy.request.method, self.methodUnknown)
        req.path = vpath
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
        for headerEncoder in self.encodersHeader:
            assert isinstance(headerEncoder, EncoderHeader)
            headerEncoder.encode(cherrypy.response.headers, rsp)
        cherrypy.response.status = rsp.code.code
        assert log.debug('Finalized request: %s and response: %s' % (req.__dict__, rsp.__dict__)) or True
        
        #TODO: remove
#        import time;
#        import random;
#        time.sleep(random.random() / 2.0);
        #TODO: remove
        
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
    print('Started HTTP REST API server...')
    cherrypy.quickstart(requestHandler, config={'global':{'engine.autoreload.on': False}})
