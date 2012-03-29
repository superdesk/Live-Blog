'''
Created on Jul 8, 2011

@package: ally core http
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the basic web server based on the python build in http server (this type of server will only run on a single
thread serving requests one at a time).
'''

from ally.api.config import GET, INSERT, UPDATE, DELETE
from ally.core.http.spec import EncoderHeader, RequestHTTP, METHOD_OPTIONS
from ally.core.spec.server import Response, Processors, ProcessorsChain, \
    ContentRequest
from collections import OrderedDict
from http.server import HTTPServer, BaseHTTPRequestHandler
import logging
import re
from urllib.parse import urlparse, parse_qsl

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

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
    
    methods = {
              'DELETE' : DELETE,
              'GET' : GET,
              'POST' : INSERT,
              'PUT' : UPDATE,
              'OPTIONS' : METHOD_OPTIONS
              }

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
        url = urlparse(self.path)
        path = url.path.lstrip('/')

        for pathRegex, processors in self.requestPaths:
            match = pathRegex.match(path)
            if match:
                chain = processors.newChain()
                assert isinstance(chain, ProcessorsChain)
                req.path = path[match.end():]
                req.rootURI = path[:match.end()]
                req.params.extend(parse_qsl(url.query, True, False))
                if not req.rootURI.endswith('/'): req.rootURI += '/'
                break
        else:
            self.send_response(404)
            self.end_headers()
            return

        req.headers.update(self.headers)
        req.content = ContentRequest(self.rfile, True)
        
        #TODO: implement proper processor for this quickfix
        ovrd = req.headers.get('X-HTTP-Method-Override')
        if ovrd: req.method = self.methods[ovrd.upper()]
        
        rsp = Response()
        chain.process(req, rsp)
        self._dispatch(rsp)
        assert log.debug('Finalized request: %s and response: %s' % (req.__dict__, rsp.__dict__)) or True

    def _dispatch(self, rsp):
        assert isinstance(rsp, Response), 'Invalid response %s' % rsp
        headers = OrderedDict()
        for headerEncoder in self.encodersHeader:
            assert isinstance(headerEncoder, EncoderHeader)
            headerEncoder.encode(headers, rsp)
        for name, value in headers.items():
            self.send_header(name, value)
        self.send_response(rsp.code.code, rsp.codeText)
        self.end_headers()
        if rsp.content:
            for bytes in rsp.content: self.wfile.write(bytes)

    def log_message(self, format, *args):
        #TODO: see for a better solution for this, check for next python release
        # This is a fix: whenever a message is logged there is an attempt to find some sort of host name which
        # creates a big delay whenever the request is made from a non localhost client.
        assert log.debug(format, *args) or True

# --------------------------------------------------------------------

def run(requestHandlerClass, port=80):
    count = 10
    while count:
        try:
            server = HTTPServer(('', port), requestHandlerClass)
            print('=' * 50, 'Started HTTP REST API server...')
            server.serve_forever()
        except KeyboardInterrupt:
            print('=' * 50, '^C received, shutting down server')
            server.socket.close()
            return
        except:
            log.exception('=' * 50 + ' The server has stooped, trying to restart')
            try: server.socket.close()
            except: pass
            count -= 1

