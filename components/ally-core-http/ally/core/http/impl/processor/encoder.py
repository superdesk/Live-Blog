'''
Created on Jun 22, 2012

@package: ally core http
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the meta creation for encoding the response.
'''

from ally.api.operator.container import Model
from ally.api.operator.type import TypeModel, TypeModelProperty
from ally.api.type import Type, TypeReference
from ally.container.ioc import injected
from ally.core.http.spec.codes import INVALID_HEADER_VALUE
from ally.core.http.spec.server import IEncoderPath, IDecoderHeader
from ally.core.http.spec.transform.support_model import DataModel, NO_MODEL_PATH, \
    IFetcher
from ally.core.impl.processor import encoder
from ally.core.impl.processor.encoder import CreateEncoderHandler, EncodeObject, \
    EncodeCollection
from ally.core.spec.resources import Path, Normalizer, Invoker
from ally.core.spec.transform.exploit import handleExploitError
from ally.core.spec.transform.render import IRender
from ally.design.context import requires, defines
from ally.support.core.util_resources import pathLongName
from ally.support.util import lastCheck, firstOf
from collections import deque, OrderedDict

# --------------------------------------------------------------------

class Request(encoder.Request):
    '''
    The request context.
    '''
    # ---------------------------------------------------------------- Required
    path = requires(Path)

class Response(encoder.Response):
    '''
    The response context.
    '''
    # ---------------------------------------------------------------- Required
    encoderPath = requires(IEncoderPath)
    # ---------------------------------------------------------------- Defined
    errorMessage = defines(str)
    encoderDataModel = defines(DataModel, doc='''
    @rtype: DataModel
    The data model associated with the encoder.
    ''')

# --------------------------------------------------------------------

