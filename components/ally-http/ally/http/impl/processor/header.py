'''
Created on Jul 9, 2011

@package: ally http
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the standard headers handling.
'''

from ally.container.ioc import injected
from ally.design.processor.attribute import requires, optional, defines
from ally.design.processor.context import Context
from ally.design.processor.handler import HandlerProcessorProceed
from ally.http.spec.server import IDecoderHeader, IEncoderHeader
from collections import deque, Iterable
import re

# --------------------------------------------------------------------

class HeaderConfigurations:
    '''
    Provides the configurations for handling HTTP headers.
    '''

    separatorMain = ','
    # The separator used in splitting value and attributes from each other. 
    separatorAttr = ';'
    # The separator used between the attributes and value.
    separatorValue = '='
    # The separator used between attribute name and attribute value.

    def __init__(self):
        assert isinstance(self.separatorMain, str), 'Invalid main separator %s' % self.separatorMain
        assert isinstance(self.separatorAttr, str), 'Invalid attribute separator %s' % self.separatorAttr
        assert isinstance(self.separatorValue, str), 'Invalid value separator %s' % self.separatorValue

        self.reSeparatorMain = re.compile(self.separatorMain)
        self.reSeparatorAttr = re.compile(self.separatorAttr)
        self.reSeparatorValue = re.compile(self.separatorValue)

# --------------------------------------------------------------------

class RequestDecode(Context):
    '''
    The request context.
    '''
    # ---------------------------------------------------------------- Required
    headers = requires(dict)
    # ---------------------------------------------------------------- Optional
    parameters = optional(list)
    # ---------------------------------------------------------------- Defined
    decoderHeader = defines(IDecoderHeader, doc='''
    @rtype: IDecoderHeader
    The decoder used for reading the request headers.
    ''')

# --------------------------------------------------------------------

@injected
class HeaderDecodeRequestHandler(HandlerProcessorProceed, HeaderConfigurations):
    '''
    Provides the request decoder for handling HTTP headers.
    '''
    useParameters = False
    # If true then if the data is present in the parameters will override the header.

    def __init__(self):
        assert isinstance(self.useParameters, bool), 'Invalid use parameters flag %s' % self.useParameters
        HeaderConfigurations.__init__(self)
        HandlerProcessorProceed.__init__(self)

    def process(self, request:RequestDecode, **keyargs):
        '''
        @see: HandlerProcessorProceed.process
        
        Provide the request headers decoders.
        '''
        assert isinstance(request, RequestDecode), 'Invalid request %s' % request

        if not request.decoderHeader:  # Only add the decoder if one is not present
            if self.useParameters and RequestDecode.parameters in request and request.parameters:
                request.decoderHeader = DecoderHeader(self, request.headers, request.parameters)
            else: request.decoderHeader = DecoderHeader(self, request.headers)

# --------------------------------------------------------------------

class ResponseDecode(Context):
    '''
    The response context.
    '''
    # ---------------------------------------------------------------- Required
    headers = requires(dict)
    # ---------------------------------------------------------------- Defined
    decoderHeader = defines(IDecoderHeader, doc='''
    @rtype: IDecoderHeader
    The decoder used for reading the response headers.
    ''')

# --------------------------------------------------------------------

@injected
class HeaderDecodeResponseHandler(HandlerProcessorProceed, HeaderConfigurations):
    '''
    Provides the response decoding for handling HTTP headers.
    '''

    def __init__(self):
        HeaderConfigurations.__init__(self)
        HandlerProcessorProceed.__init__(self)

    def process(self, response:ResponseDecode, **keyargs):
        '''
        @see: HandlerProcessorProceed.process
        
        Provide the response headers decoders.
        '''
        assert isinstance(response, ResponseDecode), 'Invalid response %s' % response

        if not response.decoderHeader and response.headers is not None: 
            # Only add the decoder if one is not present or there are no headers
            response.decoderHeader = DecoderHeader(self, response.headers)

# --------------------------------------------------------------------

class RequestEncode(Context):
    '''
    The request encode context.
    '''
    # ---------------------------------------------------------------- Defined
    headers = defines(dict, doc='''
    @rtype: dictionary{string, string}
    The raw headers for the request that the encoder will place values to.
    ''')
    encoderHeader = defines(IEncoderHeader, doc='''
    @rtype: IEncoderHeader
    The header encoder used for encoding headers that will be used in the request.
    ''')

# --------------------------------------------------------------------
    
@injected
class HeaderEncodeRequestHandler(HandlerProcessorProceed, HeaderConfigurations):
    '''
    Provides the request encoder for handling HTTP headers.
    '''

    def __init__(self):
        HeaderConfigurations.__init__(self)
        HandlerProcessorProceed.__init__(self)

    def process(self, request:RequestEncode, **keyargs):
        '''
        @see: HandlerProcessorProceed.process
        
        Provide the request headers encoders.
        '''
        assert isinstance(request, RequestEncode), 'Invalid request %s' % request

        if not request.encoderHeader:  # Only add the encoder if one is not present
            request.encoderHeader = EncoderHeader(self)
        
            if request.headers: request.encoderHeader.headers.update(request.headers)
            request.headers = request.encoderHeader.headers
            
# --------------------------------------------------------------------

class ResponseEncode(Context):
    '''
    The response context.
    '''
    # ---------------------------------------------------------------- Defined
    headers = defines(dict, doc='''
    @rtype: dictionary{string, string}
    The raw headers for the response.
    ''')
    encoderHeader = defines(IEncoderHeader, doc='''
    @rtype: IEncoderHeader
    The header encoder used for encoding headers that will be rendered in the response.
    ''')

