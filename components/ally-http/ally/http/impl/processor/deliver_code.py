'''
Created on Feb 4, 2013

@package: ally http
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Populates a provided code for the response.
'''

from ally.container.ioc import injected
from ally.design.processor.attribute import defines
from ally.design.processor.context import Context
from ally.design.processor.handler import HandlerProcessorProceed

# --------------------------------------------------------------------

class Response(Context):
    '''
    The response context.
    '''
    # ---------------------------------------------------------------- Defined
    code = defines(str)
    status = defines(int)
    isSuccess = defines(bool)

# --------------------------------------------------------------------

@injected
class DeliverCodeHandler(HandlerProcessorProceed):
    '''
    Handler that just populates a code on the response and then proceeds.
    '''

    code = str
    # The code to deliver
    status = int
    # The status code to deliver
    isSuccess = bool
    # The code success flag

    def __init__(self):
        assert isinstance(self.code, str), 'Invalid code %s' % self.code
        assert isinstance(self.status, int), 'Invalid status %s' % self.status
        assert isinstance(self.isSuccess, bool), 'Invalid success flag %s' % self.isSuccess
        super().__init__()

    def process(self, response:Response, **keyargs):
        '''
        @see: HandlerProcessorProceed.process
        
        Delivers the code.
        '''
        assert isinstance(response, Response), 'Invalid response %s' % response

        response.code, response.status, response.isSuccess = self.code, self.status, self.isSuccess
