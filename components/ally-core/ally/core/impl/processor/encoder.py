'''
Created on Jun 22, 2012

@package: ally core
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the meta creation for encoding the response.
'''

from ally.api.type import Type
from ally.container.ioc import injected
from ally.core.impl.encdec.model_encoder import ModelEncoder
from ally.core.spec.codes import Code, BAD_CONTENT
from ally.core.spec.encdec.exploit import Resolve
from ally.core.spec.encdec.render import IRender
from ally.core.spec.resources import Converter, Normalizer
from ally.design.context import defines, Context, requires
from ally.design.processor import HandlerProcessorProceed
from collections import Callable, Iterable
from io import BytesIO
from weakref import WeakKeyDictionary

# --------------------------------------------------------------------

class Response(Context):
    '''
    The response context.
    '''
    # ---------------------------------------------------------------- Required
    objType = requires(Type)
    obj = requires(object)
    # ---------------------------------------------------------------- Defined
    code = defines(Code)
    text = defines(str)

class ResponseContent(Context):
    '''
    The response content context.
    '''
    # ---------------------------------------------------------------- Required
    converterId = requires(Converter)
    converter = requires(Converter)
    normalizer = requires(Normalizer)
    renderFactory = requires(Callable)
    # ---------------------------------------------------------------- Defined
    source = defines(Iterable, doc='''
    @rtype: Iterable
    The generator containing the response content.
    ''')

# --------------------------------------------------------------------

@injected
class EncoderHandler(HandlerProcessorProceed):
    '''
    Implementation for a processor that provides the transformation of parameters into arguments.
    '''

    modelEncoder = ModelEncoder
    # The model encoder used for encoding.

    def __init__(self):
        assert isinstance(self.modelEncoder, ModelEncoder), 'Invalid model encoder %s' % self.modelEncoder
        super().__init__()

        self._cache = WeakKeyDictionary()

    def process(self, response:Response, responseCnt:ResponseContent, **keyargs):
        '''
        @see: HandlerProcessorProceed.process
        
        Create the meta responsable for encoding the response.
        '''
        assert isinstance(response, Response), 'Invalid response %s' % response
        assert isinstance(responseCnt, ResponseContent), 'Invalid response content %s' % responseCnt

        if Response.code in response and not response.code.isSuccess: return # Skip in case the response is in error
        assert isinstance(response.objType, Type), 'Invalid response object type %s' % response.objType

        encoder = self._cache.get(response.objType)
        if encoder is None:
            encoder = self.modelEncoder.encode(response.objType)
            if encoder is None:
                response.code, response.text = BAD_CONTENT, 'Cannot encode response object'
                return

            self._cache[response.objType] = encoder

        output = BytesIO()
        render = responseCnt.renderFactory(output)
        assert isinstance(render, IRender), 'Invalid render %s' % render

        data = dict(converterId=responseCnt.converterId, converter=responseCnt.converter,
                    normalizer=responseCnt.normalizer, render=render)
        resolve = Resolve(encoder)
        resolve.request(value=response.obj, **data)

        responseCnt.source = self.asGenerator(resolve, output)

    # ----------------------------------------------------------------

    def asGenerator(self, resolve, output, bufferSize=1024):
        '''
        Create a generator for the resolver, the resolver needs to push the data into the provided output bytes I/O.
        
        @param output: BytesIO
            The bytes stream to provide data from.
        @param resolve: Resolve
            The resolve to use for the output.
        @param bufferSize: integer
            The buffer size used for yielding data chunks.
        '''
        assert isinstance(resolve, Resolve), 'Invalid resolve %s' % resolve
        assert isinstance(output, BytesIO), 'Invalid output %s' % output
        assert isinstance(bufferSize, int), 'Invalid buffer size %s' % bufferSize

        while resolve.has():
            if output.tell() >= bufferSize:
                yield output.getvalue()
                output.seek(0)
                output.truncate()
            resolve.do()
        yield output.getvalue()
