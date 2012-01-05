'''
Created on Jul 8, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the decoding handler.
'''

from ally.api.operator import INSERT, UPDATE
from ally.container.ioc import injected
from ally.core.spec.codes import UNKNOWN_DECODING
from ally.core.spec.server import Processor, ProcessorsChain, Request, Response, \
    Processors, ContentRequest

# --------------------------------------------------------------------

@injected
class DecodingHandler(Processor):
    '''
    Implementation for a processor that provides the decoding of the request input content based on the requested 
    format to actual arguments that can be used in calling the invoke. The decoding handler relays on a processors
    chain that contains the decoding processors.
    
    Provides on request: content.contentType
    Provides on response: NA
    
    Requires on request: method, [content.contentType], accContentTypes
    Requires on response: [code]
    '''
    
    decodings = Processors
    # The decodings processors, if a processor is successful in the decoding process it has to stop the chain
    # execution.
    
    def __init__(self):
        assert isinstance(self.decodings, Processors), 'Invalid decodings processors %s' % self.decodings
    
    def process(self, req, rsp, chain):
        '''
        @see: Processor.process
        '''
        assert isinstance(req, Request), 'Invalid request %s' % req
        assert isinstance(rsp, Response), 'Invalid response %s' % rsp
        assert isinstance(chain, ProcessorsChain), 'Invalid processors chain %s' % chain
        assert isinstance(req.content, ContentRequest), 'Invalid content on request %s' % req.content
        if req.method in (INSERT, UPDATE):
            if req.content.contentType:
                decodingChain = self.decodings.newChain()
                assert isinstance(decodingChain, ProcessorsChain)
                decodingChain.process(req, rsp)
                if decodingChain.isConsumed():
                    rsp.setCode(UNKNOWN_DECODING,
                                'Content type %r not supported for decoding' % req.content.contentType)
                    return
            else:
                contentTypes = list(req.accContentTypes)
                contentTypes.append(None) # Adding None in case some decoder is configured as default.
                for contentType in contentTypes:
                    req.content.contentType = contentType
                    decodingChain = self.decodings.newChain()
                    assert isinstance(decodingChain, ProcessorsChain)
                    decodingChain.process(req, rsp)
                    if not decodingChain.isConsumed() or rsp.code and not rsp.code.isSuccess:
                        break
                else:
                    rsp.setCode(UNKNOWN_DECODING,
                            'Accepted content types %r not supported for decoding' % ', '.join(req.accContentTypes))
                    return
            if rsp.code and not rsp.code.isSuccess:
                # A failure occurred in decoding, stopping chain execution
                return
        chain.process(req, rsp)
