'''
Created on Jan 25, 2012

@package: ally core
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the text base encoder processor handler.
'''

from ally.container.ioc import injected
from ally.core.spec.meta import MetaService, IMetaEncode
from ally.design.context import Context, defines, requires
from ally.design.processor import HandlerProcessor, Chain
from ally.support.util_io import convertToBytes
from types import GeneratorType
import abc
import logging

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

class Response(Context):
    '''
    The response context.
    '''
    # ---------------------------------------------------------------- Required
    obj = requires(object)

class ResponseContent(Context):
    '''
    The response content context.
    '''
    # ---------------------------------------------------------------- Required
    type = requires(str)
    charSet = requires(str)
    # ---------------------------------------------------------------- Defined
    source = defines(GeneratorType, doc='''
    @rtype: GeneratorType
    The generator that provides the response content in bytes.
    ''')

# --------------------------------------------------------------------

@injected
class EncoderTextBaseHandler(HandlerProcessor):
    '''
    Provides the text base encoder.
    '''

    contentTypes = dict
    # The dictionary{string:string} containing as a key the content types specific for this encoder and as a value
    # the content type to set on the response, if None will use the key for the content type response. 
    encodingError = str
    # The encoding error resolving.

    modelMetaService = MetaService
    # The model meta service that will provide the decoding and encoding.

    def __init__(self):
        assert isinstance(self.contentTypes, dict), 'Invalid content types %s' % self.contentTypes
        assert isinstance(self.encodingError, str), 'Invalid string %s' % self.encodingError
        assert isinstance(self.modelMetaService, MetaService), 'Invalid model meta service %s' % self.modelMetaService
        super().__init__()
        # We also add the meta context to the response context
        self.processor.contexts['response'] += self.modelMetaService.createContextMeta
        # We also add the meta processing context to the response content context
        self.processor.contexts['responseCnt'] += self.modelMetaService.processContextMeta

    def process(self, chain, response:Response, responseCnt:ResponseContent, **keyargs):
        '''
        @see: HandlerProcessor.process
        
        Encode the ressponse object.
        '''
        assert isinstance(chain, Chain), 'Invalid processors chain %s' % chain
        assert isinstance(response, Response), 'Invalid response %s' % response
        assert isinstance(responseCnt, ResponseContent), 'Invalid response content %s' % responseCnt

        # Check if the response is for this encoder
        if responseCnt.type not in self.contentTypes:
            assert log.debug('The content type %r is not for this %s encoder', responseCnt.type, self) or True
        else:
            contentType = self.contentTypes[responseCnt.type]
            if contentType:
                assert log.debug('Normalized content type %r to %r', responseCnt.type, contentType) or True
                responseCnt.type = contentType

            metaEncode = self.modelMetaService.createEncode(response)
            assert isinstance(metaEncode, IMetaEncode), 'Invalid meta encode %s' % metaEncode

            meta = metaEncode.encode(response.obj, responseCnt)
            source = self.renderMeta(meta, responseCnt.charSet)
            responseCnt.source = convertToBytes(source, responseCnt.charSet, self.encodingError)

            return # We need to stop the chain if we war able to provide the encoding

        chain.proceed()

    # ----------------------------------------------------------------

    @abc.abstractclassmethod
    def renderMeta(self, meta, charSet):
        '''
        Renders the provided meta to a text.
        
        @param meta: Meta
            The meta do render.
        @param charSet: string
            A character set encoding required for the text.
        @return: generator
            The generator that delivers the encoded content in string format.
        '''
