'''
Created on Jun 11, 2012

@package: ally core http
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the accept headers handling.
'''

from ally.api.type import List, Locale
from ally.container.ioc import injected
from ally.design.processor.attribute import optional, defines
from ally.http.impl.processor.headers.accept import RequestDecode, \
    AcceptRequestDecodeHandler

# --------------------------------------------------------------------

LIST_LOCALE = List(Locale)
# The locale list used to set as an additional argument.

# --------------------------------------------------------------------

class Request(RequestDecode):
    '''
    The request context.
    '''
    # ---------------------------------------------------------------- Optional
    argumentsOfType = optional(dict)
    # ---------------------------------------------------------------- Defined
    accLanguages = defines(list, doc='''
    @rtype: list[string]
    The languages accepted for response.
    ''')

# --------------------------------------------------------------------

@injected
class AcceptDecodeHandler(AcceptRequestDecodeHandler):
    '''
    Implementation for a processor that provides the decoding of accept HTTP request headers.
    '''
    
    nameAcceptLanguage = 'Accept-Language'
    # The name for the accept languages header

    def __init__(self):
        assert isinstance(self.nameAcceptLanguage, str), 'Invalid accept languages name %s' % self.nameAcceptLanguage
        super().__init__()

    def process(self, request:Request, **keyargs):
        '''
        @see: HandlerProcessorProceed.process
        
        Decode the accepted headers.
        '''
        super().process(request)
        value = request.decoderHeader.decode(self.nameAcceptLanguage)
        if value:
            request.accLanguages = list(val for val, _attr in value)
            if Request.argumentsOfType in request and request.argumentsOfType is not None:
                request.argumentsOfType[LIST_LOCALE] = request.accLanguages
