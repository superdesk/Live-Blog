'''
Created on Jun 28, 2011

@package: ally core
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Module containing specifications for the server processing.
'''

from ally.api import model
from ally.core.spec.codes import Code
import abc
import logging
from ally.support.util_design import Chain

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

class IProcessor(metaclass=abc.ABCMeta):
    '''
    Provides the specifications for all processor classes that are involved in resolving the request to a response.
    '''

    @abc.abstractmethod
    def process(self, request, response, chain):
        '''
        Processes the filtering, the processor has the duty to proceed by calling the chain.
        
        @param request: Request
            The request to be processed.
        @param response: Response
            The response to be processed.
        @param chain: ProcessorsChain
            The chain to call the next processors.
        '''

class ProcessorsChain(Chain):
    '''
    @see: Chain
    A chain that contains a list of processors that are executed one by one.
    '''

    def process(self, request, response):
        '''
        Called in order to execute the next processors in the chain. This method will stop processing when all
        the processors have been executed.
        
        @param request: Request
            The request to dispatch to the next processors to be executed.
        @param response: Response
            The response to dispatch to the next processors to be executed.
        '''
        assert isinstance(request, Request), 'Invalid request %s' % request
        assert isinstance(response, Response), 'Invalid response %s' % response
        super().process(request, response)

class Processors:
    '''
    Container for processor's, also provides chains for their execution.
    '''

    def __init__(self, *processors):
        '''
        @param processors: arguments[Processor]
            The list of processors that compose this container.
        '''
        if __debug__:
            for processor in processors:
                assert isinstance(processor, IProcessor), 'Invalid processor %s' % processor
        self.processors = list(processors)

    def newChain(self):
        '''
        Constructs a new processors chain.
        
        @return: ProcessorsChain
            The chain of processors.
        '''
        return ProcessorsChain(processor.process for processor in self.processors)

# --------------------------------------------------------------------

class Content:
    '''
    Provides the content data.
    '''

    def __init__(self):
        '''
        Constructs the content instance.
        
        @ivar contentType: string
            The content type for the content if known.
        @ivar charSet: string
            The character set of the content.
        @ivar contentLanguage: string
            The content language for the content if known.
        @ivar contentConverter: Converter
            The content converter to use on decoding the content. 
        @ivar objFormat: dictionary{Type, string}
            Dictionary containing object formating specifications. The key is represent object types for formatting
            like: Number, Date, DateTime, Time, ... As a general rule this are the classes that are found in the 
            'type.formatted' module.
        '''
        self.contentType = None
        self.charSet = None
        self.contentLanguage = None
        self.contentConverter = None
        self.objFormat = {}

# --------------------------------------------------------------------

class ContentRequest(Content, model.Content):
    '''
    Provides the content of a request.
    '''

    def __init__(self):
        '''
        Constructs the content request instance.
        
        @see: Content.__init__
        '''
        super().__init__()
        self.length = None

    def getName(self):
        '''
        @see: model.Content.getName
        '''
        return None

    def getCharSet(self):
        '''
        @see: model.Content.getCharSet
        '''
        return self.charSet

    def getLength(self):
        '''
        @see: model.Content.getLength
        '''
        return self.length

    @abc.abstractclassmethod
    def close(self):
        '''
        Closes the content stream.
        '''

    def next(self):
        '''
        @see: model.Content.next
        '''
        return None

# --------------------------------------------------------------------

class Request:
    '''
    Maps a request object based on a request path and action.
    '''

    def __init__(self):
        '''
        @ivar method: integer
            The method of the request, can be one of GET, INSERT, UPDATE or DELETE constants in the operator module.
        @ivar accContentTypes: list
            The content types accepted for response.
        @ivar accCharSets: list
            The character sets accepted for response.
        @ivar accLanguages: list
            The accepted languages for the request.
        @ivar content: Content
            The content provider for the request.
        @ivar resourcePath: Path
            The path to the resource node.
        @ivar invoker: Invoker
            The invoker obtained from the resource path to be used for calling the service.
        @ivar params: list
            A list of tuples containing on the first position the parameter string name and on the second the string
            parameter value as provided in the request path. The parameters need to be transformed into arguments
            and also removed from this list while doing that.
            I did not use a dictionary on this since the parameter names might repeat and also the order might be
            important.
        @ivar arguments: dictionary
            A dictionary containing as a key the argument name, this dictionary needs to be populated by the 
            processors as seen fit, also the parameters need to be transformed to arguments.
        '''
        self.method = None
        self.accContentTypes = []
        self.accCharSets = []
        self.accLanguages = []
        self.content = None
        self.resourcePath = None
        self.invoker = None
        self.params = []
        self.arguments = {}

# --------------------------------------------------------------------

