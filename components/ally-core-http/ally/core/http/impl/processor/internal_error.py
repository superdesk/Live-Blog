'''
Created on Jun 22, 2012

@package: ally core http
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provide the internal error representation. This is usually when the server fails badly.
'''

from ally.container.ioc import injected
from ally.design.processor.attribute import defines
from ally.design.processor.execution import Chain
from ally.exception import DevelError
from ally.http.impl.processor.internal_error import InternalErrorHandler, \
    ResponseContent, Response
from ally.http.spec.codes import INTERNAL_ERROR
import logging
import sys

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

class ResponseDevel(Response):
    '''
    The devel response context.
    '''
    # ---------------------------------------------------------------- Defined
    text = defines(str)
    errorMessage = defines(str)

# --------------------------------------------------------------------

@injected
class InternalDevelErrorHandler(InternalErrorHandler):
    '''
    Extension for @see: InternalErrorHandler that better handles the DevelError.
    '''
    
    def __init__(self):
        '''
        Construct the internal development error handler.
        '''
        assert isinstance(self.errorHeaders, dict), 'Invalid error headers %s' % self.errorHeaders
        super().__init__(response=ResponseDevel)
            
    def handleError(self, chain):
        '''
        @see: InternalErrorHandler.handleError
        
        Handle the error.
        '''
        assert isinstance(chain, Chain), 'Invalid processors chain %s' % chain
        try: response = chain.arg.response
        except AttributeError: response = ResponseDevel()
        
        try: responseCnt = chain.arg.responseCnt
        except AttributeError: responseCnt = ResponseContent()
        
        assert isinstance(response, ResponseDevel), 'Invalid response %s' % response
        assert isinstance(responseCnt, ResponseContent), 'Invalid response content %s' % responseCnt
        
        # If there is an explanation for the error occurred, we do not need to make another one
        if ResponseContent.source in responseCnt and responseCnt.source is not None: return

        exc = sys.exc_info()[1]
        if isinstance(exc, DevelError):
            log.warn('Development error occurred while processing the chain', exc_info=True)
            response.code, response.status, response.isSuccess = INTERNAL_ERROR
            response.text, response.errorMessage = 'Development error', str(exc)
            chain.proceed()
            # We try to process now the chain (where it left of) with the exception set.
            return
        
        super().handleError(chain)
