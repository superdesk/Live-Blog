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
from ally.core.http.spec.server import METHOD_OPTIONS, RequestHTTP, ResponseHTTP, \
    RequestContentHTTP, ResponseContentHTTP
from ally.core.spec.codes import Code
from ally.core.spec.server import IStream
from ally.design.processor import Processing, Chain, Assembly
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

    pathProcessing = list
    # A list that contains tuples having on the first position a regex for matching a path, and the second value 
    # the processing for handling the path.

    def __init__(self, *args):
        assert isinstance(self.pathProcessing, list), 'Invalid path processing %s' % self.pathProcessing
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

        for regex, processing in self.pathProcessing:
            match = regex.match(path)
            if match:
                uriRoot = path[:match.end()]
                if not uriRoot.endswith('/'): uriRoot += '/'

                assert isinstance(processing, Processing), 'Invalid processing %s' % processing
                request, requestCnt = processing.contexts['request'](), processing.contexts['requestCnt']()
                response, responseCnt = processing.contexts['response'](), processing.contexts['responseCnt']()

                chain = processing.newChain()

                assert isinstance(chain, Chain), 'Invalid chain %s' % chain
                assert isinstance(request, RequestHTTP), 'Invalid request %s' % request
                assert isinstance(response, ResponseHTTP), 'Invalid response %s' % response
                assert isinstance(requestCnt, RequestContentHTTP), 'Invalid request content %s' % requestCnt
                assert isinstance(responseCnt, ResponseContentHTTP), 'Invalid response content %s' % responseCnt

                request.scheme, request.uriRoot, request.uri = url.scheme, uriRoot, path[match.end():]
                request.parameters = parse_qsl(url.query, True, False)
                break
        else:
            self.send_response(404)
            self.end_headers()
            return

        de continuat
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

pathAssemblies = list
# A list that contains tuples having on the first position a string pattern for matching a path, and as a value 
# the assembly to be used for creating the context for handling the request for the path.

def run(port=80):
    assert isinstance(pathAssemblies, list), 'Invalid path assemblies %s' % pathAssemblies
    RequestHandler.pathProcessing = []
    for pattern, assembly in pathAssemblies:
        assert isinstance(pattern, str), 'Invalid pattern %s' % pattern
        assert isinstance(assembly, Assembly), 'Invalid assembly %s' % assembly

        processing = assembly.create(request=RequestHTTP, requestCnt=RequestContentHTTP,
                                     response=ResponseHTTP, responseCnt=ResponseContentHTTP)
        RequestHandler.pathProcessing.append((re.compile(pattern), processing))

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
