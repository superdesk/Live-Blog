'''
Created on Jun 28, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Module containing specifications for the server processing.
'''

from ally.core.spec.codes import Code
from collections import deque
import abc
import logging

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

class Processor(metaclass=abc.ABCMeta):
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

class ProcessorsChain:
    '''
    A chain that contains a list of processors that are executed one by one. Each processor will have the duty
    to proceed with the processing if is the case by calling the chain.
    '''
    
    def __init__(self, processors):
        '''
        Initializes the chain with the processors to be executed.
        
        @param processors: list
            The list of processors to be executed. Attention the order in which the processors are provided
            is critical.
        '''
        assert isinstance(processors, list), 'Invalid processors list %s' % processors
        if __debug__:
            for processor in processors: assert isinstance(processor, Processor), 'Invalid processor %s' % processor
        self._processors = deque(processors)
        self._consumed = False
    
    def proceed(self):
        '''
        Indicates to the chain that it should proceed with the chain execution after a processor has returned. The proceed
        is available only when the chain execution is in execution. The execution is continued with the same request and
        response.
        '''
        self._proceed = True
    
    def process(self, request, response):
        '''
        Called in order to execute the next processors in the chain. This method will stop processing when all
        the processors have been executed.
        
        @param request: object
            The request to dispatch to the next processors to be executed.
        @param response: object
            The response to dispatch to the next processors to be executed.
        '''
        proceed = True
        while proceed:
            proceed = self._proceed = False
            if len(self._processors) > 0:
                proc = self._processors.popleft()
                assert isinstance(proc, Processor)
                assert log.debug('Processing %r', proc.__class__.__name__) or True
                proc.process(request, response, self)
                assert log.debug('Processing finalized %r', proc.__class__.__name__) or True
                if self._proceed:
                    assert log.debug('Proceed signal received, continue execution') or True
                    proceed = self._proceed
            else:
                assert log.debug('Processing finalized by consuming') or True
                self._consumed = True
    
    def isConsumed(self):
        '''
        Checks if the chain is consumed.
        
        @return: boolean
            True if all processors from the chain have been executed, False if a processor from the chain has stopped
            the execution of the other processors.
        '''
        return self._consumed

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
                assert isinstance(processor, Processor), 'Invalid processor %s' % processor
        self.processors = list(processors)
         
    def newChain(self):
        '''
        Constructs a new processors chain.
        
        @return: ProcessorsChain
            The chain of processors.
        '''
        return ProcessorsChain(self.processors)

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
        @ivar contentLanguage: string
            The content language for the content if known.
        @ivar contentConverter: Converter
            The content converter to use on decoding the content. 
        @ivar charSet: string
            The character set of the content.
        @ivar objFormat: dictionary{Type, string}
            Dictionary containing object formating specifications. The key is represent object types for formatting
            like: Number, Date, DateTime, Time, ... As a general rule this are the classes that are found in the 
            'type.formatted' module.
        '''
        self.contentType = None
        self.contentLanguage = None
        self.contentConverter = None
        self.charSet = None
        self.objFormat = {}

# --------------------------------------------------------------------

class ContentRequest(Content):
    '''
    Provides the content of a request.
    '''
    
    def __init__(self, file, keep=False):
        '''
        Constructs the content instance.
        
        @see: Content.__init__
        
        @param file: object
            The object with the 'read(nbytes)' method to provide the content bytes.
        @param keep: boolean
            Flag indicating that the used file handler should be kept open even if this content request is closed.
        @ivar length: integer|None
            The number of available bytes in the content, if None it means that is not known.
        '''
        super().__init__()
        assert file is not None and getattr(file, 'read') is not None, 'Invalid file object %s' % file
        assert isinstance(keep, bool), 'Invalid keep flag %s' % keep
        self.file = file
        self.keep = keep
        self.length = None
        self._offset = 0
        self._closed = False
    
    def read(self, nbytes=None):
        '''
        Reads nbytes from the content, attention the content can be read only once.
        
        @param nbytes: integer|None
            The number of bytes to read, or None to read all remaining available bytes from the content.
        '''
        if self._closed: raise ValueError('I/O operation on a closed file')
        count = nbytes
        if self.length is not None:
            if self._offset >= self.length:
                return ''
            delta = self.length - self._offset
            if count is None:
                count = delta
            elif count > delta:
                count = delta
        bytes = self.file.read(count)
        self._offset += len(bytes)
        return bytes
    
    def close(self):
        '''
        Closes the content stream.
        '''
        self._closed = True
        if not self.keep: self.file.close()

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
        self.contentLocation = None
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
        
        @param path: Path
            The path to be encoded.
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

