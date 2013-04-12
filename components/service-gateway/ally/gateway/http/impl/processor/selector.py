'''
Created on Feb 8, 2013

@package: gateway service
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the gateway repository selector processor.
'''

from ally.container.ioc import injected
from ally.design.processor.attribute import requires, defines
from ally.design.processor.context import Context
from ally.design.processor.handler import HandlerProcessorProceed
from ally.gateway.http.spec.gateway import IRepository, Match
from ally.http.spec.codes import PATH_NOT_FOUND, METHOD_NOT_AVAILABLE

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
    # ---------------------------------------------------------------- Defined
    match = defines(Match)
    
class Response(Context):
    '''
    Context for response. 
    '''
    # ---------------------------------------------------------------- Defined
    code = defines(str)
    status = defines(int)
    isSuccess = defines(bool)
    allows = defines(list)

# --------------------------------------------------------------------

@injected
class GatewaySelectorHandler(HandlerProcessorProceed):
    '''
    Implementation for a handler that provides the gateway repository selector. This handler will pick the appropriate gateway
    for processing.
    '''

    def process(self, request:Request, response:Response, **keyargs):
        '''
        @see: HandlerProcessorProceed.process
        
        Provides the gateway selection.
        '''
        assert isinstance(request, Request), 'Invalid request %s' % request
        assert isinstance(response, Response), 'Invalid response %s' % response
        if response.isSuccess is False: return  # Skip in case the response is in error
        
        assert isinstance(request.repository, IRepository), 'Invalid request repository %s' % request.repository
        request.match = request.repository.find(request.method, request.headers, request.uri)
        if not request.match:
            allows = request.repository.allowsFor(request.headers, request.uri)
            if allows:
                response.code, response.status, response.isSuccess = METHOD_NOT_AVAILABLE
                if response.allows is None: response.allows = list(allows)
                else: response.allows.extend(allows)
                request.match = request.repository.find(request.method, request.headers, request.uri, METHOD_NOT_AVAILABLE.status)
            else:
                response.code, response.status, response.isSuccess = PATH_NOT_FOUND
                request.match = request.repository.find(request.method, request.headers, request.uri, PATH_NOT_FOUND.status)
