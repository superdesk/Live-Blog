'''
Created on Aug 8, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the special types like @see: TypeLocale based from the request/response.
'''

from ally.api.type import Input, Locale, List
from ally.container.ioc import injected
from ally.core.spec.resources import Invoker
from ally.core.spec.server import Processor, ProcessorsChain, Request, Response

# --------------------------------------------------------------------

@injected
class RequestTypesHandler(Processor):
    '''
    Implementation for a processor that provides the special request type arguments like @see: TypeLocale.
    
    Provides on request: arguments
    Provides on response: NA
    
    Requires on request: invoker, accLanguages
    Requires on response: contentLanguage
    '''
    
    def process(self, req, rsp, chain):
        '''
        @see: Processor.process
        '''
        assert isinstance(chain, ProcessorsChain), 'Invalid processors chain %s' % chain
        assert isinstance(req, Request), 'Invalid request %s' % req
        assert isinstance(rsp, Response), 'Invalid response %s' % rsp
        assert isinstance(req.invoker, Invoker)
        for inp in req.invoker.inputs:
            assert isinstance(inp, Input)
            if inp.type.isOf(Locale):
                if isinstance(inp.type, List):
                    req.arguments[inp.name] = list(req.accLanguages)
                else:
                    req.arguments[inp.name] = rsp.contentLanguage
        chain.proceed()
