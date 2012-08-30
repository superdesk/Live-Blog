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
from ally.support.util_io import IOutputStream
from ally.core.http.spec.server import METHOD_OPTIONS, RequestHTTP, ResponseHTTP, \
    RequestContentHTTP, ResponseContentHTTP
from ally.core.spec.codes import Code
from ally.design.processor import Processing, Chain, Assembly, ONLY_AVAILABLE, \
    CREATE_REPORT
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
                req, reqCnt = processing.contexts['request'](), processing.contexts['requestCnt']()
                rsp, rspCnt = processing.contexts['response'](), processing.contexts['responseCnt']()
                chain = processing.newChain()

                assert isinstance(chain, Chain), 'Invalid chain %s' % chain
                assert isinstance(req, RequestHTTP), 'Invalid request %s' % req
                assert isinstance(reqCnt, RequestContentHTTP), 'Invalid request content %s' % reqCnt
                assert isinstance(rsp, ResponseHTTP), 'Invalid response %s' % rsp
                assert isinstance(rspCnt, ResponseContentHTTP), 'Invalid response content %s' % rspCnt

                req.scheme, req.uriRoot, req.uri = 'http', uriRoot, path[match.end():]
                req.parameters = parse_qsl(url.query, True, False)
                break
        else:
            self.send_response(404)
            self.end_headers()
            return

        req.method = method
        req.headers = dict(self.headers)
        reqCnt.source = self.rfile

        chain.process(request=req, requestCnt=reqCnt, response=rsp, responseCnt=rspCnt)

        assert isinstance(rsp.code, Code), 'Invalid response code %s' % rsp.code

        if ResponseHTTP.headers in rsp:
            for name, value in rsp.headers.items(): self.send_header(name, value)

        if ResponseHTTP.text in rsp: self.send_response(rsp.code.code, rsp.text)
        else: self.send_response(rsp.code.code)

        self.end_headers()

        if rspCnt.source is not None:
            if isinstance(rspCnt.source, IOutputStream): source = readGenerator(rspCnt.source)
            else: source = rspCnt.source

            for bytes in source: self.wfile.write(bytes)

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

        processing, report = assembly.create(ONLY_AVAILABLE, CREATE_REPORT,
                                             request=RequestHTTP, requestCnt=RequestContentHTTP,
                                             response=ResponseHTTP, responseCnt=ResponseContentHTTP)

        log.info('Assembly report for pattern \'%s\':\n%s', pattern, report)
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
