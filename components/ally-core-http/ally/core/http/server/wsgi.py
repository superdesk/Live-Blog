'''
Created on Oct 23, 2012

@package: ally core http
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the WSGI web server support.
'''

from ally.api.config import UPDATE, INSERT, GET, DELETE
from ally.container.ioc import injected
from ally.core.http.spec.server import METHOD_OPTIONS, RequestHTTP, ResponseHTTP, \
    RequestContentHTTP, ResponseContentHTTP
from ally.core.spec.codes import Code
from ally.design.processor import Processing, Chain, Assembly, ONLY_AVAILABLE, \
    CREATE_REPORT
from ally.support.util_io import IOutputStream, readGenerator
from urllib.parse import parse_qsl
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
    headerPrefix = 'HTTP_'
    # The prefix used in the WSGI context for the headers.
    headers = {'CONTENT_TYPE', 'CONTENT_LENGTH'}
    # The headers to be extracted from environment, this are the exception headers, the ones that do not start with HTTP_

    methods = {
               'DELETE' : DELETE,
               'GET' : GET,
               'POST' : INSERT,
               'PUT' : UPDATE,
               'OPTIONS' : METHOD_OPTIONS
               }
    methodUnknown = -1

    # Table mapping response codes to messages; entries have the
    # form {code: (shortmessage, longmessage)}.
    # See RFC 2616.
    responses = {
        100: ('Continue', 'Request received, please continue'),
        101: ('Switching Protocols',
              'Switching to new protocol; obey Upgrade header'),

        200: ('OK', 'Request fulfilled, document follows'),
        201: ('Created', 'Document created, URL follows'),
        202: ('Accepted',
              'Request accepted, processing continues off-line'),
        203: ('Non-Authoritative Information', 'Request fulfilled from cache'),
        204: ('No Content', 'Request fulfilled, nothing follows'),
        205: ('Reset Content', 'Clear input form for further input.'),
        206: ('Partial Content', 'Partial content follows.'),

        300: ('Multiple Choices',
              'Object has several resources -- see URI list'),
        301: ('Moved Permanently', 'Object moved permanently -- see URI list'),
        302: ('Found', 'Object moved temporarily -- see URI list'),
        303: ('See Other', 'Object moved -- see Method and URL list'),
        304: ('Not Modified',
              'Document has not changed since given time'),
        305: ('Use Proxy',
              'You must use proxy specified in Location to access this '
              'resource.'),
        307: ('Temporary Redirect',
              'Object moved temporarily -- see URI list'),

        400: ('Bad Request',
              'Bad request syntax or unsupported method'),
        401: ('Unauthorized',
              'No permission -- see authorization schemes'),
        402: ('Payment Required',
              'No payment -- see charging schemes'),
        403: ('Forbidden',
              'Request forbidden -- authorization will not help'),
        404: ('Not Found', 'Nothing matches the given URI'),
        405: ('Method Not Allowed',
              'Specified method is invalid for this resource.'),
        406: ('Not Acceptable', 'URI not available in preferred format.'),
        407: ('Proxy Authentication Required', 'You must authenticate with '
              'this proxy before proceeding.'),
        408: ('Request Timeout', 'Request timed out; try again later.'),
        409: ('Conflict', 'Request conflict.'),
        410: ('Gone',
              'URI no longer exists and has been permanently removed.'),
        411: ('Length Required', 'Client must specify Content-Length.'),
        412: ('Precondition Failed', 'Precondition in headers is false.'),
        413: ('Request Entity Too Large', 'Entity is too large.'),
        414: ('Request-URI Too Long', 'URI is too long.'),
        415: ('Unsupported Media Type', 'Entity body in unsupported format.'),
        416: ('Requested Range Not Satisfiable',
              'Cannot satisfy request range.'),
        417: ('Expectation Failed',
              'Expect condition could not be satisfied.'),

        500: ('Internal Server Error', 'Server got itself in trouble'),
        501: ('Not Implemented',
              'Server does not support this operation'),
        502: ('Bad Gateway', 'Invalid responses from another server/proxy.'),
        503: ('Service Unavailable',
              'The server cannot process the request due to a high load'),
        504: ('Gateway Timeout',
              'The gateway server did not receive a timely response'),
        505: ('HTTP Version Not Supported', 'Cannot fulfill request.'),
        }

    def __init__(self):
        assert isinstance(self.pathAssemblies, list), 'Invalid path assemblies %s' % self.pathAssemblies
        assert isinstance(self.serverVersion, str), 'Invalid server version %s' % self.serverVersion
        assert isinstance(self.headerPrefix, str), 'Invalid header prefix %s' % self.headerPrefix
        assert isinstance(self.headers, set), 'Invalid headers %s' % self.headers
        assert isinstance(self.methods, dict), 'Invalid methods %s' % self.methods
        assert isinstance(self.methodUnknown, int), 'Invalid unknwon method %s' % self.methodUnknown
        assert isinstance(self.responses, dict), 'Invalid responses %s' % self.responses

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
        self.defaultHeaders = {'Server':self.serverVersion, 'Content-Type':'text'}

    def __call__(self, context, respond):
        '''
        Process the WSGI call.
        '''
        assert isinstance(context, dict), 'Invalid context %s' % context
        assert callable(respond), 'Invalid respond callable %s' % respond

        responseHeaders = dict(self.defaultHeaders)
        path, scheme = context['PATH_INFO'], context['wsgi.url_scheme']
        if path.startswith('/'): path = path[1:]

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

                req.scheme, req.uriRoot, req.uri = scheme, uriRoot, path[match.end():]
                break
        else:
            respond('404 Not Found', list(responseHeaders.items()))
            return ()

        req.method = self.methods.get(context['REQUEST_METHOD'], self.methodUnknown)
        req.parameters = parse_qsl(context['QUERY_STRING'], True, False)
        prefix, prefixLen = self.headerPrefix, len(self.headerPrefix,)
        req.headers = {hname[prefixLen:].replace('_', '-'):hvalue
                       for hname, hvalue in context.items() if hname.startswith(prefix)}
        req.headers.update({hname.replace('_', '-'):hvalue
                            for hname, hvalue in context.items() if hname in self.headers})
        reqCnt.source = context.get('wsgi.input')

        chain.process(request=req, requestCnt=reqCnt, response=rsp, responseCnt=rspCnt)

        assert isinstance(rsp.code, Code), 'Invalid response code %s' % rsp.code

        responseHeaders.update(rsp.headers)
        if ResponseHTTP.text in rsp: status = '%s %s' % (rsp.code.code, rsp.text)
        else:
            text = self.responses.get(rsp.code.code)
            if text is not None: status = '%s %s' % (rsp.code.code, text[0])
            else: status = str(rsp.code.code)

        respond(status, list(responseHeaders.items()))

        if rspCnt.source is not None:
            if isinstance(rspCnt.source, IOutputStream): return readGenerator(rspCnt.source)
            return rspCnt.source
        return ()
