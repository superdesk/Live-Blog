'''
Created on May 25, 2012

@package: ally core http
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the parameters handler.
'''
from ally.container.ioc import injected
from ally.core.spec.codes import ILLEGAL_PARAM
from ally.core.spec.meta import IMetaService, IMetaDecode, IMetaEncode, SAMPLE, \
    Value, Object
from ally.core.spec.resources import Invoker, Path, Node, \
    INodeInvokerListener
from ally.core.spec.server import Response, Request
from weakref import WeakKeyDictionary
from ally.design.processor import Handler, Chain, mokup, processor
from ally.core.http.spec.extension import URI
from ally.core.spec.extension import Invoke, CharConvert, Arguments

# --------------------------------------------------------------------

@mokup(Request, CharConvert, URI, Invoke)
class _Request(Request, CharConvert, URI, Invoke, Arguments):
    ''' Used as a mokup class '''

# --------------------------------------------------------------------

@injected
class ParameterHandler(Handler, INodeInvokerListener):
    '''
    Implementation for a processor that provides the transformation of parameters into arguments.
    '''

    parameterMetaService = IMetaService
    # The parameters meta service that will provide the decoding and encoding.

    def __init__(self):
        assert isinstance(self.parameterMetaService, IMetaService), \
        'Invalid parameter meta service %s' % self.parameterMetaService

        self._cacheDecode = WeakKeyDictionary()
        self._cacheEncode = WeakKeyDictionary()

    @processor
    def process(self, chain, request:_Request, response:Response, **keyargs):
        '''
        Process the parameters into arguments.
        '''
        assert isinstance(chain, Chain), 'Invalid processors chain %s' % chain
        assert isinstance(request, _Request), 'Invalid request %s' % request
        assert isinstance(response, Response), 'Invalid response %s' % response
        assert isinstance(request.path, Path), 'Invalid request %s has no resource path' % request
        assert isinstance(request.path.node, Node), 'Invalid resource path %s has no node' % request.path

        if request.parameters:
            assert isinstance(request.invoker, Invoker), 'No invoker available for %s' % request
            decode = self._cacheDecode.get(request.invoker)
            if decode is None:
                decode = self.parameterMetaService.createDecode(request)
                assert isinstance(decode, IMetaDecode), 'Invalid meta decode %s' % decode
                request.path.node.addNodeListener(self)
                self._cacheDecode[request.invoker] = decode

            illegal = []
            while request.parameters:
                name, value = request.parameters.popleft()
                if not decode.decode(name, value, request.arguments, request): illegal.append((name, value))

            if illegal:
                encode = self._cacheEncode.get(request.invoker)
                if encode is None:
                    encode = self.parameterMetaService.createEncode(request)
                    assert isinstance(encode, IMetaEncode), 'Invalid meta encode %s' % encode
                    request.resourcePath.node.addNodeListener(self)
                    self._cacheEncode[request.invoker] = encode

                response.code, response.text = ILLEGAL_PARAM, 'Illegal parameter'
                sample = encode.encode(SAMPLE, request)
                if sample is None:
                    response.message = 'No parameters are allowed on this URL.\nReceived parameters \'%s\''
                    response.message %= ','.join(name for name, _value in illegal)
                else:
                    assert isinstance(sample, Object), 'Invalid sample %s' % sample
                    allowed = []
                    for meta in sample.properties:
                        assert isinstance(meta, Value), 'Invalid meta %s' % meta
                        if isinstance(meta.value, str): value = meta.value
                        else: value = meta.value
                        allowed.append('%s=%s' % (meta.identifier, meta.value))
                    response.message = 'Illegal parameter or value:\n%s\nthe allowed parameters are:\n%s'
                    response.message %= ('\n'.join('%s=%s' % param for param in illegal), '\n'.join(allowed))
                return

        chain.proceed()

    # ----------------------------------------------------------------

    def onInvokerChange(self, node, old, new):
        '''
        @see: INodeInvokerListener.onInvokerChange
        '''
        self._cacheDecode.pop(old, None)
        self._cacheEncode.pop(old, None)
