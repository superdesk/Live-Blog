'''
Created on Jul 27, 2012

@package: ally core
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Renders the response encoder.
'''

from ally.container.ioc import injected
from ally.core.spec.codes import Code
from ally.core.spec.transform.exploit import Resolve
from ally.core.spec.transform.render import IRender
from ally.design.context import defines, Context, requires, optional
from ally.design.processor import HandlerProcessorProceed
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
    # ---------------------------------------------------------------- Optional
    code = optional(Code)
    # ---------------------------------------------------------------- Defined
    source = defines(Iterable, doc='''
    @rtype: Iterable
    The generator containing the response content.
    ''')

# --------------------------------------------------------------------

@injected
class RenderEncoderHandler(HandlerProcessorProceed):
    '''
    Implementation for a handler that renders the response content encoder.
    '''

    def process(self, response:Response, **keyargs):
        '''
        @see: HandlerProcessorProceed.process
        '''
        assert isinstance(response, Response), 'Invalid response %s' % response

        if Response.code in response and not response.code.isSuccess: return # Skip in case the response is in error
        if Response.encoder not in response: return # SKip in case there is no encoder to render

        response.source = self.renderAsGenerator(response.obj, response.encoder, response.renderFactory,
                                                 response.encoderData or {})

    def renderAsGenerator(self, value, encoder, renderFactory, data, bufferSize=1024):
        '''
        Create a generator for rendering the encoder.
        '''
        output = BytesIO()
        render = renderFactory(output)
        assert isinstance(render, IRender), 'Invalid render %s' % render

        resolve = Resolve(encoder).request(value=value, render=render, **data)

        while resolve.has():
            if output.tell() >= bufferSize:
                yield output.getvalue()
                output.seek(0)
                output.truncate()
            resolve.do()
        yield output.getvalue()
