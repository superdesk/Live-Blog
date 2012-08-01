'''
Created on Jan 25, 2012

@package: ally core
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the text base encoder processor handler.
'''

from ally.container.ioc import injected
from ally.design.context import Context, defines, requires
from ally.design.processor import HandlerProcessor, Chain
from collections import Callable
from functools import partial
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
    type = requires(str)
    charSet = requires(str)
    # ---------------------------------------------------------------- Defined
    renderFactory = defines(Callable, doc='''
    @rtype: callable(IOutputStream) -> IRender
    The renderer factory to be used for the response.
    ''')

# --------------------------------------------------------------------

@injected
class RenderBaseHandler(HandlerProcessor):
    '''
    Provides the text base renderer.
    '''

    contentTypes = dict
    # The dictionary{string:string} containing as a key the content types specific for this encoder and as a value
    # the content type to set on the response, if None will use the key for the content type response. 

    def __init__(self):
        assert isinstance(self.contentTypes, dict), 'Invalid content types %s' % self.contentTypes
        super().__init__()

    def process(self, chain, response:Response, **keyargs):
        '''
        @see: HandlerProcessor.process
        
        Encode the ressponse object.
        '''
        assert isinstance(chain, Chain), 'Invalid processors chain %s' % chain
        assert isinstance(response, Response), 'Invalid response %s' % response

        # Check if the response is for this encoder
        if response.type not in self.contentTypes:
            assert log.debug('The content type \'%s\' is not for this %s encoder', response.type, self) or True
        else:
            contentType = self.contentTypes[response.type]
            if contentType:
                assert log.debug('Normalized content type \'%s\' to \'%s\'', response.type, contentType) or True
                response.type = contentType

            response.renderFactory = partial(self.renderFactory, response)
            return # We need to stop the chain if we have been able to provide the encoding

        chain.proceed()

    # ----------------------------------------------------------------

    @abc.abstractclassmethod
    def renderFactory(self, response, output):
        '''
        Factory method used for creating a renderer.
        
        @param response: Response
            The response to process the renderer.
        @param output: IOutputStream
            The output stream to be used by the renderer.
        @return: IRender
            The renderer.
        '''
