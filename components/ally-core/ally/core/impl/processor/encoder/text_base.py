'''
Created on Jan 25, 2012

@package: ally core
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the text base encoder processor handler.
'''

from ally.container.ioc import injected
from ally.core.spec.meta import Meta
from ally.design.context import Context, defines, requires
from ally.design.processor import HandlerProcessor, Chain
from ally.support.util_io import convertToBytes
from types import GeneratorType
import abc
import logging

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

class ResponseContent(Context):
    '''
    The response content context.
    '''
    # ---------------------------------------------------------------- Required
    type = requires(str)
    charSet = requires(str)
    meta = requires(Meta)
    # ---------------------------------------------------------------- Defined
    source = defines(GeneratorType, doc='''
    @rtype: generator
    The generator containing the response content.
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

    def __init__(self):
        assert isinstance(self.contentTypes, dict), 'Invalid content types %s' % self.contentTypes
        assert isinstance(self.encodingError, str), 'Invalid string %s' % self.encodingError
        super().__init__()

    def process(self, chain, responseCnt:ResponseContent, **keyargs):
        '''
        @see: HandlerProcessor.process
        
        Encode the ressponse object.
        '''
        assert isinstance(chain, Chain), 'Invalid processors chain %s' % chain
        assert isinstance(responseCnt, ResponseContent), 'Invalid response content %s' % responseCnt

        # Check if the response is for this encoder
        if responseCnt.type not in self.contentTypes:
            assert log.debug('The content type %r is not for this %s encoder', responseCnt.type, self) or True
        else:
            contentType = self.contentTypes[responseCnt.type]
            if contentType:
                assert log.debug('Normalized content type %r to %r', responseCnt.type, contentType) or True
                responseCnt.type = contentType

            assert isinstance(responseCnt.meta, Meta), 'Invalid meta encode %s' % responseCnt.meta

            source = self.renderMeta(responseCnt.meta, responseCnt.charSet)
            responseCnt.source = convertToBytes(source, responseCnt.charSet, self.encodingError)

            return # We need to stop the chain if we have been able to provide the encoding

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
