'''
Created on Feb 13, 2013

@package: ally http
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Forwards the requests to an external server.
'''

from ally.container.ioc import injected
from ally.design.processor.attribute import requires, defines
from ally.design.processor.context import Context
from ally.design.processor.handler import HandlerProcessorProceed
from ally.http.spec.server import HTTP
from ally.support.util_io import IInputStream, writeGenerator
from collections import Iterable
from http.client import HTTPConnection
from io import BytesIO
from urllib.parse import urlencode, urlunsplit
import logging
import socket
from ally.http.spec.codes import SERVICE_UNAVAILABLE

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

class Request(Context):
    '''
    Context for request. 
    '''
    # ---------------------------------------------------------------- Required
    scheme = requires(str)
    method = requires(str)
    uri = requires(str)
    parameters = requires(list)
    headers = requires(dict)

class RequestContent(Context):
    '''
    Context for request content. 
    '''
    # ---------------------------------------------------------------- Required
    source = requires(IInputStream, Iterable)

class Response(Context):
    '''
    Context for response. 
    '''
    # ---------------------------------------------------------------- Defined
    code = defines(str)
    status = defines(int)
    text = defines(str)
    headers = defines(dict)

class ResponseContent(Context):
    '''
    Context for response content. 
    '''
    # ---------------------------------------------------------------- Required
    source = defines(IInputStream)

# --------------------------------------------------------------------

@injected
class ForwardHTTPHandler(HandlerProcessorProceed):
    '''
    Implementation for a handler that provides forwarding to external servers.
    '''
    
    externalHost = str
    # The external server host.
    externalPort = int
    # The external server port.
    
    def __init__(self):
        assert isinstance(self.externalHost, str), 'Invalid external host %s' % self.externalHost
        assert isinstance(self.externalPort, int), 'Invalid external port %s' % self.externalPort
        super().__init__()

    def process(self, request:Request, requestCnt:RequestContent, response:Response, responseCnt:ResponseContent, **keyargs):
        '''
        @see: HandlerProcessorProceed.process
        
        Process the forward.
        '''
        assert isinstance(request, Request), 'Invalid request %s' % request
        assert isinstance(requestCnt, RequestContent), 'Invalid request content %s' % requestCnt
        assert isinstance(response, Response), 'Invalid response %s' % response
        assert isinstance(responseCnt, ResponseContent), 'Invalid response content %s' % responseCnt
        assert request.scheme == HTTP, 'Cannot forward for scheme %s' % request.scheme
        
        if requestCnt.source is not None:
            if isinstance(requestCnt.source, Iterable):
                body = writeGenerator(requestCnt.source, BytesIO()).getvalue()
            else:
                assert isinstance(requestCnt.source, IInputStream), 'Invalid request source %s' % requestCnt.source
                body = requestCnt.source.read()
        else: body = None
        
        if request.parameters: parameters = urlencode(request.parameters)
        else: parameters = None
        
        connection = HTTPConnection(self.externalHost, self.externalPort)
        try:
            connection.request(request.method, urlunsplit(('', '', '/%s' % request.uri, parameters, '')), body, request.headers)
        except socket.error as e:
            response.code, response.status, _isSuccess = SERVICE_UNAVAILABLE
            if e.errno == 111: response.text = 'Connection refused'
            else: response.text = str(e)
            return
        
        rsp = connection.getresponse()
        response.status = rsp.status
        response.code = response.text = rsp.reason
        response.headers = dict(rsp.headers.items())
        responseCnt.source = rsp

