'''
Created on Jun 22, 2012

@package: ally http
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provide the internal error representation. This is usually when the server fails badly.
'''

from ally.container.ioc import injected
from ally.design.processor.attribute import defines
from ally.design.processor.context import Context
from ally.design.processor.execution import Chain
from ally.design.processor.handler import Handler
from ally.design.processor.processor import Processor
from ally.http.spec.codes import INTERNAL_ERROR
from ally.support.util_io import convertToBytes, IInputStream
from collections import Iterable
from functools import partial
from io import StringIO, BytesIO
import logging
import traceback

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

class Response(Context):
    '''
    The response context.
    '''
    # ---------------------------------------------------------------- Defined
    code = defines(str)
    status = defines(int)
    isSuccess = defines(bool)
    headers = defines(dict)

class ResponseContent(Context):
    '''
    The response content context.
    '''
    # ---------------------------------------------------------------- Optional
    source = defines(IInputStream, Iterable)

# --------------------------------------------------------------------

@injected
class InternalErrorHandler(Handler):
    '''
    Implementation for a processor that provides the handling of internal errors.
    '''

    errorHeaders = {'Content-Type':'text'}
    # The headers that will be placed on the response.

    def __init__(self, response=Response, responseCnt=ResponseContent, **contexts):
        '''
        Construct the internal error handler.
        '''
        assert isinstance(self.errorHeaders, dict), 'Invalid error headers %s' % self.errorHeaders
        super().__init__(Processor(dict(response=Response, responseCnt=ResponseContent, **contexts), self.process))

    def process(self, chain, **keyargs):
        '''
        Provides the additional arguments by type to be populated.
        '''
        assert isinstance(chain, Chain), 'Invalid processors chain %s' % chain
        chain.callBackError(partial(self.handleError, chain))
        if __debug__:
            # If in debug mode and the response content has a source generator then we will try to read that
            # in order to catch any exception before the actual streaming.
            def onFinalize():
                '''
                Handle the finalization
                '''
                try: response, responseCnt = chain.arg.response, chain.arg.responseCnt
                except AttributeError: return  # If there is no response or response content we take no action
                assert isinstance(response, Response), 'Invalid response %s' % response
                assert isinstance(responseCnt, ResponseContent), 'Invalid response content %s' % responseCnt
                if isinstance(responseCnt.source, Iterable):
                    content = BytesIO()
                    try:
                        for bytes in responseCnt.source: content.write(bytes)
                    except:
                        log.exception('Exception occurred while processing the chain')
                        error = StringIO()
                        traceback.print_exc(file=error)
                        response.code, response.status, response.isSuccess = INTERNAL_ERROR
                        response.headers = self.errorHeaders
                        responseCnt.source = convertToBytes(self.errorResponse(error), 'utf8', 'backslashreplace')
                    else:
                        content.seek(0)
                        responseCnt.source = content
            
            chain.callBack(onFinalize)
            
    def handleError(self, chain):
        '''
        Handle the error.
        '''
        assert isinstance(chain, Chain), 'Invalid processors chain %s' % chain
        try: response = chain.arg.response
        except AttributeError: response = Response()
        
        try: responseCnt = chain.arg.responseCnt
        except AttributeError: responseCnt = ResponseContent()
        
        assert isinstance(response, Response), 'Invalid response %s' % response
        assert isinstance(responseCnt, ResponseContent), 'Invalid response content %s' % responseCnt
        
        # If there is an explanation for the error occurred, we do not need to make another one
        if responseCnt.source is not None: return
        
        log.exception('Exception occurred while processing the chain')
        error = StringIO()
        traceback.print_exc(file=error)
        response.code, response.status, response.isSuccess = INTERNAL_ERROR
        response.headers = self.errorHeaders
        responseCnt.source = convertToBytes(self.errorResponse(error), 'utf-8', 'backslashreplace')

    def errorResponse(self, error):
        '''
        Generates the error response.
        
        @param error: StringIO
            The error stream that contains the stack info.
        '''
        assert isinstance(error, IInputStream), 'Invalid error stream %s' % error

        yield 'Internal server error occurred, this is a major issue so please contact your administrator\n\n'
        error.seek(0)
        yield error.read()
        
