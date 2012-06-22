'''
Created on Jun 11, 2012

@package: ally core http
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the accept headers handling.
'''

from ally.container.ioc import injected
from ally.core.http.spec.server import IDecoderHeader
from ally.design.processor import HandlerProcessorProceed
from ally.api.type import List, Locale
from ally.design.context import Context, requires, optional, defines

# --------------------------------------------------------------------

LIST_LOCALE = List(Locale)
# The locale list used to set as an additional argument.

# --------------------------------------------------------------------

class Request(Context):
    '''
    The request context.
    '''
    # ---------------------------------------------------------------- Required
    decoderHeader = requires(IDecoderHeader)
    # ---------------------------------------------------------------- Optional
    argumentsOfType = optional(dict)
    # ---------------------------------------------------------------- Defined
    accTypes = defines(list, doc='''
    @rtype: list[string]
    The content types accepted for response.
    ''')
    accCharSets = defines(list, doc='''
    @rtype: list[string]
    The character sets accepted for response.
    ''')
    accLanguages = defines(list, doc='''
    @rtype: list[string]
    The languages accepted for response.
    ''')

# --------------------------------------------------------------------

@injected
class AcceptDecodeHandler(HandlerProcessorProceed):
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
        super().__init__()

    def process(self, request:Request, **keyargs):
        '''
        @see: HandlerProcessorProceed.process
        
        Decode the accepted headers.
        '''
        assert isinstance(request, Request), 'Invalid request %s' % request
        assert isinstance(request.decoderHeader, IDecoderHeader), 'Invalid decoder header %s' % request.decoderHeader

        value = request.decoderHeader.decode(self.nameAccept)
        if value: request.accTypes = list(val for val, _attr in value)

        value = request.decoderHeader.decode(self.nameAcceptCharset)
        if value: request.accCharSets = list(val for val, _attr in value)

        value = request.decoderHeader.decode(self.nameAcceptLanguage)
        if value:
            request.accLanguages = list(val for val, _attr in value)
            if Request.argumentsOfType in request: request.argumentsOfType[LIST_LOCALE] = request.accLanguages
