'''
Created on Jul 3, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the parameters handler.
'''

from ally.container.ioc import injected
from ally.core.spec.codes import ILLEGAL_PARAM, UNKNOWN_PARAMS
from ally.core.spec.resources import Invoker
from ally.core.spec.server import Processor, ProcessorsChain, Response, Request, \
    DecoderParams
from ally.exception import DevelError

# --------------------------------------------------------------------

@injected
class ParametersHandler(Processor):
    '''
    Implementation for a processor that provides the transformation of parameters into arguments, the parameters will
    be parsed only for the GET method, for other methods will stop the chain execution and send a failed code.
    
    Provides on request: arguments
    Provides on response: NA
    
    Requires on request: method, invoker, params
    Requires on response: NA
    '''

    decoders = list
    # The parameters decoders used for obtaining the arguments.

    def __init__(self):
        assert isinstance(self.decoders, list), 'Invalid decoders list %s' % self.decoders
        if __debug__:
            for decoder in self.decoders:
                assert isinstance(decoder, DecoderParams), 'Invalid parameters decoder %s' % decoder

    def process(self, req, rsp, chain):
        '''
        @see: Processor.process
        '''
        assert isinstance(chain, ProcessorsChain), 'Invalid processors chain %s' % chain
        assert isinstance(req, Request), 'Invalid request %s' % req
        assert isinstance(rsp, Response), 'Invalid response %s' % rsp
        if req.params:
            assert isinstance(req.invoker, Invoker)
            # We only consider as parameters the not mandatory primitive inputs.
            params = list(req.params)
            inputs = [req.invoker.inputs[k] for k in range(req.invoker.mandatory, len(req.invoker.inputs))]
            for inp in inputs:
                for decoder in self.decoders:
                    assert isinstance(decoder, DecoderParams)
                    try:
                        decoder.decode(inputs, inp, params, req.arguments)
                    except DevelError as e:
                        rsp.setCode(ILLEGAL_PARAM, e.message)
                        return
            if params:
                rsp.setCode(UNKNOWN_PARAMS, 'Unknown parameters or values %r' % ', '.join(
                                                                ['%s=%s' % (param[0], param[1]) for param in params]))
                return
        chain.proceed()
