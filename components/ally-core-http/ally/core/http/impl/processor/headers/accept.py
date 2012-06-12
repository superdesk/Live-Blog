'''
Created on Jun 11, 2012

@package: ally core http
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the accept headers handling.
'''

from ally.container.ioc import injected
from ally.core.http.spec.extension import HTTPDecode
from ally.core.http.spec.server import IDecoderHeader
from ally.core.spec.extension import CharSetsAccepted, TypeAccepted, \
    LanguagesAccepted, ArgumentsAdditional
from ally.design.processor import Handler, mokup, Chain, processor
from ally.api.type import List, Locale

# --------------------------------------------------------------------

LIST_LOCALE = List(Locale)
# The locale list used to set as an additional argument.

@mokup(HTTPDecode)
class _Request(HTTPDecode, TypeAccepted, CharSetsAccepted, LanguagesAccepted, ArgumentsAdditional):
    ''' Used as a mokup class '''

# --------------------------------------------------------------------

@injected
class AcceptHandler(Handler):
    '''
    Implementation for a processor that provides the decoding of accept HTTP request headers.
    '''

    nameAccept = 'Accept'
    # The name for the accept header
    nameAcceptCharset = 'Accept-Charset'
    # The name for the accept character sets header
    nameAcceptLanguage = 'Accept-Language'
    # The name for the accept languages header

    def __init__(self):
        assert isinstance(self.nameAccept, str), 'Invalid accept name %s' % self.nameAccept
        assert isinstance(self.nameAcceptCharset, str), 'Invalid accept charset name %s' % self.nameAcceptCharset
        assert isinstance(self.nameAcceptLanguage, str), 'Invalid accept languages name %s' % self.nameAcceptLanguage

    @processor
    def process(self, chain, request:_Request, **keyargs):
        '''
        Decode the accepted headers.
        '''
        assert isinstance(chain, Chain), 'Invalid processors chain %s' % chain
        assert isinstance(request, _Request), 'Invalid request %s' % request
        assert isinstance(request.decoderHeader, IDecoderHeader), 'Invalid decoder header %s' % request.decoderHeader

        value = request.decoderHeader.decode(self.nameAccept)
        if value: request.accTypes.extend(val for val, _attr in value)

        value = request.decoderHeader.decode(self.nameAcceptCharset)
        if value: request.accCharSets.extend(val for val, _attr in value)

        value = request.decoderHeader.decode(self.nameAcceptLanguage)
        if value:
            request.accLanguages.extend(val for val, _attr in value)
            request.argumentsOfType[LIST_LOCALE] = request.accLanguages

        chain.proceed()
