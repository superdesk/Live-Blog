'''
Created on Jul 27, 2012

@package: ally core http
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides model encode implementations. 
'''

from ally.api.operator.type import TypeModel
from ally.core.http.spec.server import IEncoderPath
from ally.core.spec.encdec.encode import EncodeObject
from ally.core.spec.encdec.render import IRender
from ally.core.spec.resources import Normalizer, Path
import abc

# --------------------------------------------------------------------

NO_MODEL_PATH = 1 << 1
# Flag indicating that no model path should be rendered.

class DataModel:
    '''
    Contains data used for additional support in encoding the model. The data model is used by the encode model to alter
    the encoding depending on path elements and filters.
    '''
    __slots__ = ('flag', 'path', 'accessible', 'filter', 'datas', 'fetchReference', 'fetchEncode', 'fetchData')

    def __init__(self):
        '''
        Construct the data model.
        
        @ivar flag: integer
            Flag indicating several situations for the data encode.
        @ivar path: Path|None
            The path of the model.
        @ivar accessible: dictionary{string, Path}|None
            The accessible path for the encoded model.
        @ivar filter: set(string)|None
            The properties to be rendered for the model encode, this set needs to include also the accesible paths.
        @ivar datas: dictionary{string, DataModel}|None
            The data models to be used for the properties of the encoded model.
        @ivar fetchReference: Reference
            The fetch reference for the fetch encode.
        @ivar fetchEncode: EncodeModel
            The fetch encode to be used.
        @ivar fetchData: DataModel
            The fetch data model to be used.
        '''
        self.flag = 0
        self.path = None
        self.accessible = None
        self.filter = None
        self.datas = None
        self.fetchReference = None
        self.fetchEncode = None
        self.fetchData = None

class EncodeModel(EncodeObject):
    '''
    Exploit for model encoding.
    '''
    __slots__ = ('modelType', 'nameRef', 'updateType')

    def __init__(self, modelType, nameRef, getterModel=None, updateType=None):
        '''
        Create a encode exploit for a model with a path.
        @see: EncodeObject.__init__
        
        @param modelType: TypeModel
            The model type of the encoded model.
        @param nameRef: string
            The name for the reference attribute.
        @param updateType: object
            The type to use in updating the path with the value, if not provided the modelType will be used.
        '''
        assert isinstance(modelType, TypeModel), 'Invalid model type %s' % modelType
        assert isinstance(nameRef, str), 'Invalid reference attribute name %s' % nameRef
        super().__init__(modelType.container.name, getterModel)

        self.nameRef = nameRef
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

        if fetcher:
            assert isinstance(fetcher, IFetcher), 'Invalid fetcher %s' % fetcher
            data.update(fetcher=fetcher)
            if dataModel.fetchEncode and dataModel.fetchReference:
                valueModel = fetcher.fetch(dataModel.fetchReference, value)
                if valueModel is not None:
                    return dataModel.fetchEncode(value=valueModel, name=name, dataModel=dataModel.fetchData, **data)

        data.update(value=value)

        attrs = None
        if dataModel.path and not dataModel.flag & NO_MODEL_PATH:
            assert isinstance(dataModel.path, Path), 'Invalid path model %s' % dataModel.path

            dataModel.path.update(value, self.updateType)
            if dataModel.path.isValid(): attrs = {normalizer.normalize(self.nameRef): encoderPath.encode(dataModel.path)}

        render.objectStart(name or normalizer.normalize(self.name), attrs)

        for nameProp, encodeProp in self.properties.items():
            if dataModel.filter is not None and nameProp not in dataModel.filter: continue
            if dataModel.datas: data.update(dataModel=dataModel.datas.get(nameProp))
            encodeProp(name=normalizer.normalize(nameProp), **data)

        # The accessible paths are already updated when the model path is updated.
        if dataModel.accessible:
            for namePath, path in dataModel.accessible.items():
                if not path.isValid(): continue
                if dataModel.filter is not None and namePath not in dataModel.filter: continue
                attrs = {normalizer.normalize(self.nameRef):encoderPath.encode(path)}
                render.objectStart(normalizer.normalize(namePath), attrs)
                render.objectEnd()

        render.objectEnd()

# --------------------------------------------------------------------

class IFetcher(metaclass=abc.ABCMeta):
    '''
    Specification for model fetching.
    '''
    __slots__ = ()

    @abc.abstractclassmethod
    def fetch(self, reference, valueId):
        '''
        Fetch the model object that is specific for the provided reference.
        
        @param reference: Reference
            The reference of the model object to fetch.
        @param valueId: object
            The value id for the model object to fetch.
        @return: object|None
            The model object corresponding to the reference and value id, None if the object cannot be provided.
        '''
