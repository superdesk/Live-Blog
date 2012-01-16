'''
Created on Jul 8, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the basic web server based on the python build in http server (this type of server will only run on a single
thread serving requests one at a time).
'''

from ally.api.operator import GET, INSERT, UPDATE, DELETE
from ally.core.spec.server import Response, Processors, ProcessorsChain, \
    ContentRequest
from ally.core.http.spec import EncoderHeader, RequestHTTP, METHOD_OPTIONS
from collections import OrderedDict
from http.server import HTTPServer, BaseHTTPRequestHandler
import logging
import re

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

class ResponseHTTP(Response):
    '''
    Provides the dispatch functionality for an HTTP response.
    '''

    def __init__(self, requestHandler):
        ''''
        @see: Response.__init__
        
        @param requestHandler: RequestHandler
            The request handler used for rendering response data.
        '''
        super().__init__()
        assert isinstance(requestHandler, RequestHandler), 'Invalid request handler %s' % requestHandler
        self.requestHandler = requestHandler
        self.isDispatched = False

    def dispatch(self):
        '''
        @see: Response.dispatch
        '''
        assert self.code is not None, 'No code provided for dispatching.'
        assert not self.isDispatched, 'Already dispatched'
        rq = self.requestHandler
        assert isinstance(rq, RequestHandler)
        headers = OrderedDict()
        for headerEncoder in rq.encodersHeader:
            assert isinstance(headerEncoder, EncoderHeader)
            headerEncoder.encode(headers, self)
        for name, value in headers.items():
            rq.send_header(name, value)
        rq.send_response(self.code.code, self.codeText)
        rq.end_headers()
        self.isDispatched = True
        return rq.wfile

# --------------------------------------------------------------------

class RequestHandler(BaseHTTPRequestHandler):
    '''
    The server class that handles the HTTP requests.
    '''

    requestPaths = list
    # The list of path-processors chain tuples
    # The path is a regular expression
    # The processors is a Processors instance

    encodersHeader = list
    # The header encoders

    def do_GET(self):
        self._process(GET)

    def do_POST(self):
        self._process(INSERT)

    def do_PUT(self):
        self._process(UPDATE)

    def do_DELETE(self):
        self._process(DELETE)

    def do_OPTIONS(self):
        self._process(METHOD_OPTIONS)

    # ----------------------------------------------------------------

    def __init__(self, *args):
        super().__init__(*args)
        assert isinstance(self.encodersHeader, list), 'Invalid header encoders list %s' % self.encodersHeader
        if __debug__:
            for reqPath in self.requestPaths:
                assert isinstance(reqPath, tuple), 'Invalid request paths %s' % self.requestPaths
                assert type(reqPath[0]) == type(re.compile('')), 'Invalid path regular expression %s' % reqPath[0]
                assert isinstance(reqPath[1], Processors), 'Invalid processors chain %s' % reqPath[1]


    def _process(self, method):
        req = RequestHTTP()
        req.method = method
        path = self.path.lstrip('/')

        chain = None
        for pathRegex, processors in self.requestPaths:
            match = pathRegex.match(path)
            if match:
                chain = processors.newChain()
                assert isinstance(chain, ProcessorsChain)
                req.path = path[match.end():]
                break
        if chain is None:
            self.send_response(404)
            self.end_headers()
            return

        req.headers.update(self.headers)
        req.content = ContentRequest(self.rfile)
        rsp = ResponseHTTP(self)
        chain.process(req, rsp)
        if not rsp.isDispatched:
            rsp.dispatch()
        assert log.debug('Finalized request: %s and response: %s' % (req.__dict__, rsp.__dict__)) or True

    def log_message(self, format, *args):
        #TODO: see for a better solution for this, check for next python release
        # This is a fix: whenever a message is logged there is an attempt to find some sort of host name which
        # creates a big delay whenever the request is made from a non localhost client.
        assert log.debug(format, *args) or True

# --------------------------------------------------------------------

def run(requestHandlerClass, port = 80):
    while True:
        try:
            server = HTTPServer(('', port), requestHandlerClass)
            print('Started HTTP REST API server...')
            server.serve_forever()
        except KeyboardInterrupt:
            print('^C received, shutting down server')
            server.socket.close()
            return
        except:
            log.exception('-' * 50 + 'The server has stooped, trying to restart')
            try: server.socket.close()
            except: pass

