'''
Created on Jul 4, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides hints in the encoded paths.
'''

from ally.container.ioc import injected
from ally.core.spec.resources import Path, Node, Invoker
from ally.core.spec.server import Processor, ProcessorsChain, Response, \
    EncoderParams, EncoderPath
import logging

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

#Deprecated: Instead of the Hinter a extension to the URL like /parameters should present the options.
@injected
class HintingHandler(Processor):
    '''
    @deprecated: Instead of the Hinter a extension to the URL like /parameters should present the options.
    
    This is actually an optional processor that just appends when a path is rendered all the parameters that are
    known for that path. Basically provides some hinting on what query parameters are available for the resource. 
    '''
    
    encoders = list
    # The parameters encoders used for adding parameters to the path.
   
    def __init__(self):
        assert isinstance(self.encoders, list), 'Invalid encoders list %s' % self.encoders
        if __debug__:
            for encoder in self.encoders:
                assert isinstance(encoder, EncoderParams), 'Invalid parameters encoder %s' % encoder
    
    def process(self, req, rsp, chain):
        '''
        @see: Processor.process
        '''
        assert isinstance(chain, ProcessorsChain), 'Invalid processors chain %s' % chain
        assert isinstance(rsp, Response), 'Invalid response %s' % rsp
        rsp.encoderPath = EncoderPathHinter(rsp.encoderPath, self)
        chain.process(req, rsp)

# --------------------------------------------------------------------

class EncoderPathHinter(EncoderPath):
    '''
    Provides hints in the URLs by showing all possible query parameters for a path.
    '''
    
    def __init__(self, wrapped, hintingHandler):
        '''
        @param wrapped: EncoderPath
            The encoder path to wrap for rendering paths.
        '''
        assert isinstance(wrapped, EncoderPath), 'Invalid encoder path to wrap %s' % wrapped
        assert isinstance(hintingHandler, HintingHandler), 'Invalid hinting handler %s' % hintingHandler
        self._wrapped = wrapped
        self._hintingHandler = hintingHandler
        
    def encode(self, path, parameters=None):
        '''
        @see: EncoderPath.encode
        '''
        assert isinstance(path, Path), 'Invalid path %s' % path
        if parameters is None:
            node = path.node
            assert isinstance(node, Node), \
            'The node has to be available in the path %s problems in previous processors' % path
            if node.get is not None:
                assert isinstance(node.get, Invoker)
                # We only consider as parameters the not mandatory primitive inputs.
                inputs = [node.get.inputs[k] for k in range(node.get.mandatoryCount, len(node.get.inputs))]
                models = {}
                for inp in inputs:
                    for encoder in self._hintingHandler.encoders:
                        assert isinstance(encoder, EncoderParams)
                        encoder.encodeModels(inputs, inp, models)
                parameters = []
                for name, model in models.items():
                    isList = model[0]
                    value = model[2]
                    if value is None:
                        parameters.append((name, ''))
                    elif isList:
                        parameters.append((name, value[0]))
                    else:
                        parameters.append((name, value))
        return self._wrapped.encode(path, parameters)
