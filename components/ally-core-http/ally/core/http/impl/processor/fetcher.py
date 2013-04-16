'''
Created on Jul 31, 2012

@package: ally core http
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the standard headers handling.
'''

from ally.api.operator.type import TypeModelProperty, TypeModel
from ally.api.type import Input, typeFor, TypeClass, Type
from ally.container.ioc import injected
from ally.core.http.spec.transform.support_model import DataModel, IFetcher
from ally.core.spec.resources import Path, Node, Invoker, INodeInvokerListener
from ally.design.processor.attribute import requires
from ally.design.processor.context import Context
from ally.design.processor.handler import HandlerProcessorProceed
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
    path = requires(Path)
    invoker = requires(Invoker)
    arguments = requires(dict)

class Response(Context):
    '''
    The response context.
    '''
    # ---------------------------------------------------------------- Required
    encoderData = requires(dict)
    encoderDataModel = requires(DataModel)
    isSuccess = requires(bool)

# --------------------------------------------------------------------

@injected
class FetcherHandler(HandlerProcessorProceed, INodeInvokerListener):
    '''
    Implementation for a handler that provides the fetcher used in getting the filtered models.
    '''
    typeResponse = TypeClass(Response)

    def __init__(self):
        '''
        Construct the encoder.
        '''
        assert isinstance(self.typeResponse, Type), 'Invalid type response %s' % self.typeResponse
        super().__init__()

        self._cache = WeakKeyDictionary()

    def process(self, request:Request, response:Response, **keyargs):
        '''
        @see: HandlerProcessorProceed.process
        
        Provide the fetcher.
        '''
        assert isinstance(request, Request), 'Invalid request %s' % request
        assert isinstance(response, Response), 'Invalid response %s' % response

        if response.isSuccess is False: return  # Skip in case the response is in error
        if response.encoderDataModel is None: return
        invokerMain = request.invoker
        assert isinstance(invokerMain, Invoker), 'Invalid invoker %s' % invokerMain
        assert isinstance(response.encoderData, dict), 'Invalid encoder data %s' % response.encoderData

        fetch = self.extractFetch(response.encoderDataModel)
        if fetch:
            references, pack = set(fetch), self._cache.get(invokerMain)
            if pack:
                fetcher, fetcherReferences = pack
                if not (references == fetcherReferences or references.issubset(fetcherReferences)):
                    fetcher = None
                    references.update(fetcherReferences)
            else: fetcher = None

            if fetcher is None:
                assert isinstance(request.path, Path), 'Invalid request path %s' % request.path
                node = request.path.node
                assert isinstance(node, Node), 'Invalid path node %s' % node
                node = node.root
                node.addStructureListener(self)

                fetcher = FetcherInvoker(invokerMain)
                self._cache[invokerMain] = (fetcher, references)
                for reference, invoker in fetch.items():
                    assert isinstance(invoker, Invoker)

                    modelType, indexes = typeFor(reference), []
                    if isinstance(modelType, TypeModelProperty):
                        assert isinstance(modelType, TypeModelProperty)
                        modelType = modelType.type
                    assert isinstance(modelType, TypeModel), 'Invalid mode type %s' % modelType

                    for inp in invoker.inputs:
                        assert isinstance(inp, Input)
                        if inp.hasDefault: indexes.append(fetcher.addInput(inp))
                        else:
                            if isinstance(inp.type, TypeModelProperty):
                                assert isinstance(inp.type, TypeModelProperty)
                                if inp.type.parent == modelType:
                                    indexes.append(None)
                                    continue
                            for k, inpm in enumerate(invokerMain.inputs):
                                assert isinstance(inpm, Input)
                                if inp.type == inpm.type:
                                    indexes.append(k)
                                    break
                            else:
                                log.warning('Cannot locate any input main invoker %s input for invoker %s and input %s',
                                            invokerMain, invoker, inp)
                                break
                    else: fetcher.addFetch(reference, invoker, indexes)

                fetcher.inputs.append(Input('$response', self.typeResponse, True, None))

            request.invoker = fetcher
            if request.arguments is None: request.arguments = {}
            request.arguments['$response'] = response

    def extractFetch(self, data, fetch=None):
        '''
        Extracts from the data model all the required fetch model values.
        
        @return: dictionary{Reference:Invoker}
            A dictionary containing the reference of the model and as a value the invoker that delivers the model for
            the reference.
        '''
        assert isinstance(data, DataModel), 'Invalid data model %s' % data
        if fetch is None: fetch = {}
        assert isinstance(fetch, dict), 'Invalid fetch %s' % fetch

        if data.fetchReference and data.path:
            assert isinstance(data.path, Path), 'Invalid data path %s' % data.path
            assert isinstance(data.path.node, Node), 'Invalid data path node %s' % data.path.node

            invoker = data.path.node.get
            if invoker: fetch[data.fetchReference] = invoker

            if data.fetchData: self.extractFetch(data.fetchData, fetch)
        elif DataModel.datas in data:
            for cdata in data.datas.values(): self.extractFetch(cdata, fetch)

        return fetch

    # ----------------------------------------------------------------

    def onInvokerChange(self, node, old, new):
        '''
        @see: INodeInvokerListener.onInvokerChange
        '''
        self._cache.clear()

