'''
Created on Jun 28, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mihai Balaceanu

Provides support for explaining the errors in the content of the request.
'''

from ally.container.ioc import injected
from ally.core.spec.codes import Code
from ally.core.spec.encdec.render import Object, Value, renderObject
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
    # ---------------------------------------------------------------- Defined
    source = defines(Iterable)
    # ---------------------------------------------------------------- Optional
    code = optional(Code)
    text = optional(str)
    errorMessage = optional(str)
    errorDetails = optional(Object)
    # ---------------------------------------------------------------- Required
    renderFactory = requires(Callable)

# --------------------------------------------------------------------

@injected
class ExplainErrorHandler(HandlerProcessorProceed):
    '''
    Implementation for a processor that provides on the response a form of the error that can be extracted from 
    the response code and error message, this processor uses the code status (success) in order to trigger the error
    response.
    '''

    def process(self, response:Response, **keyargs):
        '''
        @see: HandlerProcessorProceed.process
        
        Process the error into a response content.
        '''
        assert isinstance(response, Response), 'Invalid response %s' % response

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

            response.source = (output.getvalue(),)
