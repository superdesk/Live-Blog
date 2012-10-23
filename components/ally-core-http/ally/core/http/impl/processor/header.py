'''
Created on Jul 9, 2011

@package: ally core http
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the standard headers handling.
'''

from ally.container.ioc import injected
from ally.core.http.spec.server import IDecoderHeader, IEncoderHeader
from ally.design.context import Context, defines, requires, optional
from ally.design.processor import HandlerProcessorProceed
from collections import deque, Iterable
import re

# --------------------------------------------------------------------

class Request(Context):
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
    The decoder used for reading the headers.
    ''')

class Response(Context):
    '''
    The response context.
    '''
    # ---------------------------------------------------------------- Defined
    headers = defines(dict, doc='''
    @rtype: dictionary{string, string}
    The raw headers for the response.
    ''')
    encoderHeader = defines(IEncoderHeader, doc='''
    @rtype: IEncoderPath
    The path encoder used for encoding paths that will be rendered in the response.
    ''')

# --------------------------------------------------------------------

@injected
class HeaderHandler(HandlerProcessorProceed):
    '''
    Provides encoder/decoder for handling HTTP headers.
    '''

    useParameters = False
    # If true then if the data is present in the parameters will override the header.

    separatorMain = ','
    # The separator used in splitting value and attributes from each other. 
    separatorAttr = ';'
    # The separator used between the attributes and value.
    separatorValue = '='
    # The separator used between attribute name and attribute value.

    def __init__(self):
        assert isinstance(self.useParameters, bool), 'Invalid use parameters flag %s' % self.useParameters
        assert isinstance(self.separatorMain, str), 'Invalid main separator %s' % self.separatorMain
        assert isinstance(self.separatorAttr, str), 'Invalid attribute separator %s' % self.separatorAttr
        assert isinstance(self.separatorValue, str), 'Invalid value separator %s' % self.separatorValue
        super().__init__()

        self.reSeparatorMain = re.compile(self.separatorMain)
        self.reSeparatorAttr = re.compile(self.separatorAttr)
        self.reSeparatorValue = re.compile(self.separatorValue)

    def process(self, request:Request, response:Response, **keyargs):
        '''
        @see: HandlerProcessorProceed.process
        
        Provide the headers encoders and decoders.
        '''
        assert isinstance(request, Request), 'Invalid request %s' % request
        assert isinstance(response, Response), 'Invalid response %s' % response

        request.decoderHeader = DecoderHeader(self, request.headers, request.parameters
                                              if Request.parameters in request and self.useParameters else None)
        response.encoderHeader = EncoderHeader(self)
        response.headers = response.encoderHeader.headers

# --------------------------------------------------------------------

class DecoderHeader(IDecoderHeader):
    '''
    Implementation for @see: IDecoderHeader.
    '''
    __slots__ = ('handler', 'headers', 'parameters', 'parametersUsed')

    def __init__(self, handler, headers, parameters=None):
        '''
        Construct the decoder.
        
        @param handler: HeaderHandler
            The header handler of the decoder.
        @param headers: dictionary{string, string}
            The header values.
        @param parameters: list[tuple(string, string)]
            The parameter values, this list will have have the used parameters removed.
        '''
        assert isinstance(handler, HeaderHandler), 'Invalid handler %s' % handler
        assert isinstance(headers, dict), 'Invalid headers %s' % headers
        assert parameters is None or isinstance(parameters, list), 'Invalid parameters %s' % parameters

        self.handler = handler
        self.headers = {hname.lower():hvalue for hname, hvalue in headers.items()}
        self.parameters = parameters
        if parameters: self.parametersUsed = {}

    def retrieve(self, name):
        '''
        @see: IDecoderHeader.retrieve
        '''
        assert isinstance(name, str), 'Invalid name %s' % name

        name = name.lower()
        value = self.readParameters(name)
        if value: return self.handler.separatorMain.join(value)

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
        handler = self.handler
        assert isinstance(handler, HeaderHandler)

        parsed = [] if parsed is None else parsed
        for values in handler.reSeparatorMain.split(value):
            valAttr = handler.reSeparatorAttr.split(values)
            attributes = {}
            for k in range(1, len(valAttr)):
                val = handler.reSeparatorValue.split(valAttr[k])
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
    __slots__ = ('handler', 'headers')

    def __init__(self, handler):
        '''
        Construct the encoder.
        
        @param handler: HeaderHandler
            The header handler of the encoder.
        '''
        assert isinstance(handler, HeaderHandler), 'Invalid handler %s' % handler

        self.handler = handler
        self.headers = {}

    def encode(self, name, *value):
        '''
        @see: IEncoderHeader.encode
        '''
        assert isinstance(name, str), 'Invalid name %s' % name

        handler = self.handler
        assert isinstance(handler, HeaderHandler)

        values = []
        for val in value:
            assert isinstance(val, Iterable), 'Invalid value %s' % val
            if isinstance(val, str): values.append(val)
            else:
                value, attributes = val
                attributes = handler.separatorValue.join(attributes)
                values.append(handler.separatorAttr.join((value, attributes)) if attributes else value)

        self.headers[name] = handler.separatorMain.join(values)