@injected
class CreateEncoderPathHandler(CreateEncoderHandler):
    '''
    Extends the model encoder with paths also.
    '''

    namePaths = 'Resources'
    # The name used for a collection of paths.
    nameRef = 'href'
    # The reference attribute name.
    nameXFilter = 'X-Filter'
    # The header name for the filter.
    nameAll = '*'
    # The name used for marking all the properties in filtering.
    separatorNames = '.'
    # Separator used for filter names.
    valueDenied = 'denied'
    # Values used to set on the x filter attribute when the fetching is denied

    def __init__(self):
        '''
        Construct the encoder.
        '''
        assert isinstance(self.namePaths, str), 'Invalid paths name %s' % self.namePaths
        assert isinstance(self.nameRef, str), 'Invalid reference name %s' % self.nameRef
        assert isinstance(self.nameXFilter, str), 'Invalid filter header name %s' % self.nameXFilter
        assert isinstance(self.nameAll, str), 'Invalid filter name all %s' % self.nameAll
        assert isinstance(self.separatorNames, str), 'Invalid names separator %s' % self.separatorNames
        assert isinstance(self.valueDenied, str), 'Invalid value denied %s' % self.valueDenied
        super().__init__()

    def process(self, request:Request, response:Response, **keyargs):
        '''
        @see: CreateEncoderHandler.process
        '''
        assert isinstance(request, Request), 'Invalid request %s' % request
        assert isinstance(response, Response), 'Invalid response %s' % response

        super().process(request, response)
        encoder = response.encoder
        if encoder is None: return
        assert isinstance(request.invoker, Invoker), 'Invalid request invoker %s' % request.invoker

        encodeModel = None
        showPath = showAccessible = showAll = True
        if isinstance(encoder, EncodeModel):
            assert isinstance(encoder, EncodeModel)
            encodeModel = encoder
            if isinstance(request.invoker.output, TypeModelProperty): showAccessible = showAll = False
            else: showPath = False
        elif isinstance(encoder, EncodeCollection):
            assert isinstance(encoder, EncodeCollection)
            exploit = encoder.exploitItem
            if isinstance(exploit, EncodeModel):
                encodeModel = exploit
                showAccessible = showAll = False

        if encodeModel is not None:
            assert isinstance(encodeModel, EncodeModel)
            data = self.createDataModel(encodeModel, request.path, showAccessible, not showAccessible)
            response.encoderDataModel = data
            response.encoderData.update(dataModel=data, encoderPath=response.encoderPath)
            assert isinstance(data, DataModel)
            if not showPath: data.flag |= NO_MODEL_PATH
        else:
            response.encoderData.update(encoderPath=response.encoderPath)
            data = None
        assert isinstance(request.decoderHeader, IDecoderHeader), 'Invalid decoder header %s' % request.decoderHeader

        value = request.decoderHeader.decode(self.nameXFilter)
        if value is not None: value = deque(val for val, _attr in value)

        error = self.processFilter(encodeModel, data, value, response.normalizer)
        if error:
            response.text, response.errorMessage = error
            response.code = INVALID_HEADER_VALUE
            return
        self.processFilterDefault(encodeModel, data, showAll)

    def createDataModel(self, encode, path, showAccessible, inCollection):
        '''
        Create the data model for the provided encode model.
        '''
        assert isinstance(encode, EncodeModel), 'Invalid encode model %s' % encode

        data = DataModel()
        if path:
            assert isinstance(path, Path), 'Invalid request path %s' % path
            data.path = path.findGetModel(encode.modelType)
            if inCollection: data.accessiblePath = data.path
            else: data.accessiblePath = path
            if showAccessible: self.processAccessible(data)

        for nameProp, encodeProp in encode.properties.items():
            if isinstance(encodeProp, EncodeModel):
                assert isinstance(encodeProp, EncodeModel)
                data.datas[nameProp] = self.createDataModel(encodeProp, path.findGetModel(encodeProp.modelType), False, False)

        return data

    def processAccessible(self, data):
        '''
        Process the accessible paths for the provided data.
        '''
        assert isinstance(data, DataModel), 'Invalid data model %s' % data

        if data.accessibleIsProcessed: return
        data.accessibleIsProcessed = True
        if data.accessiblePath is None: return
        assert isinstance(data.accessiblePath, Path), 'Invalid path %s' % data.accessiblePath

        accessible = data.accessiblePath.findGetAllAccessible()
        if accessible:
            accessible = [(pathLongName(acc), acc) for acc in accessible]
            accessible.sort(key=firstOf)
            data.accessible = OrderedDict(accessible)

    def processFilter(self, encode, data, value, normalizer):
        '''
        Process the filtering for the encoded models.
        
        @return: tuple(text, errorMessage)
            In case of error.
        '''
        if encode is None:
            if value: return 'No filter available', 'Unknown filter properties %r' % ', '.join(value)
            return

        assert isinstance(encode, EncodeModel), 'Invalid encode model %s' % encode
        assert isinstance(data, DataModel), 'Invalid data model %s' % data
        assert isinstance(normalizer, Normalizer), 'Invalid normalizer %s' % normalizer
        assert isinstance(encode.modelType, TypeModel), 'Invalid encode model type %s' % encode.modelType

        exploits = self.exploitsFor(encode, data, normalizer)
        if value is not None:
            assert isinstance(value, deque), 'Invalid value %s' % value

            cache = {}
            while value:
                fvalue = value.pop()
                if not fvalue.strip(): continue
                fencode, fdata, fexploits, reference, fcache = encode, data, exploits, encode.modelType.clazz, cache

                for isLast, name in lastCheck(fvalue.split(self.separatorNames)):
                    if name == self.nameAll and fdata:
                        if fencode is not encode:
                            if not fdata.fetchData: self.processFetch(fencode, fdata, reference, normalizer, cache)
                            fdata, fencode = fdata.fetchData, fdata.fetchEncode

                        for nameProp in fencode.modelType.container.properties:
                            if nameProp not in fexploits: self.processFetch(fencode, fdata, reference, normalizer, cache)
                            fdata.filter.add(nameProp)
                        if DataModel.accessible in fdata: fdata.filter.update(fdata.accessible)
                        fdata = None
                        continue

                    if not fdata:
                        return 'Unexpected filter entry', 'Property \'%s\' not expected in filter \'%s\'' % (name, fvalue)
                    assert isinstance(fdata, DataModel)

                    entry = fexploits.get(name)
                    if not entry:
                        if isinstance(fencode, EncodeModelProperty):
                            # We check if the property is not located in the full encoded model.
                            fdata, fexploits = self.processFetch(fencode, fdata, reference, normalizer, cache)
                            entry = fexploits.get(name)
                        elif not data.accessibleIsProcessed:
                            self.processAccessible(data)
                            fexploits = self.exploitsFor(fencode, fdata, normalizer)
                            entry = fexploits.get(name)

                    if not entry:
                        if name != fvalue:
                            return 'Unknown filter entry', 'Invalid property \'%s\' in filter \'%s\'' % (name, fvalue)
                        return 'Unknown filter entry', 'Invalid filter \'%s\'' % name

                    fname, fencode = entry
                    fdata.filter.add(fname)
                    if fdata.fetchData:
                        assert isinstance(fdata.fetchData, DataModel)
                        fdata.fetchData.filter.add(fname)

                    if not isLast and isinstance(fencode, EncodeModel):
                        assert isinstance(fencode, EncodeModel)
                        entry = fcache.get(fname)
                        if entry is None: entry = fcache[fname] = (self.exploitsFor(fencode, fdata, normalizer), {})

                        fexploits, fcache = entry
                        if DataModel.datas in fdata: fdata = fdata.datas.get(fname)
                        else: fdata = None
                        reference = getattr(reference, name)
                    else: fdata = None

    def processFilterDefault(self, encode, data, showAll):
        '''
        Process the default properties to be presented if none specified by filtering. 
        '''
        if encode is None: return
        assert isinstance(encode, EncodeModel), 'Invalid encode model %s' % encode
        assert isinstance(data, DataModel), 'Invalid data model %s' % data

        if showAll: data.filter = None
        elif DataModel.filter not in data and data.path: data.filter = frozenset()

    def processFetch(self, encode, data, reference, normalizer, cache):
        '''
        Process the fetch.
        '''
        assert isinstance(encode, EncodeModel), 'Invalid encode model %s' % encode
        assert isinstance(data, DataModel), 'Invalid data model %s' % data
        assert isinstance(normalizer, Normalizer), 'Invalid normalizer %s' % normalizer
        assert isinstance(cache, dict), 'Invalid cache %s' % cache

        exploits = cache.get(reference)
        if exploits is None:
            data.fetchReference = reference
            data.fetchEncode = mencode = self.encoderFor(encode.modelType)
            data.fetchData = mdata = self.createDataModel(mencode, data.path, True, False)
            assert isinstance(mdata, DataModel)
            exploits = cache[reference] = self.exploitsFor(mencode, mdata, normalizer)
            data = mdata
        else: data = data.fetchData

        return data, exploits

    def exploitsFor(self, encode, data, normalizer):
        '''
        Create the exploits.
        '''
        assert isinstance(encode, EncodeModel), 'Invalid encode model %s' % encode
        assert isinstance(data, DataModel), 'Invalid data model %s' % data
        assert isinstance(normalizer, Normalizer), 'Invalid normalizer %s' % normalizer

        exploits = {normalizer.normalize(name): (name, encodeProp) for name, encodeProp in encode.properties.items()}
        if DataModel.accessible in data:
            for name in data.accessible: exploits[normalizer.normalize(name)] = (name, None)
        return exploits

    # ----------------------------------------------------------------

    def encoderItem(self, ofType):
        '''
        @see: EncoderHandler.encoderItem
        '''
        assert isinstance(ofType, Type), 'Invalid type %s' % ofType

        if isinstance(ofType, TypeModel):
            assert isinstance(ofType, TypeModel)
            assert isinstance(ofType.container, Model)

            return self.nameList % ofType.container.name, \
                self.encoderModel(ofType, exploit=EncodeModel(self, ofType))
        elif ofType.isOf(Path):
            return self.namePaths, EncodePath(self.nameRef)
        return super().encoderItem(ofType)

    def encoderPrimitive(self, typeValue, getter=None):
        '''
        @see: CreateEncoderHandler.encoderPrimitive
        '''
        assert isinstance(typeValue, Type), 'Invalid property value type %s' % typeValue
        if isinstance(typeValue, TypeReference): return EncodePath(self.nameRef, getter)
        return super().encoderPrimitive(typeValue, getter=getter)

    def encoderProperty(self, ofType, getter=None, exploit=None):
        '''
        @see: EncoderHandler.encoderProperty
        '''
        assert isinstance(ofType, TypeModelProperty), 'Invalid type model property %s' % ofType

        exploit = exploit or EncodeModelProperty(self, ofType.parent, getter, ofType)
        return super().encoderProperty(ofType, getter, exploit)

    def encoderModel(self, ofType, getter=None, exploit=None, **keyargs):
        '''
        @see: EncoderHandler.encoderModel
        '''
        exploit = exploit or EncodeModel(self, ofType, getter)
        return super().encoderModel(ofType, getter, exploit)

