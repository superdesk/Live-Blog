'''
Created on Aug 10, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the converters for the response content and request content.
'''

from ally.core.spec.context import TransformModel
from ally.core.spec.resources import Converter, Normalizer
from ally.core.spec.server import IProcessor, ProcessorsChain, Request
import logging

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

class TransformModelHandler(IProcessor):
    '''
    Provides the standard transform services for the model decoding, this will be populated on the response and request
    content.
    
    Provides on request: NA
    Provides on response: normalizer, converterId, converter
    
    Requires on request: content.normalizer, content.converterId, content.converter
    Requires on response: NA
    '''

    def __init__(self):
        self._normalizer = Normalizer()
        self._converter = Converter()

    def process(self, req, rsp, chain):
        '''
        @see: IProcessor.process
        '''
        assert isinstance(chain, ProcessorsChain), 'Invalid processors chain %s' % chain
        assert isinstance(req, Request), 'Invalid request %s' % req

        TransformModel(self._converter, self._normalizer, self._converter, self=rsp)
        TransformModel(self._converter, self._normalizer, self._converter, self=req.content)

        chain.proceed()