# --------------------------------------------------------------------

class FetcherInvoker(Invoker):
    '''
    Invoker that provides the model fetching.
    '''
    __slots__ = ('invoker', 'references', 'invokers')

    def __init__(self, invoker):
        '''
        Construct the fetcher.
        '''
        assert isinstance(invoker, Invoker), 'Invalid invoker %s' % invoker
        Invoker.__init__(self, invoker.name, invoker.method, invoker.output, list(invoker.inputs), invoker.hints,
                         invoker.infoIMPL, invoker.infoAPI)

        self.invoker = invoker
        self.references = {}
        self.invokers = []

    def addInput(self, inp):
        '''
        Add a new optional input to the invoker inputs.
        
        @param inp: Input
            The input to be added.
        @return: integer
            The index of the input.
        '''
        assert isinstance(inp, Input), 'Invalid input %s' % inp
        assert inp.hasDefault, 'Input is not optional %s' % inp

        self.inputs.append(Input('%s.%s' % (inp.name, len(self.invokers)), inp.type, True, inp.default))

        return len(self.inputs) - 1

    def addFetch(self, reference, invoker, indexes):
        '''
        Add a new reference entry in the fetcher.
        
        @param reference: Reference
            The reference for fetching.
        @param invoker: Invoker
            The invoker associated with the reference.
        @param indexes: list[integer]
            The indexes in the invoker arguments to be used for the invoker at fetching, basically all the indexes of
            the arguments (beside of the model id one which is None in the indexes) to be used for call the invoker.
        '''
        assert isinstance(invoker, Invoker), 'Invalid invoker %s' % invoker
        assert isinstance(indexes, list), 'Invalid indexes list %s' % indexes

        self.references[reference] = len(self.invokers)
        self.invokers.append((invoker, indexes))

    def invoke(self, *args):
        '''
        @see: Invoker.invoke
        '''
        response = args[-1]
        assert isinstance(response, Response), 'Invalid response %s' % response
        response.encoderData.update(fetcher=Fetcher(self, args))
        return self.invoker.invoke(*args[:len(self.invoker.inputs)])

class Fetcher(IFetcher):
    '''
    The fetcher implementation.
    '''
    __slots__ = ('fetcher', 'args', '_cache')

    def __init__(self, fetcher, args):
        '''
        Construct the fetcher.
        '''
        assert isinstance(fetcher, FetcherInvoker), 'Invalid fetcher invoker %s' % fetcher
        assert isinstance(args, (tuple, list)), 'Invalid arguments %s' % args

        self.fetcher = fetcher
        self.args = args

        self._cache = {}

    def fetch(self, reference, valueId):
        '''
        @see: IFetcher.fetch
        '''
        value, values = self, self._cache.get(reference)
        if values is None: values = self._cache[reference] = {}
        else: value = values.get(valueId, value)
        if value is self:
            fetcher = self.fetcher
            assert isinstance(fetcher, FetcherInvoker)

            index = fetcher.references.get(reference)
            if index is None: value = None
            else:
                invoker, indexes = fetcher.invokers[index]
                assert isinstance(invoker, Invoker)

                value = invoker.invoke(*(valueId if k is None else self.args[k] for k in indexes))
            values[valueId] = value

        return value

