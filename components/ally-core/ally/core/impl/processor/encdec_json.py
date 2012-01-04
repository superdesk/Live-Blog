'''
Created on Jul 11, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the JSON encoding handler.
'''

from _pyio import TextIOWrapper
from ally import internationalization
from ally.api.operator import Model, Property, INSERT, UPDATE
from ally.api.type import TypeProperty, Iter, TypeModel, TypeNone
from ally.core.impl.node import NodePath
from ally.core.impl.processor.encdec_base import EncodingBaseHandler, \
    DecodingBaseHandler, findLastModel
from ally.core.impl.util_type import isPropertyTypeId, isPropertyTypeIntId, \
    isTypeIntId, pathsFor
from ally.core.spec.codes import BAD_CONTENT
from ally.core.spec.resources import Path, Converter
from ally.core.spec.server import Request, Response, ProcessorsChain, \
    ContentRequest
from ally.exception import DevelException, InputException, Ref
from ally.ioc import injected
import codecs
import json
import logging

# --------------------------------------------------------------------

log = logging.getLogger(__name__)
_ = internationalization.translator(__name__)

# --------------------------------------------------------------------

@injected
class EncodingJSONHandler(EncodingBaseHandler):
    '''
    Provides the JSON encoding.
    '''

    def __init__(self):
        super().__init__()
        
    def process(self, req, rsp, chain):
        '''
        @see: Processor.process
        '''
        assert isinstance(req, Request), 'Invalid request %s' % req
        assert isinstance(rsp, Response), 'Invalid response %s' % rsp
        assert isinstance(chain, ProcessorsChain), 'Invalid processors chain %s' % chain
        if self._processResponse(rsp):
            obj = None
            if not rsp.objType and isinstance(rsp.obj, dict):
                # Expecting a plain dictionary dictionary or list for rendering
                obj = rsp.obj

            elif rsp.encoderPath:
                if rsp.contentLocation:
                    obj = {self.normalizer.normalize(self.attrPath):rsp.encoderPath.encode(rsp.contentLocation)}
                else:
                    typ = rsp.objType
                    if typ is None or isinstance(typ, TypeNone):
                        assert log.debug('Nothing to encode') or True
                        return
                    if isinstance(typ, Iter):
                        assert isinstance(typ, Iter)
                        if typ.isOf(Path):
                            obj = self._convertListPath(rsp.obj, rsp)
                        elif isPropertyTypeId(typ.itemType):
                            obj = self._convertListIds(rsp.obj, typ.itemType, req.resourcePath, rsp)
                        elif isinstance(typ.itemType, TypeProperty):
                            obj = self._convertListProperty(rsp.obj, typ.itemType, rsp)
                        elif isinstance(typ.itemType, TypeModel):
                            self._processObjectInclude(typ.itemType.model, rsp)
                            obj = self._convertListModels(rsp.obj, typ.itemType.model, req.resourcePath, rsp)
                        else:
                            assert log.debug('Cannot encode list item object type %r', typ.itemType) or True
                    elif isinstance(typ, TypeProperty):
                        if isPropertyTypeId(typ):
                            path = self.resourcesManager.findGetModel(req.resourcePath, typ.model)
                        else: path = None
                        obj = self._convertProperty(rsp.obj, path, typ, rsp)
                    elif isinstance(typ, TypeModel):
                        obj = self._convertModel(rsp.obj, typ.model, req.resourcePath, rsp)
                    else:
                        assert log.debug('Cannot encode object type %r', typ) or True
            if obj:
                txt = TextIOWrapper(rsp.dispatch(), self._getCharSet(req, rsp), self.encodingError)
                # Need to stop the text close since this will close the socket, just a small hack to prevent this.
                txt.close = None
                json.dump(obj, txt)
                return
        chain.process(req, rsp)

    def _appendPath(self, pathsObj, path, rsp, fullName=False, pathName=None):
        assert isinstance(path, Path), 'Invalid path %s' % path
        assert isinstance(rsp, Response)
        if not pathName:
            node = path.node
            assert isinstance(node, NodePath)
            if fullName:
                pathName = ''
                while node is not None and isinstance(node, NodePath):
                    pathName = node.name + pathName
                    node = node.parent
            else:
                pathName = node.name
            pathName = self.normalizer.normalize(pathName)
        pathsObj[pathName] = {self.attrPath:rsp.encoderPath.encode(path)}

    def _convertListPath(self, paths, rsp):
        pathsObj = {}
        for path in paths:
            self._appendPath(pathsObj, path, rsp, True)
        return {self.normalizer.normalize(self.tagResources):pathsObj}
    
    def _convertProperty(self, value, path, typProp, rsp):
        assert isinstance(rsp, Response)
        assert isinstance(rsp.contentConverter, Converter)
        if isPropertyTypeIntId(typProp):
            value = self.converterId.asString(value, typProp)
        else:
            value = rsp.contentConverter.asString(value, typProp)
        idObj = {self.normalizer.normalize(typProp.property.name):value}
        if path is not None:
            assert isinstance(path, Path)
            path.update(value, typProp)
            idObj[self.normalizer.normalize(self.attrPath)] = rsp.encoderPath.encode(path)
        return idObj
    
    def _convertProperties(self, obj, properties, paths, rsp):
        assert isinstance(rsp, Response)
        assert isinstance(rsp.contentConverter, Converter)
        propObj = {}
        for prop in properties:
            assert isinstance(prop, Property)
            value = prop.get(obj)
            if value is not None:
                path = paths.get(prop.name)
                if isTypeIntId(prop.type) or isPropertyTypeIntId(prop.type):
                    value = self.converterId.asString(value, prop.type)
                else:
                    value = rsp.contentConverter.asString(value, prop.type)
                if path is not None:
                    path.update(value, prop.type)
                    value = {self.normalizer.normalize(prop.type.property.name):value,
                             self.attrPath:rsp.encoderPath.encode(path)}
                propObj[self.normalizer.normalize(prop.name)] = value
        return propObj

    def _convertListIds(self, ids, typProp, basePath, rsp):
        assert isinstance(typProp, TypeProperty)
        idsList = []
        path = self.resourcesManager.findGetModel(basePath, typProp.model)
        for id in ids:
            idsList.append(self._convertProperty(id, path, typProp, rsp))
        return {self.normalizer.normalize(typProp.model.name + self.tagListSufix):idsList}
    
    def _convertListProperty(self, values, typProp, rsp):
        assert isinstance(typProp, TypeProperty)
        valuesList = []
        for value in values:
            valuesList.append(self._convertProperty(value, None, typProp, rsp))
        return {self.normalizer.normalize(typProp.property.name + self.tagListSufix)
                :valuesList}
        
    def _convertModel(self, obj, model, basePath, rsp):
        assert isinstance(model, Model)
        
        properties = [prop for prop in model.properties.values() if prop.name not in rsp.objExclude]
        modelPaths = pathsFor(self.resourcesManager, properties, basePath)
        modelObj = self._convertProperties(obj, properties, modelPaths, rsp)
        
        paths = self.resourcesManager.findGetAllAccessible(basePath)
        pathsModel = self.resourcesManager.findGetAccessibleByModel(model, obj)
        paths.extend([path for path in pathsModel if path not in paths])
        for path in paths: self._appendPath(modelObj, path, rsp, True)
        
        return {self.normalizer.normalize(model.name):modelObj}
        
    def _convertListModels(self, objects, model, basePath, rsp):
        assert isinstance(model, Model)
        path = self.resourcesManager.findGetModel(basePath, model)
        if path is None: properties = list(model.properties.values())
        else: properties = [prop for prop in model.properties.values() if prop.name in rsp.objInclude]
        modelsList = []
        if not properties:
            assert path, 'Nothing to render'
            pathName = self.normalizer.normalize(model.name)
            refList = []
            for obj in objects:
                path.update(obj, model)
                self._appendPath(refList, path, rsp, pathName=pathName)
            return {self.normalizer.normalize(model.name + self.tagListSufix):refList}
        if len(properties) == 1:
            prop = properties[0]
            assert isinstance(prop, Property)
            typProp = TypeProperty(model, prop)
            idsList = []
            for obj in objects:
                if path is not None:
                    path.update(obj, model)
                idsList.append(self._convertProperty(prop.get(obj), path, typProp, rsp))
            return {self.normalizer.normalize(typProp.model.name + self.tagListSufix):idsList}
        elif len(properties) > 0:
            modelPaths = pathsFor(self.resourcesManager, properties, basePath)
            for obj in objects:
                objModel = self._convertProperties(obj, properties, modelPaths, rsp)
                if path is not None:
                    path.update(obj, model)
                    objModel[self.normalizer.normalize(self.attrPath)] = rsp.encoderPath.encode(path)
                modelsList.append(objModel)
            return {self.normalizer.normalize(model.name + self.tagListSufix):modelsList}

