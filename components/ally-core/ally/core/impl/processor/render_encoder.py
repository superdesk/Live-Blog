'''
Created on Jul 27, 2012

@package: ally core
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Renders the response encoder.
'''

from ally.container.ioc import injected
from ally.core.spec.transform.exploit import Resolve
from ally.core.spec.transform.render import IRender
from ally.design.processor.attribute import requires, defines, optional
from ally.design.processor.context import Context
from ally.design.processor.handler import HandlerProcessorProceed
from collections import Callable, Iterable
from io import BytesIO
import logging

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

class Response(Context):
    '''
    The response context.
    '''
    # ---------------------------------------------------------------- Required
    renderFactory = requires(Callable)
    encoder = requires(Callable)
    encoderData = requires(dict)
    obj = requires(object)
    isSuccess = requires(bool)

class ResponseContent(Context):
    '''
    The response content context.
    '''
    # ---------------------------------------------------------------- Defined
    source = defines(Iterable, doc='''
    @rtype: Iterable
    The generator containing the response content.
    ''')
    length = defines(int)

# --------------------------------------------------------------------

@injected
class RenderEncoderHandler(HandlerProcessorProceed):
    '''
    Implementation for a handler that renders the response content encoder.
    '''
    
    allowChunked = False
    # Flag indicating that a chuncked transfer is allowed, more or less if this is false a length is a must.
    bufferSize = 1024
    # The buffer size used in the generator returned chuncks.
    
    def __init__(self):
        assert isinstance(self.allowChunked, bool), 'Invalid allow chuncked flag %s' % self.allowChunked
        assert isinstance(self.bufferSize, int), 'Invalid buffer size %s' % self.bufferSize
        super().__init__()

    def process(self, response:Response, responseCnt:ResponseContent, **keyargs):
        '''
        @see: HandlerProcessorProceed.process
        
        Process the encoder rendering.
        '''
        assert isinstance(response, Response), 'Invalid response %s' % response
        assert isinstance(responseCnt, ResponseContent), 'Invalid response content %s' % responseCnt

        if response.isSuccess is False: return  # Skip in case the response is in error
        if response.encoder is None: return  # Skip in case there is no encoder to render
        assert callable(response.renderFactory), 'Invalid response renderer factory %s' % response.renderFactory

        output = BytesIO()
        render = response.renderFactory(output)
        assert isinstance(render, IRender), 'Invalid render %s' % render

        resolve = Resolve(response.encoder).request(value=response.obj, render=render, **response.encoderData or {})

        if not self.allowChunked and responseCnt.length is None:
    
            while resolve.has(): resolve.do()
            content = output.getvalue()
            responseCnt.length = len(content)
            responseCnt.source = (content,)
            output.close()
        else:
            responseCnt.source = self.renderAsGenerator(resolve, output, self.bufferSize)

    def renderAsGenerator(self, resolve, output, bufferSize):
        '''
        Create a generator for rendering the encoder.
        '''
        while resolve.has():
            if output.tell() >= bufferSize:
                yield output.getvalue()
                output.seek(0)
                output.truncate()
            resolve.do()
        yield output.getvalue()
        output.close()