# --------------------------------------------------------------------

class EncodeModel(EncodeObject):
    '''
    Exploit for model encoding.
    '''
    __slots__ = ('encoder', 'modelType', 'updateType')

    def __init__(self, encoder, modelType, getter=None, updateType=None):
        '''
        Create a encode exploit for a model with a path.
        @see: EncodeObject.__init__

        @param encoder: CreateEncoderPathHandler
            The encoder that created the model encode.
        @param modelType: TypeModel
            The model type of the encoded model.
        @param updateType: object
            The type to use in updating the path with the value, if not provided the modelType will be used.
        '''
        assert isinstance(encoder, CreateEncoderPathHandler), 'Invalid encoder %s' % encoder
        assert isinstance(modelType, TypeModel), 'Invalid model type %s' % modelType
        super().__init__(modelType.container.name, getter)

        self.encoder = encoder
        self.modelType = modelType
        self.updateType = updateType or modelType

    def __call__(self, value, render, normalizer, encoderPath, name=None, dataModel=None, fetcher=None, **data):
        assert isinstance(render, IRender), 'Invalid render %s' % render
        assert isinstance(normalizer, Normalizer), 'Invalid normalizer %s' % normalizer
        assert isinstance(encoderPath, IEncoderPath), 'Invalid encoder path %s' % encoderPath
        assert name is None or isinstance(name, str), 'Invalid name %s' % name

        if dataModel is None: return super().__call__(value, render, normalizer, name, **data)
        assert isinstance(dataModel, DataModel), 'Invalid data model %s' % dataModel

        if self.getter: value = self.getter(value)
        if value is None: return

        data.update(render=render, normalizer=normalizer, encoderPath=encoderPath)

        attrs = None
        if fetcher:
            assert isinstance(fetcher, IFetcher), 'Invalid fetcher %s' % fetcher
            data.update(fetcher=fetcher)
            if dataModel.fetchEncode and dataModel.fetchReference:
                valueModel = fetcher.fetch(dataModel.fetchReference, value)
                if valueModel is not None:
                    return dataModel.fetchEncode(value=valueModel, name=name, dataModel=dataModel.fetchData, **data)
                attrs = {normalizer.normalize(self.encoder.nameXFilter): self.encoder.valueDenied}

        data.update(value=value)
        if dataModel.path and not dataModel.flag & NO_MODEL_PATH:
            assert isinstance(dataModel.path, Path), 'Invalid path model %s' % dataModel.path

            dataModel.path.update(value, self.updateType)
            if dataModel.path.isValid():
                if attrs is None: attrs = {}
                attrs[normalizer.normalize(self.encoder.nameRef)] = encoderPath.encode(dataModel.path)

        render.objectStart(normalizer.normalize(name or self.name), attrs)

        for nameProp, encodeProp in self.properties.items():
            if DataModel.filter in dataModel and nameProp not in dataModel.filter: continue
            if DataModel.datas in dataModel: data.update(dataModel=dataModel.datas.get(nameProp))
            try: encodeProp(name=nameProp, **data)
            except: handleExploitError(encodeProp)

        # The accessible paths are already updated when the model path is updated.
        if DataModel.accessible in dataModel:
            for namePath, path in dataModel.accessible.items():
                if not path.isValid(): continue
                if DataModel.filter in dataModel and namePath not in dataModel.filter: continue
                attrs = {normalizer.normalize(self.encoder.nameRef):encoderPath.encode(path)}
                render.objectStart(normalizer.normalize(namePath), attrs)
                render.objectEnd()

        render.objectEnd()

