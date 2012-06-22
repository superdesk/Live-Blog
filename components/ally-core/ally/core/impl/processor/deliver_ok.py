'''
Created on Nov 23, 2011

@package: ally core
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides a processor that just sends an ok status as a response without any body. This is useful for the OPTIONS
method for instance where we just want to deliver some response headers. 
'''

from ally.container.ioc import injected
from ally.core.spec.codes import RESOURCE_FOUND, Code
from ally.design.processor import HandlerProcessor, Chain
from ally.design.context import Context, requires, defines

# --------------------------------------------------------------------

class Request(Context):
    '''
    The request context.
    '''
    # ---------------------------------------------------------------- Required
    method = requires(int)

class Response(Context):
    '''
    The response context.
    '''
    # ---------------------------------------------------------------- Defined
    code = defines(Code)
    text = defines(str)

# --------------------------------------------------------------------

@injected
class DeliverOkHandler(HandlerProcessor):
    '''
    Handler that just sends an ok status.
    '''

    forMethod = int
    # The method to respond with Ok for.

    def __init__(self):
        assert isinstance(self.forMethod, int), 'Invalid for method %s' % self.forMethod
        super().__init__()

    def process(self, chain, request:Request, response:Response, **keyargs):
        '''
        @see: HandlerProcessor.process
        
        Delivers Ok if the request methos is the expected one.
        '''
        assert isinstance(chain, Chain), 'Invalid processors chain %s' % chain
        assert isinstance(request, Request), 'Invalid request %s' % request
        assert isinstance(response, Response), 'Invalid response %s' % response

        if request.method == self.forMethod:
            response.code, response.text = RESOURCE_FOUND, 'Ok'
            return

        chain.proceed()
