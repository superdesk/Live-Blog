'''
Created on May 25, 2012

@package: ally core http
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the parameters handler.
'''

from ally.container.ioc import injected
from ally.core.http.impl.encdec.parameter import ParameterDecoderEncoder
from ally.core.spec.codes import ILLEGAL_PARAM, Code
from ally.core.spec.encdec.render import Object, List, Value
from ally.core.spec.encdec.support import SAMPLE
from ally.core.spec.resources import Invoker, Path, Node, INodeInvokerListener, \
    Normalizer, Converter
from ally.design.context import Context, requires, defines
from ally.design.processor import HandlerProcessorProceed
from collections import deque
from weakref import WeakKeyDictionary
import logging

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

class Request(Context):
    '''
    The request context.
    '''
    # ---------------------------------------------------------------- Required
    parameters = requires(list)
    path = requires(Path)
    invoker = requires(Invoker)
    arguments = requires(dict)
    converter = requires(Converter)
    normalizer = requires(Normalizer)

class Response(Context):
    '''
    The response context.
    '''
    # ---------------------------------------------------------------- Defined
    code = defines(Code)
    text = defines(str)
    errorMessage = defines(str, doc='''
    @rtype: object
    The error message for the code.
    ''')
    errorDetails = defines(Object, doc='''
    @rtype: Object
    The error text object describing a detailed situation for the error.
    ''')

# --------------------------------------------------------------------

@injected
class ParameterHandler(HandlerProcessorProceed, INodeInvokerListener):
    '''
    Implementation for a processor that provides the transformation of parameters into arguments.
    '''

    parameterDecoderEncoder = ParameterDecoderEncoder
    # The parameter transformer to be used by the parameter handler.

    def __init__(self):
        assert isinstance(self.parameterDecoderEncoder, ParameterDecoderEncoder), \
        'Invalid parameter decoder/encoder %s' % self.parameterDecoderEncoder
        HandlerProcessorProceed.__init__(self)

        self._cacheDecode = WeakKeyDictionary()
        self._cacheEncode = WeakKeyDictionary()

    def process(self, request:Request, response:Response, **keyargs):
        '''
        @see: HandlerProcessorProceed.process
        
        Process the parameters into arguments.
        '''
        assert isinstance(request, Request), 'Invalid request %s' % request
        assert isinstance(response, Response), 'Invalid response %s' % response
        if Response.code in response and not response.code.isSuccess: return # Skip in case the response is in error

        assert isinstance(request.path, Path), 'Invalid request %s has no resource path' % request
        assert isinstance(request.path.node, Node), 'Invalid resource path %s has no node' % request.path
        assert isinstance(request.invoker, Invoker), 'No invoker available for %s' % request

        if request.parameters:
            decode = self._cacheDecode.get(request.invoker)
            if decode is None:
                decode = self.parameterDecoderEncoder.decodeInvoker(request.invoker)
                request.path.node.addNodeListener(self)
                self._cacheDecode[request.invoker] = decode

            illegal = []
            context = dict(target=request.arguments, normalizer=request.normalizer, converter=request.converter)
            for name, value in request.parameters:
                if not decode(path=name, value=value, **context): illegal.append((name, value))

            if illegal:
                encode = self._cacheEncode.get(request.invoker)
                if encode is None:
                    encode = self.parameterDecoderEncoder.encodeInvoker(request.invoker)
                    request.path.node.addNodeListener(self)
                    self._cacheEncode[request.invoker] = encode

                response.code, response.text = ILLEGAL_PARAM, 'Illegal parameter'
                context = dict(normalizer=request.normalizer, converter=request.converter)
                sample = encode(value=SAMPLE, **context)

                errors = [List('illegal', *(Value('name', name) for name, _value in illegal))]
                if sample:
                    assert isinstance(sample, deque), 'Invalid sample %s' % sample

                    response.errorMessage = 'Illegal parameter or value'
                    errors.append(List('sample', *(Object('sample', Value('name', name), Value('expected', value))
                                                   for name, value in sample)))
                else:
                    response.errorMessage = 'No parameters are allowed on this URL'

                response.errorDetails = Object('parameter', *errors)

    # ----------------------------------------------------------------

    def onInvokerChange(self, node, old, new):
        '''
        @see: INodeInvokerListener.onInvokerChange
        '''
        self._cacheDecode.pop(old, None)
        self._cacheEncode.pop(old, None)
