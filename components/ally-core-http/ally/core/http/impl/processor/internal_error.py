'''
Created on Jun 22, 2012

@package: ally core
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provide the internal error representation. This is usually when the server fails badly.
'''

from ally.container.ioc import injected
from ally.core.spec.codes import Code, INTERNAL_ERROR, BAD_CONTENT
from ally.design.context import defines, Context
from ally.design.processor import HandlerProcessor, Chain
from ally.support.util_io import IOutputStream, convertToBytes
from collections import Iterable
from io import BytesIO, StringIO
import logging
import traceback
from ally.exception import DevelError

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

class Response(Context):
    '''
    The response context.
    '''
    # ---------------------------------------------------------------- Defined
    code = defines(Code)
    text = defines(str)
    errorMessage = defines(str)
    headers = defines(dict)

class ResponseContent(Context):
    '''
    The response content context.
    '''
    # ---------------------------------------------------------------- Optional
    source = defines(IOutputStream, Iterable)

# --------------------------------------------------------------------

@injected
class InternalErrorHandler(HandlerProcessor):
    '''
    Implementation for a processor that provides the handling of internal errors.
    '''

    errorHeaders = {'Content-Type':'text'}
    # The headers that will be placed on the response.

    def __init__(self):
        '''
        Construct the internal error handler.
        '''
        assert isinstance(self.errorHeaders, dict), 'Invalid error headers %s' % self.errorHeaders
        super().__init__()

    def process(self, chain, response:Response, responseCnt:ResponseContent, **keyargs):
        '''
        @see: HandlerProcessor.process
        
        Provides the additional arguments by type to be populated.
        '''
        assert isinstance(chain, Chain), 'Invalid processors chain %s' % chain
        assert isinstance(response, Response), 'Invalid response %s' % response
        assert isinstance(responseCnt, ResponseContent), 'Invalid response content %s' % responseCnt

        error = None
        try:
            try:
                chain.process(response=response, responseCnt=responseCnt, **keyargs)
                # We process the chain internally so we might cache any exception.
            except DevelError as e:
                log.warn('Exception occurred while processing the chain', exc_info=True)
                response.code, response.text, response.errorMessage = BAD_CONTENT, 'Development error', str(e)
                chain.process(response=response, responseCnt=responseCnt, **keyargs)
                # We try to process now the chain (where it left of) with the exception set.
        except:
            log.exception('Exception occurred while processing the chain')
            error = StringIO()
            traceback.print_exc(file=error)
        else:
            if __debug__ and isinstance(responseCnt.source, Iterable):
                # If in debug mode and the response content has a source generator then we will try to read that
                # in order to catch any exception before the actual streaming.
                content = BytesIO()
                try:
                    for bytes in responseCnt.source: content.write(bytes)
                except:
                    log.exception('Exception occurred while processing the chain')
                    error = StringIO()
                    traceback.print_exc(file=error)
                else:
                    content.seek(0)
                    responseCnt.source = content

        if error is not None:
            response.code = INTERNAL_ERROR
            response.text = 'Upps, please consult the server logs'
            response.headers = self.errorHeaders
            responseCnt.source = convertToBytes(self.errorResponse(error), 'utf8', 'backslashreplace')

    def errorResponse(self, error):
        '''
        Generates the error response.
        
        @param error: StringIO
            The error stream that contains the stack info.
        '''
        assert isinstance(error, IOutputStream), 'Invalid error stream %s' % error

        yield 'Internal server error occurred, this is a major issue so please contact your administrator\n\n'
        error.seek(0)
        yield error.read()

# --------------------------------------------------------------------
