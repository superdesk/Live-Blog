'''
Created on May 25, 2012

@package: ally core http
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the parameters handler.
'''
from ally.container.ioc import injected
from ally.core.http.spec import RequestHTTP
from ally.core.spec.codes import ILLEGAL_PARAM
from ally.core.spec.meta import IMetaService, IMetaDecode, IMetaEncode, SAMPLE, \
    Value, Object, Context
from ally.core.spec.resources import Invoker, ConverterPath, Path, Node, \
    INodeInvokerListener
from ally.core.spec.server import IProcessor, ProcessorsChain, Response
from weakref import WeakKeyDictionary

# --------------------------------------------------------------------

@injected
class ParameterHandler(IProcessor, INodeInvokerListener):
    '''
    Implementation for a processor that provides the transformation of parameters into arguments.
    
    Provides on request: arguments
    Provides on response: NA
    
    Requires on request: resourcePath, invoker, parameters
    Requires on response: NA
    '''

    parameterMetaService = IMetaService
    # The parameters meta service that will provide the decoding and encoding.
    converterPath = ConverterPath
    # The converter path used in parsing the parameter values.

    def __init__(self):
        assert isinstance(self.parameterMetaService, IMetaService), \
        'Invalid parameter meta service %s' % self.parameterMetaService
        assert isinstance(self.converterPath, ConverterPath), 'Invalid ConverterPath object %s' % self.converterPath

        self._cacheDecode = WeakKeyDictionary()
        self._cacheEncode = WeakKeyDictionary()

    def process(self, req, rsp, chain):
        '''
        @see: IProcessor.process
        '''
        assert isinstance(chain, ProcessorsChain), 'Invalid processors chain %s' % chain
        assert isinstance(req, RequestHTTP), 'Invalid request %s' % req
        assert isinstance(rsp, Response), 'Invalid response %s' % rsp
        assert isinstance(req.resourcePath, Path), 'Invalid request %s has no resource path' % req
        assert isinstance(req.resourcePath.node, Node), 'Invalid resource path %s has no node' % req.resourcePath

        if req.parameters:
            assert isinstance(req.invoker, Invoker), 'No invoker found on the request %s' % req
            decode = self._cacheDecode.get(req.invoker)
            if decode is None:
                decode = self.parameterMetaService.createDecode(Context(invoker=req.invoker))
                assert isinstance(decode, IMetaDecode), 'Invalid meta decode %s' % decode
                req.resourcePath.node.addNodeListener(self)
                self._cacheDecode[req.invoker] = decode

            illegal = []
            context = Context(converter=self.converterPath, normalizer=self.converterPath)
            while req.parameters:
                name, value = req.parameters.popleft()
                if not decode.decode(name, value, req.arguments, context): illegal.append((name, value))

            if illegal:
                encode = self._cacheEncode.get(req.invoker)
                if encode is None:
                    encode = self.parameterMetaService.createEncode(Context(invoker=req.invoker))
                    assert isinstance(encode, IMetaEncode), 'Invalid meta encode %s' % encode
                    req.resourcePath.node.addNodeListener(self)
                    self._cacheEncode[req.invoker] = encode

                sample = encode.encode(SAMPLE, context)
                if sample is None:
                    text = 'No parameters are allowed on this URL.\nReceived parameters \'%s\''
                    text %= ','.join(name for name, _value in illegal)
                else:
                    assert isinstance(sample, Object), 'Invalid sample %s' % sample
                    allowed = []
                    for meta in sample.properties:
                        assert isinstance(meta, Value), 'Invalid meta %s' % meta
                        if isinstance(meta.value, str): value = meta.value
                        else: value = meta.value
                        allowed.append('%s=%s' % (meta.identifier, meta.value))
                    text = 'Illegal parameter or value:\n%s\nthe allowed parameters are:\n%s'
                    text %= ('\n'.join('%s=%s' % param for param in illegal), '\n'.join(allowed))

                rsp.setCode(ILLEGAL_PARAM, text, 'Illegal parameter')
                return

        chain.proceed()

    # ----------------------------------------------------------------

    def onInvokerChange(self, node, old, new):
        '''
        @see: INodeInvokerListener.onInvokerChange
        '''
        self._cacheDecode.pop(old, None)
        self._cacheEncode.pop(old, None)
