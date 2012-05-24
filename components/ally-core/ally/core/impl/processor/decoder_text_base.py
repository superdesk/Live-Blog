'''
Created on Aug 11, 2011

@package: ally core
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the basic decoding processor handler.
'''

from ally.api.operator.type import TypeModel
from ally.api.type import Input
from ally.container.ioc import injected
from ally.core.spec.resources import Normalizer, Converter, Invoker
from ally.core.spec.server import IProcessor
import logging

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

@injected
class DecodingTextBaseHandler(IProcessor):
    '''
    Provides the base decoder for request content that contain model data.
    '''

    normalizer = Normalizer
    # The normalizer used by the encoding for the XML tag names.
    converterId = Converter
    # The converter to use on the id's of the models.
    contentTypes = list
    # The list[string] of content types known by this decoding.

    def __init__(self):
        assert isinstance(self.normalizer, Normalizer), 'Invalid Normalizer object %s' % self.normalizer
        assert isinstance(self.converterId, Converter), 'Invalid Converter object %s' % self.converterId
        assert isinstance(self.contentTypes, list), 'Invalid content types list %s' % self.contentTypes

# --------------------------------------------------------------------

def findLastModel(invoker):
    '''
    Provides if is the case the Model represented by the invoker as the last mandatory input.
    
    @param invoker: Invoker
        The invoker to find the model for.
    @return: tuple(string, TypeModel)
        A tuple containing the name of the input and the type model, None if there is no such input.
    '''
    assert isinstance(invoker, Invoker), 'Invalid invoker %s' % invoker
    if invoker.inputs:
        # We search the right most type model from the input, the rest of type models are ignored.
        for k in range(invoker.mandatory - 1, -1, -1):
            inp = invoker.inputs[k]
            assert isinstance(inp, Input)
            if isinstance(inp.type, TypeModel):
                return inp.name, inp.type
    return None

