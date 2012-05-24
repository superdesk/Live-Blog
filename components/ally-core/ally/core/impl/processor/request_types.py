'''
Created on Aug 8, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the special types like @see: TypeLocale based from the request/response.
'''

from ally.api.type import Input, List, TypeLocale, TypeScheme
from ally.container.ioc import injected
from ally.core.spec.resources import Invoker
from ally.core.spec.server import IProcessor, ProcessorsChain, Request, Response

# --------------------------------------------------------------------

@injected
class RequestTypesHandler(IProcessor):
    '''
    Implementation for a processor that provides the special request type arguments like @see: TypeLocale.
    
    Provides on request: arguments
    Provides on response: NA
    
    Requires on request: invoker, accLanguages
    Requires on response: contentLanguage
    '''

    def process(self, req, rsp, chain):
        '''
        @see: IProcessor.process
        '''
        assert isinstance(chain, ProcessorsChain), 'Invalid processors chain %s' % chain
        assert isinstance(req, Request), 'Invalid request %s' % req
        assert isinstance(rsp, Response), 'Invalid response %s' % rsp
        assert isinstance(req.invoker, Invoker)
        for inp in req.invoker.inputs:
            assert isinstance(inp, Input)
            if isinstance(inp.type, TypeLocale):
                assert isinstance(rsp.contentLanguage, str), 'There is no content language on the response'
                req.arguments[inp.name] = rsp.contentLanguage
            elif isinstance(inp.type, TypeScheme):
                assert isinstance(rsp.scheme, str), 'There is no scheme on the response'
                req.arguments[inp.name] = rsp.scheme
            elif isinstance(inp.type, List):
                if isinstance(inp.type.itemType, TypeLocale):
                    if req.accLanguages: req.arguments[inp.name] = list(req.accLanguages)
                    else: req.arguments[inp.name] = [rsp.contentLanguage]
        chain.proceed()
