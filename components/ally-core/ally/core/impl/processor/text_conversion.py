'''
Created on Aug 10, 2011

@package: ally core
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the converters for the response content and request content.
'''

from ally.container.ioc import injected
from ally.core.spec.resources import Converter, Normalizer
from ally.design.processor.attribute import defines
from ally.design.processor.context import Context
from ally.design.processor.handler import HandlerProcessorProceed
import logging

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

class Content(Context):
    '''
    The content context.
    '''
    # ---------------------------------------------------------------- Defined
    normalizer = defines(Normalizer, doc='''
    @rtype: Normalizer
    The normalizer to use for decoding request content.
    ''')
    converter = defines(Converter, doc='''
    @rtype: Converter
    The converter to use for decoding request content.
    ''')

# --------------------------------------------------------------------

@injected
class ConversionSetHandler(HandlerProcessorProceed):
    '''
    Provides the standard transform services for the model decoding, this will be populated on the response and request
    content.
    '''
    normalizer = Normalizer
    # The normalizer to set on the content request and content response.
    converter = Converter
    # The converter to set on the content request and content response.

    def __init__(self):
        assert isinstance(self.normalizer, Normalizer), 'Invalid normalizer %s' % self.normalizer
        assert isinstance(self.converter, Converter), 'Invalid converter %s' % self.converter
        super().__init__()

    def process(self, requestCnt:Content, response:Content, **keyargs):
        '''
        @see: HandlerProcessorProceed.process
        
        Provide the character conversion for request and response content.
        '''
        assert isinstance(requestCnt, Content), 'Invalid request content %s' % requestCnt
        assert isinstance(response, Content), 'Invalid response content %s' % response

        requestCnt.normalizer = response.normalizer = self.normalizer
        requestCnt.converter = response.converter = self.converter
