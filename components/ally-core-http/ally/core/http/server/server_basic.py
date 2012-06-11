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
from ally.core.http.spec.server import METHOD_OPTIONS, RequestHTTP, ResponseHTTP
from ally.core.spec.codes import Code
from ally.core.spec.server import Content, IStream, ClassesServer
from ally.design.processor import Processing, Chain
from ally.support.util_io import readGenerator
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qsl
import logging
import re

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

class RequestHandler(BaseHTTPRequestHandler):
    '''
    The server class that handles the HTTP requests.
    '''

    pathHandlers = list
    # A list that contains tuples having on the first position a regex for matching a path, and as a value 
    # the processing for handling the path.

    def __init__(self, *args):
        assert isinstance(self.pathHandlers, list), 'Invalid path handlers %s' % self.pathHandlers
        super().__init__(*args)

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

    def _process(self, method):
        url = urlparse(self.path)
        path = url.path.lstrip('/')

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

                req.scheme, req.uriRoot, req.uri = url.scheme, uriRoot, path[match.end():]
                req.parameters.extend(parse_qsl(url.query, True, False))
                break
        else:
            self.send_response(404)
            self.end_headers()
            return

        req.method = method
        req.headers.update(self.headers)
        cntReq.source = self.rfile

        chain.process(request=req, requestCnt=cntReq, response=rsp, responseCnt=cntRsp)

        assert isinstance(rsp.code, Code), 'Invalid response code %s' % rsp.code

        for name, value in rsp.headers.items(): self.send_header(name, value)

        self.send_response(rsp.code.code, rsp.text)
        self.end_headers()
        if cntRsp.source is not None:
            if isinstance(cntRsp.source, IStream): source = readGenerator(cntRsp.source)
            else: source = cntRsp.source

            for bytes in source: self.wfile.write(bytes)

        assert log.debug('Finalized request: %s and response: %s' % (req, rsp)) or True

    # ----------------------------------------------------------------

    def log_message(self, format, *args):
        #TODO: see for a better solution for this, check for next python release
        # This is a fix: whenever a message is logged there is an attempt to find some sort of host name which
        # creates a big delay whenever the request is made from a non localhost client.
        assert log.debug(format, *args) or True

# --------------------------------------------------------------------

pathHandlers = list
# A list that contains tuples having on the first position a string pattern for matching a path, and as a value 
# a list of handlers to be used for creating the context for handling the request for the path.

def run(port=80):
    assert isinstance(pathHandlers, list), 'Invalid path handlers %s' % pathHandlers
    RequestHandler.pathHandlers = []
    for pattern, handlers in pathHandlers:
        assert isinstance(pattern, str), 'Invalid pattern %s' % pattern
        classes = ClassesServer(RequestHTTP, ResponseHTTP)
        RequestHandler.pathHandlers.append((re.compile(pattern), Processing(handlers, classes)))

    try:
        server = HTTPServer(('', port), RequestHandler)
        print('=' * 50, 'Started HTTP REST API server...')
        server.serve_forever()
    except KeyboardInterrupt:
        print('=' * 50, '^C received, shutting down server')
        server.socket.close()
        return
    except:
        log.exception('=' * 50 + ' The server has stooped')
        try: server.socket.close()
        except: pass
