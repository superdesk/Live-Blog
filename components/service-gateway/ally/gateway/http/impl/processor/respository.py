'''
Created on Apr 12, 2012

@package: gateway service
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the gateway repository processor.
'''

from ally.container.ioc import injected
from ally.design.processor.assembly import Assembly
from ally.design.processor.attribute import defines
from ally.design.processor.context import Context
from ally.design.processor.execution import Processing, Chain
from ally.design.processor.handler import HandlerBranchingProceed
from ally.design.processor.processor import Using
from ally.gateway.http.spec.gateway import IRepository, Gateway, Match
from ally.http.spec.codes import BAD_GATEWAY, isSuccess
from ally.http.spec.server import RequestHTTP, ResponseHTTP, ResponseContentHTTP, \
    HTTP_GET, HTTP, HTTP_OPTIONS
from ally.support.util_io import IInputStream
from io import BytesIO
from sched import scheduler
from threading import Thread
from urllib.parse import urlparse, parse_qsl
import codecs
import json
import logging
import time

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

class Request(Context):
    '''
    The request context.
    '''
    # ---------------------------------------------------------------- Defined
    repository = defines(IRepository)
    
class Response(Context):
    '''
    The response context.
    '''
    # ---------------------------------------------------------------- Defined
    code = defines(str)
    status = defines(int)
    isSuccess = defines(bool)
    text = defines(str)

# --------------------------------------------------------------------

class RequestGateway(RequestHTTP):
    '''
    The request gateway context.
    '''
    # ---------------------------------------------------------------- Defined
    accTypes = defines(list)
    accCharSets = defines(list)

# --------------------------------------------------------------------

@injected
class GatewayRepositoryHandler(HandlerBranchingProceed):
    '''
    Implementation for a handler that provides the gateway repository by using REST data received from either internal or
    external server. The Gateway structure is defined as in the @see: gateway-http plugin.
    '''
    
    scheme = HTTP
    # The scheme to be used in fetching the Gateway objects.
    mimeTypeJson = 'json'
    # The json mime type to be sent for the gateway requests.
    encodingJson = 'utf-8'
    # The json encoding to be sent for the gateway requests.
    uri = str
    # The URI used in fetching the gateways.
    cleanupInterval = float
    # The number of seconds to perform clean up for cached gateways.
    assembly = Assembly
    # The assembly to be used in processing the request for the gateways.
    
    def __init__(self):
        assert isinstance(self.scheme, str), 'Invalid scheme %s' % self.scheme
        assert isinstance(self.mimeTypeJson, str), 'Invalid json mime type %s' % self.mimeTypeJson
        assert isinstance(self.encodingJson, str), 'Invalid json encoding %s' % self.encodingJson
        assert isinstance(self.uri, str), 'Invalid URI %s' % self.uri
        assert isinstance(self.cleanupInterval, int), 'Invalid cleanup interval %s' % self.cleanupInterval
        assert isinstance(self.assembly, Assembly), 'Invalid assembly %s' % self.assembly
        super().__init__(Using(self.assembly, request=RequestGateway).sources('requestCnt', 'response', 'responseCnt'))
        self.initialize()

    def process(self, processing, request:Request, response:Response, **keyargs):
        '''
        @see: HandlerBranchingProceed.process
        
        Obtains the repository.
        '''
        assert isinstance(processing, Processing), 'Invalid processing %s' % processing
        assert isinstance(request, Request), 'Invalid request %s' % request
        assert isinstance(response, Response), 'Invalid response %s' % response
        
        if not self._repository:
            robj, status, text = self.obtainGateways(processing, self.uri)
            if robj is None or not isSuccess(status):
                log.info('Cannot fetch the gateways from URI \'%s\', with response %s %s', self.uri, status, text)
                response.code, response.status, response.isSuccess = BAD_GATEWAY
                response.text = text
                return
            self._repository = Repository(robj)
        request.repository = self._repository
        
    # ----------------------------------------------------------------
   
    def obtainGateways(self, processing, uri):
        '''
        Get the gateway objects representation.
        
        @param processing: Processing
            The processing used for delivering the request.
        @param uri: string
            The URI to call, parameters are allowed.
        @return: tuple(dictionary{...}|None, integer, string)
            A tuple containing as the first position the gateway objects representation, None if the gateways cannot be fetched,
            on the second position the response status and on the last position the response text.
        '''
        assert isinstance(processing, Processing), 'Invalid processing %s' % processing
        assert isinstance(uri, str), 'Invalid URI %s' % uri
        
        request = processing.ctx.request()
        assert isinstance(request, RequestGateway), 'Invalid request %s' % request
        
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
        return json.load(codecs.getreader(self.encodingJson)(source)), response.status, text

    # ----------------------------------------------------------------
    
    def initialize(self):
        '''
        Initialize the repository.
        '''
        self._repository = None
        self.startCleanupThread('Cleanup gateways thread')
   
    def startCleanupThread(self, name):
        '''
        Starts the cleanup thread.
        
        @param name: string
            The name for the thread.
        '''
        schedule = scheduler(time.time, time.sleep)
        def executeCleanup():
            self.performCleanup()
            schedule.enter(self.cleanupInterval, 1, executeCleanup, ())
        schedule.enter(self.cleanupInterval, 1, executeCleanup, ())
        scheduleRunner = Thread(name=name, target=schedule.run)
        scheduleRunner.daemon = True
        scheduleRunner.start()

    def performCleanup(self):
        '''
        Performs the cleanup for gateways.
        '''
        self._repository = None
        
