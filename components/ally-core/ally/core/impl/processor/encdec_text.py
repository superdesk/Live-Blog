'''
Created on Jan 25, 2012

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the basic text encoding/decoding processor handler.
'''


from ally.api.operator import Model, Property
from ally.api.type import TypeModel, TypeNone, Iter, TypeProperty
from ally.container.ioc import injected
from ally.core.impl.node import NodePath
from ally.core.spec.resources import Normalizer, Converter, ResourcesManager, \
    Path
from ally.core.spec.server import Processor, Request, Response, ProcessorsChain, \
    EncoderPath
from ally.support.api.util_type import isTypeId, isPropertyTypeId, \
    isPropertyTypeIntId, isTypeIntId
from io import TextIOWrapper
from numbers import Number
import logging

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

@injected
class EncodingTextHandler(Processor):
    '''
    Provides the text base encoding.
    
    Provides on request: NA
    Provides on response: the content response
    
    Requires on request: resourcePath
    Requires on response: contentType, encoderPath, contentConverter, obj, objType, [contentLocation]
    '''
    
    resourcesManager = ResourcesManager
    # The resources manager used in locating the resource nodes for the id's presented.
    normalizer = Normalizer
    # The normalizer used by the encoding for the XML tag names.
    converterId = Converter
    # The converter to use on the id's of the models.
    nameResources = 'Resources'
    # The name to be used as the main container for the resources.
    namePath = 'href'
    # The name to use as the attribute in rendering the hyper link.
    nameList = '%sList'
    # The name to use for rendering lists.

    def __init__(self):
        assert isinstance(self.resourcesManager, ResourcesManager), \
        'Invalid resources manager %s' % self.resourcesManager
        assert isinstance(self.normalizer, Normalizer), 'Invalid Normalizer object %s' % self.normalizer
        assert isinstance(self.converterId, Converter), 'Invalid Converter object %s' % self.converterId
        assert isinstance(self.nameResources, str), 'Invalid name resources %s' % self.nameResources
        assert isinstance(self.namePath, str), 'Invalid name path %s' % self.namePath
        assert isinstance(self.nameList, str), 'Invalid name list %s' % self.nameList
    
    def process(self, req, rsp, chain):
        '''
        @see: Processor.process
        '''
        assert isinstance(req, Request), 'Invalid request %s' % req
        assert isinstance(rsp, Response), 'Invalid response %s' % rsp
        assert isinstance(chain, ProcessorsChain), 'Invalid processors chain %s' % chain
        
        if not rsp.objType:
            if isinstance(rsp.obj, dict):
                # Expecting a plain dictionary dictionary or list for rendering
                assert isValid(rsp.obj), 'Invalid object %s' % rsp.obj
                obj = rsp.obj
            else:
                assert log.debug('Nothing to encode') or True
                return
        elif rsp.encoderPath and rsp.contentConverter:
            assert isinstance(rsp.contentConverter, Converter), 'Invalid content converter %s' % rsp.contentConverter
            assert isinstance(rsp.encoderPath, EncoderPath), 'Invalid encoder path %s' % rsp.encoderPath
            asString, pathEncode = rsp.contentConverter.asString, rsp.encoderPath.encode
            if rsp.contentLocation: 
                obj = {self.normalizer.normalize(self.attrPath):pathEncode(rsp.contentLocation)}
            else:
                obj = self.convert(rsp.obj, rsp.objType, asString, pathEncode, rsp.objInclude, rsp.objExclude,
                                   req.resourcePath)
        if obj:
            #txt = TextIOWrapper(rsp.dispatch(), self._getCharSet(req, rsp), self.encodingError)
            print(obj)
            return
        
        chain.process(req, rsp)
        
    # ----------------------------------------------------------------
    
    def convert(self, value, vtype, asString, pathEncode, objInclude=None, objExclude=None, resourcePath=None):
        '''
        Converts the provided value to a text object.
        
        @param value: object
            The value object to be converter to text object.
        @param vtype: object
            The type of the object to convert.
        @param asString: Callable
            The call used converting values to string values.
        @param pathEncode: Callable
            The call used for encoding the path.
        @param objInclude: list[string]|tuple(string)|None
            The list of names to be included in the text object, the include list has priority over object exclude.
        @param objExclude: list[string]|tuple(string)|None
            The list of names to be excluded from the rendered text object.
        @param resourcePath: Path|None
            The resource path from where the value originated.
        @return: dictionary(string, dictionary{string, ...}}
            The text object.
        '''
        if isinstance(vtype, Iter):
            assert isinstance(vtype, Iter)
            itype = vtype.itemType
            if not itype:
                assert log.debug('There is no type for list item ') or True
            elif itype.isOf(Path):
                return self.convertListPath(value, pathEncode)
            elif isPropertyTypeId(itype):
                assert isinstance(itype, TypeProperty)
                if resourcePath: path = self.resourcesManager.findGetModel(resourcePath, itype.model)
                else: path = None
                return self.convertListProperty(value, itype, asString, pathEncode, path)
            elif isinstance(itype, TypeProperty):
                return self.convertListProperty(value, itype, asString, pathEncode)
            elif isinstance(itype, TypeModel):
                assert isinstance(itype, TypeModel)
                propPaths, paths = self.modelPaths(value, itype.model, resourcePath)
                return self.convertListModels(value, itype.model, asString, pathEncode, objInclude, propPaths, paths)
            else:
                assert log.debug('Cannot encode list item object type %r', itype) or True
        elif isinstance(vtype, TypeNone):
            assert log.debug('Nothing to encode') or True
        elif isinstance(vtype, TypeProperty):
            if isPropertyTypeId(vtype) and resourcePath:
                assert isinstance(vtype, TypeProperty)
                path = self.resourcesManager.findGetModel(resourcePath, vtype.model)
            else: path = None
            return self.convertProperty(value, vtype, asString, pathEncode, path)
        elif isinstance(vtype, TypeModel):
            assert isinstance(vtype, TypeModel)
            propPaths, paths = self.modelPaths(value, vtype.model, resourcePath)
            return self.convertModel(value, vtype.model, asString, pathEncode, objExclude, objInclude, propPaths, paths)
        else:
            assert log.debug('Cannot encode object type %r', vtype) or True
    
    def convertProperty(self, value, tprop, asString, pathEncode, path=None):
        '''
        Converts the provided property to a text object.
        
        @param value: object
            The property value.
        @param tprop: TypeProperty
            The type property of the value.
        @param asString: Callable
            The call used converting values to string values.
        @param pathEncode: Callable
            The call used for encoding the path.
        @param path: Path|None
            The reference path of the property value.
        @return: dictionary(string, string}
            The text object.
        '''
        assert isinstance(tprop, TypeProperty), 'Invalid type property %s' % tprop
        assert callable(asString), 'Invalid as string converter %s' % asString
        assert callable(pathEncode), 'Invalid path encoder %s' % pathEncode
        
        normalize = self.normalizer.normalize
        
        obj = {normalize(tprop.property.name):
               self.converterId.asString(value, tprop) if isPropertyTypeIntId(tprop) else asString(value, tprop)}
        if path is not None:
            assert isinstance(path, Path), 'Invalid path %s' % path
            path.update(value, tprop)
            obj[normalize(self.namePath)] = pathEncode(path)
        return obj
    
    def convertProperties(self, modelObject, properties, asString, pathEncode, propertiesPaths=None, paths=None):
        '''
        Converts the provided properties to a text object.
        
        @param modelObject: object
            The properties model instance.
        @param properties: list[Property]|tuple(Property)
            The properties to convert the values for.
        @param asString: Callable
            The call used converting values to string values.
        @param pathEncode: Callable
            The call used for encoding the path.
        @param propertiesPaths: dictionary{string, Path}|None
            The reference paths of the properties.
        @param paths: list[Path]|tuple(Path)
            Additional resources paths to be included in the properties text object.
        @return: dictionary(string, dictionary{string, ...}}
            The text object.
        '''
        assert modelObject is not None, 'A model object is required'
        assert isinstance(properties, (list, tuple)), 'Invalid properties %s' % properties
        assert callable(asString), 'Invalid as string converter %s' % asString
        assert callable(pathEncode), 'Invalid path encoder %s' % pathEncode
        assert not propertiesPaths or isinstance(propertiesPaths, dict), 'Invalid properties paths %s' % propertiesPaths
        assert properties or paths, 'Nothing to convert, there are no properties or paths' 
        
        normalize, namePath, converterId = self.normalizer.normalize, self.namePath, self.converterId.asString
        
        obj = {}
        for prop in properties:
            assert isinstance(prop, Property), 'Invalid property %s' % prop
            value = prop.get(modelObject)
            typ = prop.type
            if value is not None:
                if isTypeIntId(typ) or isPropertyTypeIntId(typ): value = converterId(value, typ)
                else: value = asString(value, typ)
                    
                path = propertiesPaths.get(prop.name) if propertiesPaths else None
                if path:
                    path.update(value, typ)
                    value = {normalize(prop.name):value, namePath:pathEncode(path)}

                obj[normalize(prop.name)] = value
        if paths:
            assert isinstance(paths, (list, tuple)), 'Invalid paths %s' % paths
            if __debug__:
                for path in paths:
                    assert isinstance(path, Path), 'Invalid path %s' % path
                    assert isinstance(path.node, NodePath), \
                    'Invalid path, it suppose to have a node path %s' % path.node
            obj.update({path.node.nameLong():{namePath:pathEncode(path)} for path in paths})
        return obj
    
    def convertModel(self, modelObject, model, asString, pathEncode, objExclude=None, objInclude=None,
                     propertiesPaths=None, paths=None):
        '''
        Converts the provided model object to a text object.
        
        @param modelObject: object
            The properties model instance.
        @param model: Model
            The model of the object to convert.
        @param asString: Callable
            The call used converting values to string values.
        @param pathEncode: Callable
            The call used for encoding the path.
        @param objExclude: list[string]|tuple(string)|None
            The list of names to be excluded from the rendered text object.
        @param objInclude: list[string]|tuple(string)|None
            The list of names to be included in the text object, the include list has priority over object exclude.
        @param propertiesPaths: dictionary{string, Path}|None
            The reference paths of the properties.
        @param paths: list[Path]|tuple(Path)
            Additional resources paths to be included in the properties text object.
        @return: dictionary(string, dictionary{string, ...}}
            The text object.
        '''
        assert modelObject is not None, 'A model object is required'
        assert isinstance(model, Model), 'Invalid model %s' % model
        assert callable(asString), 'Invalid as string converter %s' % asString
        assert callable(pathEncode), 'Invalid path encoder %s' % pathEncode
        assert not propertiesPaths or isinstance(propertiesPaths, dict), 'Invalid properties paths %s' % propertiesPaths

        if paths:
            assert isinstance(paths, (list, tuple)), 'Invalid paths %s' % paths
            if __debug__:
                for path in paths:
                    assert isinstance(path, Path), 'Invalid path %s' % path
                    assert isinstance(path.node, NodePath), \
                    'Invalid path, it suppose to have a node path %s' % path.node
        
        if objInclude:
            assert isinstance(objInclude, (list, tuple)), 'Invalid object include %s' % objInclude
            properties = [prop for name, prop in model.properties.items() if name in objInclude]
            if paths: paths = [path for path in paths if path.node.nameLong() in objInclude]
        elif objExclude:
            assert isinstance(objExclude, (list, tuple)), 'Invalid object exclude %s' % objExclude
            properties = [prop for name, prop in model.properties.items() if name not in objExclude]
            if paths: paths = [path for path in paths if path.node.nameLong() not in objExclude]
        else: properties = list(model.properties.values())

        obj = self.convertProperties(modelObject, properties, asString, pathEncode, propertiesPaths, paths)
        
        return {self.normalizer.normalize(model.name):obj}
   
    def convertListPath(self, paths, pathEncode):
        '''
        Converts the provided paths to a text object.
        
        @param paths: list[Path]|tuple(Path)
            The paths to be converted.
        @param pathEncode: Callable
            The call used for encoding the path.
        @return: dictionary(string, dictionary{string, string}}
            The text object.
        '''
        assert isinstance(paths, (list, tuple)), 'Invalid paths %s' % paths
        assert callable(pathEncode), 'Invalid path encoder %s' % pathEncode
        if __debug__:
            for path in paths:
                assert isinstance(path, Path), 'Invalid path %s' % path 
                assert isinstance(path.node, NodePath), 'Invalid path, it suppose to have a node path %s' % path.node 
        
        namePath = self.namePath
        return {
                self.normalizer.normalize(self.nameResources):
                {path.node.nameLong():{namePath:pathEncode(path)} for path in paths}
                }

    def convertListProperty(self, values, tprop, asString, pathEncode, path=None):
        '''
        Converts the provided list of property values to a text object.
        
        @param values: list[object]|tuple(object)
            The property values to convert.
        @param tprop: TypeProperty
            The type property of the values.
        @param asString: Callable
            The call used converting values to string values.
        @param pathEncode: Callable
            The call used for encoding the path.
        @param path: Path|None
            The reference path of the property value.
        @return: dictionary(string, string}
            The text object.
        '''
        assert isinstance(values, (list, tuple)), 'Invalid values %s' % values
        assert isinstance(tprop, TypeProperty), 'Invalid type property %s' % tprop
        
        convert = self.convertProperty
        return {self.normalizer.normalize(self.nameList % tprop.model.name):
                [convert(value, tprop, asString, pathEncode, path) for value in values]
                }
        
    def convertListModels(self, modelObjects, model, asString, pathEncode, objInclude=None, propertiesPaths=None,
                          paths=None):
        '''
        Converts the provided models objects to a text object.
        
        @param modelObjects: Iterable[object]
            The model object to be converter to text object.
        @param model: Model
            The model of the objects to convert.
        @param asString: Callable
            The call used converting values to string values.
        @param pathEncode: Callable
            The call used for encoding the path.
        @param objInclude: list[string]|tuple(string)|None
            The list of names to be included in the text object, the include list has priority over object exclude.
        @param objExclude: list[string]|tuple(string)|None
            The list of names to be excluded from the rendered text object.
        @param propertiesPaths: dictionary{string, Path}|None
            The reference paths of the properties.
        @param paths: list[Path]|tuple(Path)
            Additional resources paths to be included in the properties text object.
        @return: dictionary(string, dictionary{string, ...}}
            The text object.
        '''
        assert modelObjects is not None, 'The model objects are required'
        assert isinstance(model, Model), 'Invalid model %s' % model
        assert callable(asString), 'Invalid as string converter %s' % asString
        assert callable(pathEncode), 'Invalid path encoder %s' % pathEncode
        assert not propertiesPaths or isinstance(propertiesPaths, dict), 'Invalid properties paths %s' % propertiesPaths

        if paths:
            assert isinstance(paths, (list, tuple)), 'Invalid paths %s' % paths
            if __debug__:
                for path in paths:
                    assert isinstance(path, Path), 'Invalid path %s' % path
                    assert isinstance(path.node, NodePath), \
                    'Invalid path, it suppose to have a node path %s' % path.node
                    
        normalize = self.normalizer.normalize
        
        if objInclude:
            assert isinstance(objInclude, (list, tuple)), 'Invalid object include %s' % objInclude
            properties = [prop for name, prop in model.properties.items() if name in objInclude]
            if paths: paths = [path for path in paths if path.node.nameLong() in objInclude]
        else:
            for prop in model.properties.values():
                assert isinstance(prop, Property), 'Invalid property %s' % prop
                if isTypeId(prop.type) and prop.name in propertiesPaths:
                    path = propertiesPaths[prop.name]
                    assert isinstance(path, Path), 'Invalid path %s' % path
                    namePath = self.namePath
                    references = []
                    for modelObject in modelObjects:
                        path.update(modelObject, model)
                        references.append({namePath:pathEncode(path)})
                    return {normalize(self.nameList % model.name):references}
            properties = list(model.properties.values())
        
        if len(properties) == 1:
            prop = properties[0]
            assert isinstance(prop, Property), 'Invalid property %s' % prop
            path = propertiesPaths.get(prop.name) if propertiesPaths else None
            return self.convertListProperty((prop.get(modelObject) for modelObject in modelObjects),
                                            TypeProperty(model, prop), asString, pathEncode, path)

        convert = self.convertProperties
        return {
                normalize(self.nameList % model.name):
                [convert(modelObject, properties, asString, pathEncode, propertiesPaths, paths) 
                 for modelObject in modelObjects]
                }
        
    # ----------------------------------------------------------------
    
    def modelPaths(self, modelObject, model, resourcePath=None):
        '''
        Provides the model properties paths and additional resource paths.
        
        @param modelObject: object
            The model instance.
        @param model: Model
            The model of the object to provide the resource paths.
        @param resourcePath: Path|None
            The resource path where the model object has originated.
        @return: tuple(dictionary{string, Path}, list[Path])
            A tuple contains on the first position the model's properties paths, and on the second position a list of
            additional resource paths for the model.
        '''
        assert modelObject is not None, 'A model object is required'
        assert isinstance(model, Model), 'Invalid model %s' % model
        if resourcePath:
            propertiesPaths = self.resourcesManager.findGetModelProperties(resourcePath, model)
            paths = self.resourcesManager.findGetAllAccessible(resourcePath)
        else:
            paths = None
            propertiesPaths = None
        mPaths = self.resourcesManager.findGetAccessibleByModel(model, modelObject)
        if paths: paths.extend([path for path in mPaths if path not in paths])
        else: paths = mPaths
        
        return propertiesPaths, paths
                
# --------------------------------------------------------------------

def isValid(obj):
    '''
    Checks if the provided object is valid as a text object.
    
    @param obj: dictionary(string, string|list[string]|dictionary{string, ...}}
        The object to be checked.
    @return: boolean
        true if the object is valid, False otherwise.
    '''
    if not isinstance(obj, dict): return False
    for key, value in obj.items():
        if not isinstance(key, (str, Number)): return False
        if isinstance(value, list):
            for ele in value:
                if not isinstance(ele, (str, Number)) and not isValid(ele): return False
        elif not isinstance(value, (str, Number)) and not isValid(value) :return False
    return True
