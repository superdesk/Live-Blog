'''
Created on Jun 12, 2012

@package: ally core http
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the content language header decoding.
'''

from ally.container.ioc import injected
from ally.core.http.spec.extension import HTTPDecode
from ally.core.http.spec.server import IDecoderHeader
from ally.core.spec.extension import Language, ArgumentsAdditional
from ally.design.processor import Handler, processor, Chain, ext
from ally.api.type import Locale

# --------------------------------------------------------------------

@injected
class ContentLanguageDecodeHandler(Handler):
    '''
    Implementation for a processor that provides the decoding of content language HTTP request header.
    '''

    nameContentLanguage = 'Content-Language'
    # The header name for the content language.

    def __init__(self):
        assert isinstance(self.nameContentLanguage, str), 'Invalid content language name %s' % self.nameContentLanguage

    @processor
    def process(self, chain, request:(HTTPDecode, ext(ArgumentsAdditional)), requestCnt:ext(Language), **keyargs):
        '''
        Provides the content language decode for the request.
        '''
        assert isinstance(chain, Chain), 'Invalid processors chain %s' % chain
        assert isinstance(request, HTTPDecode), 'Invalid request %s' % request
        assert isinstance(request, ArgumentsAdditional), 'Invalid request %s' % request
        assert isinstance(requestCnt, Language), 'Invalid request content %s' % requestCnt
        assert isinstance(request.decoderHeader, IDecoderHeader), 'Invalid header decoder %s' % request.decoderHeader

        value = request.decoderHeader.retrieve(self.nameContentLanguage)
        if value: request.argumentsOfType[Locale] = requestCnt.language = value

        chain.proceed()
