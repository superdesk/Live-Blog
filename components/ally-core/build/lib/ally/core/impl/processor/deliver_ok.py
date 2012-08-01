'''
Created on Nov 23, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides a processor that just sends an ok status as a response without any body. This is useful for the OPTIONS
method for instance where we just want to deliver some response headers. 
'''

from ally.container.ioc import injected
from ally.core.spec.codes import RESOURCE_FOUND
from ally.core.spec.server import Processor, Request, Response, ProcessorsChain

# --------------------------------------------------------------------

@injected
class DeliverOkHandler(Processor):
    '''
    Handler that just sends an ok status.
    
    Provides on request: NA
    Provides on response: NA
    
    Requires on request: headers
    Requires on response: NA
    '''
    
    forMethod = int
    
    def __init__(self):
        assert isinstance(self.forMethod, int), 'Invalid for method %s' % self.forMethod
    
    def process(self, req, rsp, chain):
        '''
        @see: Processor.process
        '''
        assert isinstance(req, Request), 'Invalid request %s' % req
        assert isinstance(rsp, Response), 'Invalid response %s' % rsp
        assert isinstance(chain, ProcessorsChain), 'Invalid processors chain %s' % chain
        if req.method == self.forMethod:
            rsp.setCode(RESOURCE_FOUND, 'Ok')
        else:
            chain.proceed()
