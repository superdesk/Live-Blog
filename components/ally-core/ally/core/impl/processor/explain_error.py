'''
Created on Jun 28, 2011

@package: ally core
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mihai Balaceanu

Provides support for explaining the errors in the content of the request.
'''

from ally.container.ioc import injected
from ally.core.spec.codes import Code
from ally.core.spec.transform.render import Object, Value, renderObject
from ally.design.context import Context, requires, defines, optional
from ally.design.processor import HandlerProcessorProceed
from collections import Iterable, Callable
from io import BytesIO
import logging

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

class Response(Context):
    '''
    The response context.
    '''
    # ---------------------------------------------------------------- Optional
    code = optional(Code)
    text = optional(str)
    errorMessage = optional(str, doc='''
    @rtype: object
    The error message for the code.
    ''')
    errorDetails = optional(Object, doc='''
    @rtype: Object
    The error text object describing a detailed situation for the error.
    ''')
    # ---------------------------------------------------------------- Required
    renderFactory = requires(Callable)

class ResponseContent(Context):
    '''
    The response content context.
    '''
    # ---------------------------------------------------------------- Defined
    source = defines(Iterable)
    length = defines(int)

# --------------------------------------------------------------------

@injected
class ExplainErrorHandler(HandlerProcessorProceed):
    '''
    Implementation for a processor that provides on the response a form of the error that can be extracted from 
    the response code and error message, this processor uses the code status (success) in order to trigger the error
    response.
    '''

    def process(self, response:Response, responseCnt:ResponseContent, **keyargs):
        '''
        @see: HandlerProcessorProceed.process
        
        Process the error into a response content.
        '''
        assert isinstance(response, Response), 'Invalid response %s' % response
        assert isinstance(responseCnt, ResponseContent), 'Invalid response content %s' % responseCnt

        if Response.code in response and not response.code.isSuccess and Response.renderFactory in response:
            errors = [Value('code', str(response.code.code))]
            if Response.errorMessage in response:
                errors.append(Value('message', response.errorMessage))
            elif Response.text in response:
                errors.append(Value('message', response.text))

            if Response.errorDetails in response:
                errors.append(Object('details', response.errorDetails))

            output = BytesIO()
            render = response.renderFactory(output)
            renderObject(Object('error', *errors), render)

            content = output.getvalue()
            responseCnt.length = len(content)
            responseCnt.source = (output.getvalue(),)