class Response(Content):
    '''
    Provides the response support.
    '''

    def __init__(self):
        '''
        @see: Content.__init__
        
        @ivar code: Code
            The code of the response, do not update this directly use a one of the methods.
        @ivar codeMessage: object
            A message for the code, do not update this directly use a one of the methods.
        @ivar codeText: string
            A text message for the code, do not update this directly use a one of the methods.
        @ivar scheme: string
            The scheme URI protocol name to be used for the response.
        @ivar location: string
            The location where a request content can be found, used for redirects.
        @ivar allows: integer
            Contains the allow flags for the methods.
        @ivar encoderPath: EncoderPath
            The path encoder used for encoding paths that will be rendered in the response.
        @ivar obj: object
            The object to be rendered.
        @ivar objType: Type|None
            The type of the object to be rendered, if object type is None then the encoders expect as the object
            a composition of dictionaries, lists and string types, the normalization is handled by the encoder.
        @ivar objMeta: Object|None
            The object meta, used in getting the data from the response object.
        @ivar content: Iterable
            A generator or iterable that provides the content in bytes for the response.
        '''
        super().__init__()
        self.code = None
        self.codeMessage = None
        self.codeText = None
        self.scheme = None
        self.location = None
        self.allows = 0
        self.encoderPath = None
        self.obj = None
        self.objType = None
        self.objMeta = None
        self.content = None

    def addAllows(self, method):
        '''
        Set the status of allowing get method. 
        
        @param method: integer
            The method of the request, can be one of GET, INSERT, UPDATE or DELETE constants in this module.
        '''
        assert isinstance(method, int), \
        'Invalid method %s, needs to be one of the integer defined request methods' % method
        self.allows |= method

    def setCode(self, code, message, text=None):
        '''
        Sets the provided code.
        
        @param code: Code
            The code to set.
        @param message: object
            The message to send in relation to the code, can have multiple forms.
        @param text: string
            The message in text for the code.
        '''
        assert isinstance(code, Code), 'Invalid code %s' % code
        assert text is None or isinstance(text, str), 'Invalid code text %s, can be None' % text
        self.code = code
        self.codeMessage = message
        self.codeText = text
        if self.codeText is None and isinstance(self.codeMessage, str):
            self.codeText = message

# --------------------------------------------------------------------

class DecoderParams(metaclass=abc.ABCMeta): #TODO: DEPRECATED: to be refactored and removed, no decoders should be present
    '''
    Provides the decoding for request parameters.
    '''

    @abc.abstractmethod
    def decode(self, inputs, input, params, args):
        '''
        Decodes based on the input from the provided parameters the arguments that will be populated into args.
        If based on the provided input there are relevant parameters than remove those parameters from the provided
        list than the obtained arguments are added to the args dictionary.
        
        @param inputs: list
            The list of inputs involved in the decoding process, this are used to prevent confusion in
            decoding parameter names.
        @param input: Input
            The input to decode arguments for.
        @param params: list
            The list of tuples (param name, param value) to extract the arguments from, all the parameters that 
            are used need to be removed from the list.
        @param args: dictionary
            The dictionary {arg name:arg value} that will be populated with the obtained argument values.
        @raise DevelException: Thrown if a parameter does not contain the right value. 
        '''

# --------------------------------------------------------------------

class EncoderPath(metaclass=abc.ABCMeta):
    '''
    Provides the path encoding.
    '''

    @abc.abstractmethod
    def encode(self, path, parameters=None):
        '''
        Encodes the provided path to a full request path.
        
        @param path: Path|string
            The path to be encoded, for a local REST resource it will be a Path object, also it can be a string that will
            be interpreted as a path.
        @param parameters: list
            A list of tuples containing on the first position the parameter string name and on the second the string
            parameter value as to be represented in the request path.
        @return: object
            The full compiled request path, the type depends on the implementation.
        '''

class EncoderParams(metaclass=abc.ABCMeta):
    '''
    Provides the encoding from inputs to request parameters.
    '''

    @abc.abstractmethod
    def encode(self, inputs, input, arg, params):
        '''
        Encodes based on the input and provided argument value into the parameters list.
        
        @param inputs: list
            The list of inputs involved in the encoding process, this are used to prevent confusion in
            encoding parameter names.
        @param input: Input
            The input to encode the argument value for.
        @param arg: object
            The object value represented by the input to encode it.
        @param params: list
            A list of tuples containing on the first position the parameter string name and on the second the string
            parameter value as to be represented in the request path. To this list all the obtained parameters will 
            be added.
        @return: boolean
            True if this encoder has successful encoded the input, False otherwise.
        '''

    @abc.abstractmethod
    def encodeModels(self, inputs, input, models):
        '''
        Encodes the models represented by the provided input. The model is represented as a tuple 
        (isList, type, value), where isList specifies if the parameter contains a list, type the type of the 
        parameter and value needs to be either a string or list of strings depending on the isList flag.
        
        @param inputs: list
            The list of inputs involved in the encoding process, this are used to prevent confusion in
            encoding parameter names.
        @param input: Input
            The input to encode the argument value for.
        @param models: dictionary
            A dictionary having as a key the parameter name and as a value the model.
        '''

