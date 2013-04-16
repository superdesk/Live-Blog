'''
Created on Apr 12, 2012

@package: gateway service
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the gateway repository processor.
'''

from .respository import GatewayRepositoryHandler, Repository
from ally.container.ioc import injected
from ally.design.processor.attribute import requires, defines
from ally.design.processor.context import Context
from ally.design.processor.execution import Processing
from ally.gateway.http.spec.gateway import IRepository, Match
from ally.http.spec.codes import BAD_REQUEST, BAD_GATEWAY, INVALID_AUTHORIZATION, \
    isSuccess
from ally.http.spec.server import IDecoderHeader
from datetime import datetime, timedelta
import logging

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

class Request(Context):
    '''
    The request context.
    '''
    # ---------------------------------------------------------------- Defined
    repository = defines(IRepository)
    match = defines(Match)
    # ---------------------------------------------------------------- Required
    decoderHeader = requires(IDecoderHeader)

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

@injected
class GatewayAuthorizedRepositoryHandler(GatewayRepositoryHandler):
    '''
    Extension for @see: GatewayRepositoryHandler that provides the service for authorized gateways.
    '''
    
    nameAuthorization = 'Authorization'
    # The header name for the session identifier.
    
    def __init__(self):
        assert isinstance(self.nameAuthorization, str), 'Invalid authorization name %s' % self.nameAuthorization
        super().__init__()
        
        self._timeOut = timedelta(seconds=self.cleanupInterval)

    def process(self, processing, request:Request, response:Response, **keyargs):
        '''
        @see: HandlerBranchingProceed.process
        
        Obtains the repository.
        '''
        assert isinstance(processing, Processing), 'Invalid processing %s' % processing
        assert isinstance(request, Request), 'Invalid request %s' % request
        if response.isSuccess is False: return  # Skip in case the response is in error
        
        assert isinstance(request.decoderHeader, IDecoderHeader), 'Invalid decoder header %s' % request.decoderHeader
        authentication = request.decoderHeader.retrieve(self.nameAuthorization)
        if not authentication: return
        
        repository = self._repositories.get(authentication)
        if repository is None:
            robj, status, text = self.obtainGateways(processing, self.uri % authentication)
            if robj is None or not isSuccess(status):
                if status == BAD_REQUEST.status:
                    response.code, response.status, response.isSuccess = INVALID_AUTHORIZATION
                    if request.repository:
                        assert isinstance(request.repository, IRepository), 'Invalid repository %s' % request.repository
                        request.match = request.repository.find(request.method, request.headers, request.uri,
                                                                INVALID_AUTHORIZATION.status)
                else:
                    log.info('Cannot fetch the authorized gateways from URI \'%s\', with response %s %s', self.uri, status, text)
                    response.code, response.status, response.isSuccess = BAD_GATEWAY
                    response.text = text
                return
            repository = self._repositories[authentication] = Repository(robj)
        self._lastAccess[authentication] = datetime.now()
        
        if request.repository: request.repository = RepositoryJoined(repository, request.repository)
        else: request.repository = repository
    
    # ----------------------------------------------------------------
    
    def initialize(self):
        '''
        @see: GatewayRepositoryHandler.initialize
        '''
        self._repositories = {}
        self._lastAccess = {}
        self.startCleanupThread('Cleanup authorized gateways thread')

    def performCleanup(self):
        '''
        @see: GatewayRepositoryHandler.performCleanup
        '''
        current, expired = datetime.now() - self._timeOut, []
        for authentication, lastAccess in self._lastAccess.items():
            if current > lastAccess: expired.append(authentication)
        
        assert log.debug('Clearing %s sessions at %s' % (len(expired), datetime.now())) or True
        for authentication in expired:
            self._repositories.pop(authentication, None)
            self._lastAccess.pop(authentication, None)

# --------------------------------------------------------------------

class RepositoryJoined(IRepository):
    '''
    Repository that uses other repositories to provide services.
    '''
    __slots__ = ('_repositories',)
    
    def __init__(self, main, *repositories):
        '''
        Construct the joined repositories.
        
        @param main: IRepository
            The main repository, this will be used for storing caches.
        @param repositories: arguments[IRepository]
            The repositories to join with the main repositories.
        '''
        assert isinstance(main, IRepository), 'Invalid main repository %s' % main
        assert repositories, 'At least one other repository is required for joining'
        if __debug__:
            for repository in repositories: assert isinstance(repository, IRepository), 'Invalid repository %s' % repository
        
        self._repositories = [main]
        self._repositories.extend(repositories)
        
    def find(self, method=None, headers=None, uri=None, error=None):
        '''
        @see: IRepository.find
        '''
        for repository in self._repositories:
            assert isinstance(repository, IRepository), 'Invalid repository %s' % repository
            match = repository.find(method, headers, uri, error)
            if match is not None: return match
        
    def allowsFor(self, headers=None, uri=None):
        '''
        @see: IRepository.allowsFor
        '''
        allowed = set()
        for repository in self._repositories:
            assert isinstance(repository, IRepository), 'Invalid repository %s' % repository
            allowed.update(repository.allowsFor(headers, uri))
        return allowed
        
    def obtainCache(self, identifier):
        '''
        @see: IRepository.obtainCache
        '''
        return self._repositories[0].obtainCache(identifier)
