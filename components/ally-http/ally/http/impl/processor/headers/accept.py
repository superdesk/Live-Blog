'''
Created on Jun 11, 2012

@package: ally core http
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the accept headers handling.
'''

from ally.container.ioc import injected
from ally.design.processor.attribute import requires, defines
from ally.design.processor.context import Context
from ally.design.processor.handler import HandlerProcessorProceed
from ally.http.spec.server import IDecoderHeader, IEncoderHeader

# --------------------------------------------------------------------

class AcceptConfigurations:
    '''
    Configurations for accept HTTP request headers.
    '''

    nameAccept = 'Accept'
    # The name for the accept header
    nameAcceptCharset = 'Accept-Charset'
    # The name for the accept character sets header

    def __init__(self):
        assert isinstance(self.nameAccept, str), 'Invalid accept name %s' % self.nameAccept
        assert isinstance(self.nameAcceptCharset, str), 'Invalid accept charset name %s' % self.nameAcceptCharset
    
# --------------------------------------------------------------------

class RequestDecode(Context):
    '''
    The request decode context.
    '''
    # ---------------------------------------------------------------- Required
    decoderHeader = requires(IDecoderHeader)
    # ---------------------------------------------------------------- Defined
    accTypes = defines(list, doc='''
    @rtype: list[string]
    The content types accepted for response.
    ''')
    accCharSets = defines(list, doc='''
    @rtype: list[string]
    The character sets accepted for response.
    ''')

# --------------------------------------------------------------------

@injected
class AcceptRequestDecodeHandler(HandlerProcessorProceed, AcceptConfigurations):
    '''
    Implementation for a processor that provides the decoding of accept HTTP request headers.
    '''

    def __init__(self):
        HandlerProcessorProceed.__init__(self)
        AcceptConfigurations.__init__(self)

    def process(self, request:RequestDecode, **keyargs):
        '''
        @see: HandlerProcessorProceed.process
        
        Decode the accepted headers.
        '''
        assert isinstance(request, RequestDecode), 'Invalid request %s' % request
        assert isinstance(request.decoderHeader, IDecoderHeader), 'Invalid decoder header %s' % request.decoderHeader

        value = request.decoderHeader.decode(self.nameAccept)
        if value: request.accTypes = list(val for val, _attr in value)

        value = request.decoderHeader.decode(self.nameAcceptCharset)
        if value: request.accCharSets = list(val for val, _attr in value)

# --------------------------------------------------------------------

class RequestEncode(Context):
    '''
    The request context.
    '''
    # ---------------------------------------------------------------- Required
    encoderHeader = requires(IEncoderHeader)
    accTypes = requires(list, doc='''
    @rtype: list[string]
    The content types accepted for response.
    ''')
    accCharSets = requires(list, doc='''
    @rtype: list[string]
    The character sets accepted for response.
    ''')

# --------------------------------------------------------------------

@injected
class AcceptRequestEncodeHandler(HandlerProcessorProceed, AcceptConfigurations):
    '''
    Implementation for a processor that provides the encoding of accept HTTP request headers.
    '''

    def __init__(self):
        HandlerProcessorProceed.__init__(self)
        AcceptConfigurations.__init__(self)

    def process(self, request:RequestEncode, **keyargs):
        '''
        @see: HandlerProcessorProceed.process
        
        Encode the accepted headers.
        '''
        assert isinstance(request, RequestEncode), 'Invalid request %s' % request
        assert isinstance(request.encoderHeader, IEncoderHeader), 'Invalid encoder header %s' % request.encoderHeader

        if RequestEncode.accTypes: request.encoderHeader.encode(self.nameAccept, *request.accTypes)
        
        if RequestEncode.accCharSets: request.encoderHeader.encode(self.nameAcceptCharset, *request.accCharSets)
