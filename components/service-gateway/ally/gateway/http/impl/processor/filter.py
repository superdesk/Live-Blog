'''
Created on Feb 8, 2013

@package: gateway service
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the gateway filter processor.
'''

from ally.container.ioc import injected
from ally.design.processor.assembly import Assembly
from ally.design.processor.attribute import requires, defines
from ally.design.processor.context import Context
from ally.design.processor.execution import Processing, Chain
from ally.design.processor.handler import HandlerBranchingProceed
from ally.design.processor.processor import Using
from ally.gateway.http.spec.gateway import IRepository, Match, Gateway
from ally.http.spec.codes import FORBIDDEN_ACCESS, BAD_GATEWAY, isSuccess
from ally.http.spec.server import HTTP, RequestHTTP, ResponseContentHTTP, \
    ResponseHTTP, HTTP_GET
from ally.support.util_io import IInputStream
from babel.compat import BytesIO
from urllib.parse import urlparse, parse_qsl
import codecs
import json
import logging

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

class Request(Context):
    '''
    The request context.
    '''
    # ---------------------------------------------------------------- Required
    method = requires(str)
    headers = requires(dict)
    uri = requires(str)
    repository = requires(IRepository)
    match = requires(Match)
    
class Response(Context):
    '''
    Context for response. 
    '''
    # ---------------------------------------------------------------- Defined
    code = defines(str)
    status = defines(int)
    isSuccess = defines(bool)
    text = defines(str)
    
class RequestFilter(RequestHTTP):
    '''
    The request filter context.
    '''
    # ---------------------------------------------------------------- Defined
    accTypes = defines(list)
    accCharSets = defines(list)

# --------------------------------------------------------------------

@injected
class GatewayFilterHandler(HandlerBranchingProceed):
    '''
    Implementation for a handler that provides the gateway filter.
    '''
    
    scheme = HTTP
    # The scheme to be used in calling the filters.
    mimeTypeJson = 'json'
    # The json mime type to be sent for the filter requests.
    encodingJson = 'utf-8'
    # The json encoding to be sent for the gateway requests.
    assembly = Assembly
    # The assembly to be used in processing the request for the filters.
    
    def __init__(self):
        assert isinstance(self.scheme, str), 'Invalid scheme %s' % self.scheme
        assert isinstance(self.mimeTypeJson, str), 'Invalid json mime type %s' % self.mimeTypeJson
        assert isinstance(self.encodingJson, str), 'Invalid json encoding %s' % self.encodingJson
        assert isinstance(self.assembly, Assembly), 'Invalid assembly %s' % self.assembly
        super().__init__(Using(self.assembly, request=RequestFilter).sources('requestCnt', 'response', 'responseCnt'))

    def process(self, processing, request:Request, response:Response, **keyargs):
        '''
        @see: HandlerBranchingProceed.process
        '''
        assert isinstance(processing, Processing), 'Invalid processing %s' % processing
        assert isinstance(request, Request), 'Invalid request %s' % request
        assert isinstance(response, Response), 'Invalid response %s' % response
        if not request.match: return  # No filtering is required if there is no match on request
        
        assert isinstance(request.repository, IRepository), 'Invalid request repository %s' % request.repository
        match = request.match
        assert isinstance(match, Match), 'Invalid response match %s' % match
        assert isinstance(match.gateway, Gateway), 'Invalid gateway %s' % match.gateway
        
        cache = request.repository.obtainCache('filters')
        assert isinstance(cache, dict), 'Invalid cache %s' % cache
        if match.gateway.filters:
            for filterURI in match.gateway.filters:
                assert isinstance(filterURI, str), 'Invalid filter %s' % filterURI
                try: filterURI = filterURI.format(None, *match.groupsURI)
                except IndexError:
                    response.code, response.status, response.isSuccess = BAD_GATEWAY
                    response.text = 'Invalid filter URI \'%s\' for groups %s' % (filterURI, match.groupsURI)
                    return
                
                isAllowed = cache.get(filterURI)
                if isAllowed is None:
                    isAllowed, status, text = self.obtainFilter(processing, filterURI)
                    if isAllowed is None:
                        log.info('Cannot fetch the filter from URI \'%s\', with response %s %s', request.uri, status, text)
                        response.code, response.status, response.isSuccess = BAD_GATEWAY
                        response.text = text
                        return
                    cache[filterURI] = isAllowed
                
                if not isAllowed:
                    response.code, response.status, response.isSuccess = FORBIDDEN_ACCESS
                    request.match = request.repository.find(request.method, request.headers, request.uri, FORBIDDEN_ACCESS.status)
                    return
                
    # ----------------------------------------------------------------
    
    def obtainFilter(self, processing, uri):
        '''
        Checks the filter URI.
        
        @param processing: Processing
            The processing used for delivering the request.
        @param uri: string
            The URI to call, parameters are allowed.
        @return: boolean
            True if the filter URI provided a True value, False otherwise.
        @return: tuple(boolean|None, integer, string)
            A tuple containing as the first True if the filter URI provided a True value, None if the filter cannot be fetched,
            on the second position the response status and on the last position the response text.
        '''
        assert isinstance(processing, Processing), 'Invalid processing %s' % processing
        assert isinstance(uri, str), 'Invalid URI %s' % uri
        
        request = processing.ctx.request()
        assert isinstance(request, RequestFilter), 'Invalid request %s' % request
        
        url = urlparse(uri)
        request.scheme, request.method = self.scheme, HTTP_GET
        request.headers = {}
        request.uri = url.path.lstrip('/')
        request.parameters = parse_qsl(url.query, True, False)
        request.accTypes = [self.mimeTypeJson]
        request.accCharSets = [self.encodingJson]
        
        chain = Chain(processing)
        chain.process(request=request, requestCnt=processing.ctx.requestCnt(),
                      response=processing.ctx.response(), responseCnt=processing.ctx.responseCnt()).doAll()

        response, responseCnt = chain.arg.response, chain.arg.responseCnt
        assert isinstance(response, ResponseHTTP), 'Invalid response %s' % response
        assert isinstance(responseCnt, ResponseContentHTTP), 'Invalid response content %s' % responseCnt
        
        if ResponseHTTP.text in response and response.text: text = response.text
        elif ResponseHTTP.code in response and response.code: text = response.code
        else: text = None
        if ResponseContentHTTP.source not in responseCnt or responseCnt.source is None or not isSuccess(response.status):
            return None, response.status, text
        
        if isinstance(responseCnt.source, IInputStream):
            source = responseCnt.source
        else:
            source = BytesIO()
            for bytes in responseCnt.source: source.write(bytes)
            source.seek(0)
        allowed = json.load(codecs.getreader(self.encodingJson)(source))
        return allowed['HasAccess'] == 'True', response.status, text
