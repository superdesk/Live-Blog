'''
Created on Oct 23, 2012

@package: ally http
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the WSGI web server support.
'''

from ally.container.ioc import injected
from ally.design.processor.assembly import Assembly
from ally.design.processor.execution import Processing, Chain
from ally.http.spec.server import RequestHTTP, ResponseHTTP, RequestContentHTTP, \
    ResponseContentHTTP
from ally.support.util_io import IInputStream, readGenerator
from urllib.parse import parse_qsl
import logging

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

@injected
class RequestHandler:
    '''
    The server class that handles the requests.
    '''
    
    serverVersion = str
    # The server version name
    headerPrefix = 'HTTP_'
    # The prefix used in the WSGI context for the headers.
    headers = {'CONTENT_TYPE', 'CONTENT_LENGTH'}
    # The headers to be extracted from environment, this are the exception headers, the ones that do not start with HTTP_
    assembly = Assembly
    # The assembly used for resolving the requests

    def __init__(self):
        assert isinstance(self.serverVersion, str), 'Invalid server version %s' % self.serverVersion
        assert isinstance(self.headerPrefix, str), 'Invalid header prefix %s' % self.headerPrefix
        assert isinstance(self.headers, set), 'Invalid headers %s' % self.headers
        assert isinstance(self.responses, dict), 'Invalid responses %s' % self.responses
        assert isinstance(self.assembly, Assembly), 'Invalid assembly %s' % self.assembly
        
        self.processing = self.assembly.create(request=RequestHTTP, requestCnt=RequestContentHTTP,
                                               response=ResponseHTTP, responseCnt=ResponseContentHTTP)
        
        self.defaultHeaders = {'Server':self.serverVersion, 'Content-Type':'text'}
        self.headerPrefixLen = len(self.headerPrefix)

    def __call__(self, context, respond):
        '''
        Process the WSGI call.
        '''
        assert isinstance(context, dict), 'Invalid context %s' % context
        assert callable(respond), 'Invalid respond callable %s' % respond
        
        proc = self.processing
        assert isinstance(proc, Processing), 'Invalid processing %s' % proc
        
        request, requestCnt = proc.ctx.request(), proc.ctx.requestCnt()
        assert isinstance(request, RequestHTTP), 'Invalid request %s' % request
        assert isinstance(requestCnt, RequestContentHTTP), 'Invalid request content %s' % requestCnt

        request.scheme, request.method = context.get('wsgi.url_scheme', '').upper(), context.get('REQUEST_METHOD', '').upper()
        request.headers = {hname[self.headerPrefixLen:].replace('_', '-'):hvalue
                           for hname, hvalue in context.items() if hname.startswith(self.headerPrefix)}
        request.headers.update({hname.replace('_', '-'):hvalue
                                for hname, hvalue in context.items() if hname in self.headers})
        request.uri = context.get('PATH_INFO', '').lstrip('/')
        request.parameters = parse_qsl(context.get('QUERY_STRING', ''), True, False)

        requestCnt.source = context.get('wsgi.input')

        chain = Chain(proc)
        chain.process(request=request, requestCnt=requestCnt,
                      response=proc.ctx.response(), responseCnt=proc.ctx.responseCnt()).doAll()

        response, responseCnt = chain.arg.response, chain.arg.responseCnt
        assert isinstance(response, ResponseHTTP), 'Invalid response %s' % response
        assert isinstance(responseCnt, ResponseContentHTTP), 'Invalid response content %s' % responseCnt

        responseHeaders = dict(self.defaultHeaders)
        if ResponseHTTP.headers in response and response.headers is not None: responseHeaders.update(response.headers)
        
        assert isinstance(response.status, int), 'Invalid response status code %s' % response.status
        if ResponseHTTP.text in response and response.text: status = '%s %s' % (response.status, response.text)
        elif ResponseHTTP.code in response and response.code: status = '%s %s' % (response.status, response.code)
        else: status = str(response.status)
        respond(status, list(responseHeaders.items()))

        if ResponseContentHTTP.source in responseCnt and responseCnt.source is not None:
            if isinstance(responseCnt.source, IInputStream): return readGenerator(responseCnt.source)
            return responseCnt.source
        return ()
