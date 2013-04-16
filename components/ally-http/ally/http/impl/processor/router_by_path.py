'''
Created on Jan 30, 2013

@package: ally http
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides a processor that routes the requests based on patterns.
'''

from ally.container.ioc import injected
from ally.design.processor.assembly import Assembly
from ally.design.processor.attribute import requires
from ally.design.processor.context import Context, copy
from ally.design.processor.execution import Chain, Processing
from ally.design.processor.handler import HandlerBranching
from ally.design.processor.processor import Routing
import logging
import re

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

class Request(Context):
    '''
    Context for request. 
    '''
    # ---------------------------------------------------------------- Required
    uri = requires(str)

# --------------------------------------------------------------------

@injected
class RoutingByPathHandler(HandlerBranching):
    '''
    Implementation for a handler that provides the routing of requests based on regex patterns. The regex needs to provide
    capturing groups that joined will become the routed uri. 
    '''
    
    pattern = str
    # The string pattern for matching the path, the pattern needs to provide capturing groups that joined will become
    # the routed uri.
    assembly = Assembly
    # The assembly to be used in processing the request for the provided pattern.
    useSameContexts = True
    # Flag indicating that the routing should use the same requests context as provided.
    
    def __init__(self):
        assert isinstance(self.pattern, str), 'Invalid pattern %s' % self.pattern
        assert isinstance(self.assembly, Assembly), 'Invalid assembly %s' % self.assembly
        assert isinstance(self.useSameContexts, bool), 'Invalid use same contexts flag %s' % self.useSameContexts
        super().__init__(Routing(self.assembly, self.useSameContexts))
        
        self._regex = re.compile(self.pattern)
            
    def process(self, chain, processing, request:Request, requestCnt, response, responseCnt):
        '''
        @see: HandlerBranching.process
        
        Process the routing.
        '''
        assert isinstance(chain, Chain), 'Invalid chain %s' % chain
        assert isinstance(processing, Processing), 'Invalid processing %s' % processing
        assert isinstance(request, Request), 'Invalid request %s' % request
        
        match = self._regex.match(request.uri)
        if match:
            if not self.useSameContexts:
                req, reqCnt = processing.ctx.request(), processing.ctx.requestCnt()
                copy(request, req)
                copy(requestCnt, reqCnt)
                request, requestCnt = req, reqCnt
                response, responseCnt = processing.ctx.response(), processing.ctx.responseCnt()
                
            request.uri = ''.join(match.groups())
            chain.update(request=request, requestCnt=requestCnt, response=response, responseCnt=responseCnt)
            chain.branch(processing)
        else:
            chain.proceed()