# --------------------------------------------------------------------

class Repository(IRepository):
    '''
    The gateways repository.
    '''
    __slots__ = ('_gateways', '_cache')
    
    def __init__(self, objs):
        '''
        Construct the gateways repository based on the provided dictionary object.
        
        @param objs: dictionary{string: list[dictionary{...}]}
            The dictionary used for defining the repository gateways, the objects as is defined from response.
        '''
        assert isinstance(objs, dict), 'Invalid objects %s' % objs
        assert 'GatewayList' in objs, 'Invalid objects %s, not GatewayList' % objs
        
        self._gateways = [Gateway(obj) for obj in objs['GatewayList']]
        self._cache = {}
        
    def find(self, method=None, headers=None, uri=None, error=None):
        '''
        @see: IRepository.find
        '''
        for gateway in self._gateways:
            groupsURI = self._macth(gateway, method, headers, uri, error)
            if groupsURI is not None: return Match(gateway, groupsURI)
        
    def allowsFor(self, headers=None, uri=None):
        '''
        @see: IRepository.allowsFor
        '''
        allowed = set()
        for gateway in self._gateways:
            assert isinstance(gateway, Gateway)
            groupsURI = self._macth(gateway, None, headers, uri, None)
            if groupsURI is not None: allowed.update(gateway.methods)
        # We need to remove auxiliar methods
        allowed.discard(HTTP_OPTIONS)
        return allowed
        
    def obtainCache(self, identifier):
        '''
        @see: IRepository.obtainCache
        '''
        cache = self._cache.get(identifier)
        if cache is None: cache = self._cache[identifier] = {}
        return cache

    # ----------------------------------------------------------------
    
    def _macth(self, gateway, method, headers, uri, error):
        '''
        Checks the match for the provided gateway and parameters.
        
        @return: tuple(string)|None
            The URI match groups, None if there is no match.
        '''
        assert isinstance(gateway, Gateway)
        groupsURI = ()
        
        if method is not None:
            assert isinstance(method, str), 'Invalid method %s' % method
            if gateway.methods:
                if method.upper() not in gateway.methods: return
        
        if headers is not None:
            assert isinstance(headers, dict), 'Invalid headers %s' % uri
            isOk = False
            if gateway.headers:
                for nameValue in headers.items():
                    header = '%s:%s' % nameValue
                    for pattern in gateway.headers:
                        if pattern.match(header):
                            isOk = True
                            break
                    if isOk: break
                if not isOk: return
        elif gateway.headers: return
                
        if uri is not None:
            assert isinstance(uri, str), 'Invalid URI %s' % uri
            if gateway.pattern:
                matcher = gateway.pattern.match(uri)
                if matcher: groupsURI = matcher.groups()
                else: return
        elif gateway.pattern: return
                
        if error is not None:
            assert isinstance(error, int), 'Invalid error %s' % error
            if gateway.errors:
                if error not in gateway.errors: return
            else: return
        elif gateway.errors: return
            
        return groupsURI