class EncodeModelProperty(EncodeModel):
    '''
    Exploit for model encoding that represents only a property.
    '''
    __slots__ = ()

    def __init__(self, encoder, modelType, getter=None, updateType=None):
        '''
        Create a encode exploit for a model with a path and a single property.
        @see: EncodeModel.__init__
        '''
        super().__init__(encoder, modelType, getter, updateType)

    if __debug__:

        def __call__(self, **data):
            assert len(self.properties) <= 1, 'To many properties %s for a single property model %s' % \
            (tuple(self.properties.keys()), self.modelType)

            return super().__call__(**data)

class EncodePath:
    '''
    Exploit for path encoding.
    '''
    __slots__ = ('nameRef', 'getter')

    def __init__(self, nameRef, getter=None):
        '''
        Create a encode exploit for a path.
        
        @param nameRef: string
            The name for the reference attribute.
        @param getter: callable(object) -> object|None
            The getter used to get the path from the value object.
        '''
        assert isinstance(nameRef, str), 'Invalid reference attribute name %s' % nameRef
        assert getter is None or callable(getter), 'Invalid getter %s' % getter

        self.nameRef = nameRef
        self.getter = getter

    def __call__(self, value, render, normalizer, encoderPath, name=None, **data):
        assert isinstance(render, IRender), 'Invalid render %s' % render
        assert isinstance(normalizer, Normalizer), 'Invalid normalizer %s' % normalizer
        assert isinstance(encoderPath, IEncoderPath), 'Invalid encoder path %s' % encoderPath

        if self.getter: value = self.getter(value)
        if value is None: return

        if isinstance(value, Path):
            assert isinstance(value, Path)
            if not value.isValid(): return
            name = name or normalizer.normalize(pathLongName(value))
        else:
            assert isinstance(value, str), 'Invalid path %s' % value
        assert isinstance(name, str), 'Invalid name %s' % name

        attrs = {normalizer.normalize(self.nameRef):encoderPath.encode(value)}
        render.objectStart(name, attrs)
        render.objectEnd()
