'''
Created on Jan 25, 2012

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the text encoding/decoding processor handler.
'''

from ally.api.operator import Model, Property
from ally.api.type import TypeModel, TypeNone, Iter, TypeProperty
from ally.container.ioc import injected
from ally.core.impl.node import NodePath
from ally.core.spec.codes import UNKNOWN_ENCODING
from ally.core.spec.resources import Normalizer, Converter, ResourcesManager, \
    Path
from ally.core.spec.server import Processor, Request, Response, ProcessorsChain, \
    EncoderPath
from ally.exception import DevelException
from ally.support.api.util_type import isTypeId, isPropertyTypeId, \
    isPropertyTypeIntId
from collections import Iterable, OrderedDict
from io import TextIOWrapper
from numbers import Number
import codecs
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
    charSetDefault = str
    # The default character set to be used if none provided for the content.
    encoders = list
    # A list[tuple(dictionary{string:string}, Callable(object, file writer, string))] containing tuples of two. On the 
    # first position has the dictionary{string:string} containing as a key the content types specific for this encoder 
    # and as a value the content type to set on the response, if None will use the key for the content type response. 
    # On the second position contains a Callable(object, file writer, string)) function that takes as the first argument
    # the text object to be encoded, the second the text file writer to dump to the encoded text and on the last position
    # the character set encoding used.
    nameResources = 'Resources'
    # The name to be used as the main container for the resources.
    namePath = 'href'
    # The name to use as the attribute in rendering the hyper link.

    def __init__(self):
        assert isinstance(self.resourcesManager, ResourcesManager), \
        'Invalid resources manager %s' % self.resourcesManager
        assert isinstance(self.normalizer, Normalizer), 'Invalid Normalizer object %s' % self.normalizer
        assert isinstance(self.converterId, Converter), 'Invalid Converter object %s' % self.converterId
        assert isinstance(self.charSetDefault, str), 'Invalid default character set %s' % self.charSetDefault
        assert isinstance(self.nameResources, str), 'Invalid name resources %s' % self.nameResources
        assert isinstance(self.encoders, list), 'Invalid encoders %s' % self.encoders
        assert isinstance(self.namePath, str), 'Invalid name path %s' % self.namePath
    
    def process(self, req, rsp, chain):
        '''
        @see: Processor.process
        '''
        assert isinstance(req, Request), 'Invalid request %s' % req
        assert isinstance(rsp, Response), 'Invalid response %s' % rsp
        assert isinstance(chain, ProcessorsChain), 'Invalid processors chain %s' % chain
        
        if rsp.contentType:
            contentType = rsp.contentType
            for contentTypes, encoder in self.encoders:
                if contentType in contentTypes: break
            else:
                rsp.setCode(UNKNOWN_ENCODING, 'Content type %r not supported for encoding' % rsp.contentType)
                return
        else:
            for contentType in req.accContentTypes:
                for contentTypes, encoder in self.encoders:
                    if contentType in contentTypes:
                        rsp.contentType = contentType
                        break
                else: continue
                break
            else:
                # Checking for None in case some encoder is configured as default.
                for contentTypes, encoder in self.encoders:
                    if None in contentTypes:
                        contentType = None
                        break
                else:
                    rsp.setCode(UNKNOWN_ENCODING, 'Accepted content types %r not supported for encoding' % 
                                ', '.join(req.accContentTypes))
                    return
        
        contentTypeNormalized = contentTypes[contentType]
        if contentTypeNormalized:
            assert log.debug('Normalized content type %r to %r', contentType, contentTypeNormalized) or True
            rsp.contentType = contentTypeNormalized
        
        if not rsp.objType:
            if isinstance(rsp.obj, dict):
                # Expecting a plain dictionary dictionary or list for rendering
                assert isValid(rsp.obj), 'Invalid object %s' % rsp.obj
                obj = rsp.obj
            else:
                assert log.debug('Nothing to encode') or True
                return
        else:
            if not rsp.encoderPath:
                assert log.debug('There is no path encoder on the response, no paths will be rendered') or True
                def noPathEncode(*args): raise DevelException('There is no path encoder on the response')
                pathEncode = noPathEncode
            else:
                assert isinstance(rsp.encoderPath, EncoderPath), 'Invalid encoder path %s' % rsp.encoderPath
                pathEncode = rsp.encoderPath.encode
                
            assert isinstance(rsp.contentConverter, Converter), 'Invalid content converter %s' % rsp.contentConverter
            asString = rsp.contentConverter.asString
            
            if rsp.contentLocation: 
                obj = {self.normalizer.normalize(self.attrPath):pathEncode(rsp.contentLocation)}
            else:
                obj = self.convert(rsp.obj, rsp.objType, asString, pathEncode, rsp.objInclude, rsp.objExclude,
                                   req.resourcePath)
                
        if obj:
            # Resolving the character set
            if rsp.charSet:
                try: codecs.lookup(rsp.charSet)
                except LookupError: rsp.charSet = None
            if not rsp.charSet:
                for charSet in req.accCharSets:
                    try: codecs.lookup(charSet)
                    except LookupError: continue
                    rsp.charSet = charSet
                    break
                else: rsp.charSet = self.charSetDefault
                
            encoder(obj, TextIOWrapper(rsp.dispatch(), rsp.charSet), rsp.charSet)
        
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
            elif isinstance(itype, TypeProperty):
                assert isinstance(itype, TypeProperty)
                if resourcePath and isPropertyTypeId(itype):
                    path = self.resourcesManager.findGetModel(resourcePath, itype.model)
                else: path = None
                return self.convertListProperty(value, itype, asString, pathEncode, path)
            elif isinstance(itype, TypeModel):
                assert isinstance(itype, TypeModel)
                if resourcePath:
                    pathsProp = self.resourcesManager.findGetModelProperties(resourcePath, itype.model)
                    path = self.resourcesManager.findGetModel(resourcePath, itype.model)
                    if path:
                        assert isinstance(itype.model, Model)
                        idName = [name for name, prop in itype.model.properties.items() if isTypeId(prop.type)]
                        if len(idName) == 1: pathsProp[idName[0]] = path
                else:
                    pathsProp = None
                    path = None
                return self.convertListModels(value, itype.model, asString, pathEncode, objInclude, pathsProp, path)
            else:
                assert log.debug('Cannot encode list item object type %r', itype) or True
        elif isinstance(vtype, TypeNone):
            assert log.debug('Nothing to encode') or True
        elif isinstance(vtype, TypeProperty):
            assert isinstance(vtype, TypeProperty)
            if resourcePath and isPropertyTypeId(vtype):
                path = self.resourcesManager.findGetModel(resourcePath, vtype.model)
            else: path = None
            return self.convertProperty(value, vtype, asString, pathEncode, path)
        elif isinstance(vtype, TypeModel):
            assert isinstance(vtype, TypeModel)
            if resourcePath:
                pathsProp = self.resourcesManager.findGetModelProperties(resourcePath, vtype.model)
                paths = self.resourcesManager.findGetAllAccessible(resourcePath)
            else:
                paths = None
                pathsProp = None
            pathsModel = self.resourcesManager.findGetAccessibleByModel(vtype.model, value)
            if paths: paths.extend([path for path in pathsModel if path not in paths])
            else: paths = pathsModel
            return self.convertModel(value, vtype.model, asString, pathEncode, objExclude, objInclude, pathsProp, paths)
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
    
    def convertProperties(self, modelObject, model, properties, asString, pathEncode, propertiesPaths=None, paths=None):
        '''
        Converts the provided properties to a text object.
        
        @param modelObject: object
            The properties model instance.
        @param model: Model
            The model of the properties to convert the values for.
        @param properties: list[string]|tuple(string)
            The properties names to convert the values for.
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
        assert isinstance(model, Model), 'Invalid model %s' % model
        assert isinstance(properties, (list, tuple)), 'Invalid properties %s' % properties
        assert callable(asString), 'Invalid as string converter %s' % asString
        assert callable(pathEncode), 'Invalid path encoder %s' % pathEncode
        assert not propertiesPaths or isinstance(propertiesPaths, dict), 'Invalid properties paths %s' % propertiesPaths
        assert properties or paths, 'Nothing to convert, there are no properties or paths' 
        
        normalize, namePath, converterId = self.normalizer.normalize, self.namePath, self.converterId.asString
        
        obj = OrderedDict()
        for name in properties:
            assert isinstance(name, str), 'Invalid property name %s' % name
            prop = model.properties[name]
            assert isinstance(prop, Property)
            
            if isinstance(prop.type, TypeProperty): typeProp = prop.type
            else: typeProp = model.typeProperties[name]
            assert isinstance(typeProp, TypeProperty)
            
            value = prop.get(modelObject)
            
            if value is not None:
                path = propertiesPaths.get(name) if propertiesPaths else None
                
                if isPropertyTypeIntId(typeProp): value = converterId(value, typeProp)
                else: value = asString(value, typeProp)
                    
                path = propertiesPaths.get(name) if propertiesPaths else None
                if path:
                    assert isinstance(path, Path)
                    path.update(value, typeProp)
                    value = {normalize(typeProp.property.name):value, namePath:pathEncode(path)}

                obj[normalize(name)] = value
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
            properties = [name for name in model.properties if name in objInclude]
            if paths: paths = [path for path in paths if path.node.nameLong() in objInclude]
        elif objExclude:
            assert isinstance(objExclude, (list, tuple)), 'Invalid object exclude %s' % objExclude
            properties = [name for name in model.properties if name not in objExclude]
            if paths: paths = [path for path in paths if path.node.nameLong() not in objExclude]
        else: properties = list(model.properties)

        obj = self.convertProperties(modelObject, model, properties, asString, pathEncode, propertiesPaths, paths)
        
        return {self.normalizer.normalize(model.name):obj}
   
    def convertListPath(self, paths, pathEncode):
        '''
        Converts the provided paths to a text object.
        
        @param paths: Iterable[Path]
            The paths to be converted.
        @param pathEncode: Callable
            The call used for encoding the path.
        @return: dictionary(string, dictionary{string, string}}
            The text object.
        '''
        assert isinstance(paths, Iterable), 'Invalid paths %s' % paths
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
        
        @param values: Iterable[object]
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
        assert isinstance(values, Iterable), 'Invalid values %s' % values
        assert isinstance(tprop, TypeProperty), 'Invalid type property %s' % tprop
        
        convert = self.convertProperty
        return {self.normalizer.normalize(tprop.model.name):
                [convert(value, tprop, asString, pathEncode, path) for value in values]
                }
        
    def convertListModels(self, modelObjects, model, asString, pathEncode, objInclude=None, propertiesPaths=None,
                          path=None):
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
        @param path: Path|None
            The reference path of the model.
        @return: dictionary(string, dictionary{string, ...}}
            The text object.
        '''
        assert isinstance(modelObjects, Iterable), 'Invalid model objects %s' % modelObjects
        assert isinstance(model, Model), 'Invalid model %s' % model
        assert callable(asString), 'Invalid as string converter %s' % asString
        assert callable(pathEncode), 'Invalid path encoder %s' % pathEncode
        assert not propertiesPaths or isinstance(propertiesPaths, dict), 'Invalid properties paths %s' % propertiesPaths

        normalize = self.normalizer.normalize
        
        if objInclude:
            assert isinstance(objInclude, (list, tuple)), 'Invalid object include %s' % objInclude
            properties = [name for name in model.properties if name in objInclude]
        elif path:
            assert isinstance(path, Path), 'Invalid path %s' % path
            namePath = self.namePath
            references = []
            for modelObject in modelObjects:
                path.update(modelObject, model)
                references.append({namePath:pathEncode(path)})
            return {normalize(model.name):references}
        else:
            properties = list(model.properties)
        
        if len(properties) == 1:
            name = properties[0]
            prop = model.properties[name]
            typeProp = model.typeProperties[name]
            assert isinstance(prop, Property), 'Invalid property %s' % prop
            pathProp = propertiesPaths.get(name) if propertiesPaths else None
            return self.convertListProperty((prop.get(modelObject) for modelObject in modelObjects),
                                            typeProp, asString, pathEncode, pathProp)
        
        convert = self.convertProperties
        return {
                normalize(model.name):
                [convert(modelObject, model, properties, asString, pathEncode, propertiesPaths)
                 for modelObject in modelObjects]
                }
        
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