# --------------------------------------------------------------------

@injected
class DecodingJSONHandler(DecodingBaseHandler):
    '''
    Provides the decoder for JSON content.
    '''
    
    def __init__(self):
        super().__init__()
        
    def process(self, req, rsp, chain):
        '''
        @see: Processor.process
        '''
        assert isinstance(req, Request), 'Invalid request %s' % req
        assert isinstance(rsp, Response), 'Invalid response %s' % rsp
        assert isinstance(chain, ProcessorsChain), 'Invalid processors chain %s' % chain
        assert req.method in (INSERT, UPDATE), 'Invalid method %s for processor' % req.method
        if self._isValidRequest(req):
            nameModel = findLastModel(req.invoker)
            
            if nameModel:
                try:
                    obj = json.load(codecs.getreader(req.content.charSet or self.charSetDefault)(req.content))
                except ValueError as e:
                    rsp.setCode(BAD_CONTENT, 'Invalid JSON content')
                    return

                name, model = nameModel
                assert isinstance(req.content, ContentRequest)
                assert log.debug('Decoding model %s', model) or True
                try:
                    req.arguments[name] = self._decodeModel(obj, model,
                                                            req.content.contentConverter or rsp.contentConverter)
                    assert log.debug('Successfully decoded for input (%s) value %s', name, req.arguments[name]) or True
                except DevelException as e:
                    rsp.setCode(BAD_CONTENT, e.message)
                except InputException as e:
                    rsp.setCode(BAD_CONTENT, e, 'Invalid data')
                return
            else:
                assert log.debug('Expected a model for decoding the content, could not find one') or True
        else:
            assert log.debug('Invalid request for the JSON decoder') or True
        chain.process(req, rsp)
            
    def _decodeModel(self, obj, model, converter):
        assert isinstance(model, Model)
        assert isinstance(converter, Converter)
        objCount = 1
        modelName = self.normalizer.normalize(model.name)
        modelObj = obj.pop(modelName, None)
        if modelObj is None:
            raise DevelException('Expected key %r for object count %s' % (modelName, objCount))
        if len(obj) > 0:
            raise DevelException('Unknown keys %r for object count %s' % 
                                   (', '.join(str(key) for key in obj.keys()), objCount))
        objCount += 1
        obj = modelObj
        mi = model.createModel()
        errors = []
        for prop in model.properties.values():
            assert isinstance(prop, Property)
            propName = self.normalizer.normalize(prop.name)
            if propName in obj:
                content = obj.pop(propName)
                if content is not None: content = content if isinstance(content, str) else str(content)
                if isTypeIntId(prop.type) or isPropertyTypeId(prop.type):
                    converter = self.converterId
                try:
                    prop.set(mi, converter.asValue(content, prop.type))
                except ValueError:
                    errors.append(Ref(_('Invalid value expected $1 type', _(prop.type)), model=model, property=prop))
                    assert log.debug('Problems setting property %r from JSON value %s', propName, content) or True
        if len(obj) > 0: raise DevelException('Unknown keys %r' % ', '.join(str(key) for key in obj.keys()))
        if len(errors) > 0: raise InputException(*errors)
        return mi
