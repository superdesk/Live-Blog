'''
Created on Jul 12, 2011

@package: ally core
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the encoding processing node.
'''

from ally.container.ioc import injected
from ally.core.spec.codes import UNKNOWN_ENCODING, Code
from ally.design.context import Context, defines, optional
from ally.design.processor import Assembly, Handler, Processing, NO_VALIDATION, \
    Processor, Chain
import codecs
import itertools
import logging
from ally.exception import DevelError

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

class Request(Context):
    '''
    The request context.
    '''
    # ---------------------------------------------------------------- Optional
    accTypes = optional(list)
    accCharSets = optional(list)

class Response(Context):
    '''
    The response context.
    '''
    # ---------------------------------------------------------------- Defined
    code = defines(Code)
    text = defines(str)

class ResponseContent(Context):
    '''
    The response content context.
    '''
    # ---------------------------------------------------------------- Defined
    type = defines(str, doc='''
    @rtype: string
    The response content type.
    ''')
    charSet = defines(str, doc='''
    @rtype: string
    The character set for the text content.
    ''')

# --------------------------------------------------------------------

@injected
class EncodingHandler(Handler):
    '''
    Implementation for a processor that provides the support for executing the encoding processors. The encoding
    just like decoding uses an internal processor chain execution. If a processor is successful in the encoding
    process it has to stop the chain execution.
    '''

    contentTypeDefaults = [None]
    # The default content types to use
    charSetDefault = str
    # The default character set to be used if none provided for the content.
    encodingAssembly = Assembly
    # The encoding processors, if a processor is successful in the encoding process it has to stop the 
    # chain execution.

    def __init__(self):
        assert isinstance(self.encodingAssembly, Assembly), 'Invalid encodings assembly %s' % self.encodingAssembly
        assert isinstance(self.contentTypeDefaults, (list, tuple)), \
        'Invalid default content type %s' % self.contentTypeDefaults
        assert isinstance(self.charSetDefault, str), 'Invalid default character set %s' % self.charSetDefault

        contexts = dict(request=Request, response=Response, responseCnt=ResponseContent)
        encodingProcessing = self.encodingAssembly.create(NO_VALIDATION, **contexts)
        assert isinstance(encodingProcessing, Processing), 'Invalid processing %s' % encodingProcessing
        contexts = encodingProcessing.contexts

        def call(chain, **keyargs):
            assert isinstance(chain, Chain), 'Invalid processors chain %s' % chain
            self.process(encodingProcessing, **keyargs)
            chain.proceed()

        cd = self.process.__code__
        super().__init__(Processor(contexts, call, 'process', cd.co_filename, cd.co_firstlineno))

    def process(self, encodingProcessing, request, response, responseCnt, **keyargs):
        '''
        Encodes the response object.
        
        @param encodingProcessing: Processing
            The processing that provides the encoding chain.
            
        The rest of the parameters are contexts.
        '''
        assert isinstance(encodingProcessing, Processing), 'Invalid encoding processing %s' % encodingProcessing
        assert isinstance(request, Request), 'Invalid request %s' % request
        assert isinstance(response, Response), 'Invalid response %s' % response
        assert isinstance(responseCnt, ResponseContent), 'Invalid response content %s' % responseCnt

        # Resolving the character set
        if ResponseContent.charSet in responseCnt:
            try: codecs.lookup(responseCnt.charSet)
            except LookupError: responseCnt.charSet = None
        else: responseCnt.charSet = None

        if responseCnt.charSet is None:
            for charSet in request.accCharSets or ():
                try: codecs.lookup(charSet)
                except LookupError: continue
                responseCnt.charSet = charSet
                break
            else: responseCnt.charSet = self.charSetDefault

        if ResponseContent.type in responseCnt:
            encodingChain = encodingProcessing.newChain()
            assert isinstance(encodingChain, Chain), 'Invalid chain %s' % encodingChain

            responseWasInError = Response.code in response and not response.code.isSuccess
            encodingChain.process(request=request, response=response, responseCnt=responseCnt, **keyargs)
            if encodingChain.isConsumed() and not responseWasInError:
                if Response.code in response and not response.code.isSuccess: return
                response.code = UNKNOWN_ENCODING
                response.text = 'Content type \'%s\' not supported for encoding' % responseCnt.type
                return

        # Adding None in case some encoder is configured as default.
        for contentType in itertools.chain(request.accTypes or (), self.contentTypeDefaults):
            responseCnt.type = contentType

            encodingChain = encodingProcessing.newChain()
            assert isinstance(encodingChain, Chain), 'Invalid chain %s' % encodingChain

            encodingChain.process(request=request, response=response, responseCnt=responseCnt, **keyargs)
            if not encodingChain.isConsumed(): break
        else:
            raise DevelError('There is no encoding available, this is more likely a setup issues since the '
                             'default content types should have resolved the encoding')