# --------------------------------------------------------------------
    
@injected
class HeaderEncodeResponseHandler(HandlerProcessorProceed, HeaderConfigurations):
    '''
    Provides the response encoder for handling HTTP headers.
    '''

    def __init__(self):
        HeaderConfigurations.__init__(self)
        HandlerProcessorProceed.__init__(self)

    def process(self, response:ResponseEncode, **keyargs):
        '''
        @see: HandlerProcessorProceed.process
        
        Provide the response headers encoders.
        '''
        assert isinstance(response, ResponseEncode), 'Invalid response %s' % response

        if not response.encoderHeader:  # Only add the encoder if one is not present
            response.encoderHeader = EncoderHeader(self)
        
            if response.headers: response.encoderHeader.headers.update(response.headers)
            response.headers = response.encoderHeader.headers

# --------------------------------------------------------------------

class DecoderHeader(IDecoderHeader):
    '''
    Implementation for @see: IDecoderHeader.
    '''
    __slots__ = ('configuration', 'headers', 'parameters', 'parametersUsed')

    def __init__(self, configuration, headers, parameters=None):
        '''
        Construct the decoder.
        
        @param configuration: HeaderConfigurations
            The header configuration.
        @param headers: dictionary{string, string}
            The header values.
        @param parameters: list[tuple(string, string)]
            The parameter values, this list will have have the used parameters removed.
        '''
        assert isinstance(configuration, HeaderConfigurations), 'Invalid configuration %s' % configuration
        assert isinstance(headers, dict), 'Invalid headers %s' % headers
        assert parameters is None or isinstance(parameters, list), 'Invalid parameters %s' % parameters

        self.configuration = configuration
        self.headers = {hname.lower():hvalue for hname, hvalue in headers.items()}
        self.parameters = parameters
        if parameters: self.parametersUsed = {}

    def retrieve(self, name):
        '''
        @see: IDecoderHeader.retrieve
        '''
        assert isinstance(name, str), 'Invalid name %s' % name
        cfg = self.configuration
        assert isinstance(cfg, HeaderConfigurations)
        
        name = name.lower()
        value = self.readParameters(name)
        if value: return cfg.separatorMain.join(value)

        return self.headers.get(name)

    def decode(self, name):
        '''
        @see: IDecoderHeader.decode
        '''
        assert isinstance(name, str), 'Invalid name %s' % name
        
        name = name.lower()
        value = self.readParameters(name)
        if value:
            parsed = []
            for v in value: self.parse(v, parsed)
            return parsed

        value = self.headers.get(name)
        if value: return self.parse(value)

    # ----------------------------------------------------------------

    def parse(self, value, parsed=None):
        '''
        Parses the provided value.
        
        @param value: string
            The value to parse.
        @param parsed: list[tuple(string, dictionary{string, string}]
            The parsed values.
        @return: list[tuple(string, dictionary{string, string}]
            The parsed values, if parsed is provided then it will be the same list.
        '''
        assert isinstance(value, str), 'Invalid value %s' % value
        cfg = self.configuration
        assert isinstance(cfg, HeaderConfigurations)

        parsed = [] if parsed is None else parsed
        for values in cfg.reSeparatorMain.split(value):
            valAttr = cfg.reSeparatorAttr.split(values)
            attributes = {}
            for k in range(1, len(valAttr)):
                val = cfg.reSeparatorValue.split(valAttr[k])
                attributes[val[0].strip()] = val[1].strip().strip('"') if len(val) > 1 else None
            parsed.append((valAttr[0].strip(), attributes))
        return parsed

    def readParameters(self, name):
        '''
        Read the parameters for the provided name.
        
        @param name: string
            The name (lower case) to read the parameters for.
        @return: deque[string]
            The list of found values, might be empty.
        '''
        if not self.parameters: return

        assert isinstance(name, str), 'Invalid name %s' % name
        assert name == name.lower(), 'Invalid name %s, needs to be lower case only' % name

        value = self.parametersUsed.get(name)
        if value is None:
            value, k = deque(), 0
            while k < len(self.parameters):
                if self.parameters[k][0].lower() == name:
                    value.append(self.parameters[k][1])
                    del self.parameters[k]
                    k -= 1
                k += 1
            self.parametersUsed[name] = value

        return value

class EncoderHeader(IEncoderHeader):
    '''
    Implementation for @see: IEncoderHeader.
    '''
    __slots__ = ('configuration', 'headers')

    def __init__(self, configuration):
        '''
        Construct the encoder.
        
        @param configuration: HeaderConfigurations
            The header configuration.
        '''
        assert isinstance(configuration, HeaderConfigurations), 'Invalid configuration %s' % configuration

        self.configuration = configuration
        self.headers = {}

    def encode(self, name, *value):
        '''
        @see: IEncoderHeader.encode
        '''
        assert isinstance(name, str), 'Invalid name %s' % name

        cfg = self.configuration
        assert isinstance(cfg, HeaderConfigurations)

        values = []
        for val in value:
            assert isinstance(val, Iterable), 'Invalid value %s' % val
            if isinstance(val, str): values.append(val)
            else:
                value, attributes = val
                attributes = cfg.separatorValue.join(attributes)
                values.append(cfg.separatorAttr.join((value, attributes)) if attributes else value)

        self.headers[name] = cfg.separatorMain.join(values)
