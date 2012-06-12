'''
Created on Aug 10, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the converters for the response content and request content.
'''

from ally.container.ioc import injected
from ally.core.spec.extension import CharConvert
from ally.core.spec.resources import Converter, Normalizer
from ally.design.processor import Handler, processor, Chain
import logging

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

@injected
class CharConverSetHandler(Handler):
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

    @processor
    def processRequestCnt(self, chain, requestCnt:CharConvert, **keyargs):
        '''
        Provide the character conversion for request content.
        '''
        assert isinstance(chain, Chain), 'Invalid processors chain %s' % chain
        assert isinstance(requestCnt, CharConvert), 'Invalid request content %s' % requestCnt

        requestCnt.normalizer = self.normalizer
        requestCnt.converter = self.converter

        chain.proceed()

    @processor
    def processResponseCnt(self, chain, responseCnt:CharConvert, **keyargs):
        '''
        Provide the character conversion for request content.
        '''
        assert isinstance(chain, Chain), 'Invalid processors chain %s' % chain
        assert isinstance(responseCnt, CharConvert), 'Invalid response content %s' % responseCnt

        responseCnt.normalizer = self.normalizer
        responseCnt.converter = self.converter

        chain.proceed()
