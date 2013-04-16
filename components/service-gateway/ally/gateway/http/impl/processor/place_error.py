'''
Created on Feb 8, 2013

@package: gateway service
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the gateway error parameters populating.
'''

from ally.container.ioc import injected
from ally.design.processor.attribute import requires, defines
from ally.design.processor.context import Context
from ally.design.processor.handler import HandlerProcessorProceed
from ally.http.spec.codes import METHOD_NOT_AVAILABLE
import logging

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

class Request(Context):
    '''
    The request context.
    '''
    # ---------------------------------------------------------------- Required
    parameters = defines(list)
    
class Response(Context):
    '''
    Context for response. 
    '''
    # ---------------------------------------------------------------- Defined
    status = requires(int)
    isSuccess = requires(bool)
    allows = requires(list)

# --------------------------------------------------------------------

@injected
class GatewayErrorHandler(HandlerProcessorProceed):
    '''
    Implementation for a handler that populates the gateway error parameters.
    '''
    
    nameStatus = 'status'
    # The parameter name for status.
    nameAllow = 'allow'
    # The parameter name for allow.
    
    def __init__(self):
        assert isinstance(self.nameStatus, str), 'Invalid status name %s' % self.nameStatus
        assert isinstance(self.nameAllow, str), 'Invalid allow name %s' % self.nameAllow
        super().__init__()

    def process(self, request:Request, response:Response, **keyargs):
        '''
        @see: HandlerProcessorProceed.process
        
        Places the error.
        '''
        assert isinstance(request, Request), 'Invalid request %s' % request
        assert isinstance(response, Response), 'Invalid response %s' % response
        if response.isSuccess is not False: return  # Skip if the response is not in error.
        
        assert isinstance(response.status, int), 'Invalid response status %s' % response.status
        
        if request.parameters is None: request.parameters = []
        request.parameters.insert(0, (self.nameStatus, response.status))
        if response.status == METHOD_NOT_AVAILABLE.status and response.allows is not None:
            for allow in response.allows: request.parameters.append((self.nameAllow, allow))
        
