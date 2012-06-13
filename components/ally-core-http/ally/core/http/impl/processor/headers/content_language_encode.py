'''
Created on Jun 12, 2012

@package: ally core http
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the encoding for the content language header.
'''

from ally.container.ioc import injected
from ally.core.http.spec.extension import HTTPEncode
from ally.core.http.spec.server import IEncoderHeader
from ally.core.spec.extension import Language
from ally.design.processor import Handler, Chain, processor

# --------------------------------------------------------------------

@injected
class ContentLanguageEncodeHandler(Handler):
    '''
    Implementation for a processor that provides the encoding of content language HTTP response header.
    '''

    nameContentLanguage = 'Content-Language'
    # The header name for the content language.

    def __init__(self):
        assert isinstance(self.nameContentLanguage, str), 'Invalid content language name %s' % self.nameContentLanguage

    @processor
    def process(self, chain, response:HTTPEncode, responseCnt:Language, **keyargs):
        '''
        Encodes the content language.
        '''
        assert isinstance(chain, Chain), 'Invalid processors chain %s' % chain
        assert isinstance(response, HTTPEncode), 'Invalid response %s' % response
        assert isinstance(responseCnt, Language), 'Invalid response content %s' % responseCnt
        assert isinstance(response.encoderHeader, IEncoderHeader), \
        'Invalid response header encoder %s' % response.encoderHeader

        if responseCnt.language is not None:
            response.encoderHeader.encode(self.nameContentLanguage, responseCnt.language)

        chain.proceed()
