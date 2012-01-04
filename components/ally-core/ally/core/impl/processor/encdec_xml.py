'''
Created on Jul 11, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the XML encoding/decoding processor handler.
'''

from _pyio import TextIOWrapper
from ally import internationalization
from ally.api.operator import Model, Property
from ally.api.type import TypeProperty, Iter, TypeModel, TypeNone
from ally.core.impl.node import NodePath
from ally.core.impl.processor.encdec_base import DecodingBaseHandler, \
    EncodingBaseHandler, findLastModel
from ally.core.impl.util_type import isPropertyTypeId, isPropertyTypeIntId, \
    isTypeIntId, pathsFor
from ally.core.spec.codes import BAD_CONTENT
from ally.core.spec.resources import Path, Converter
from ally.core.spec.server import Request, Response, ProcessorsChain, \
    ContentRequest
from ally.digester_xml import Rule, RuleRoot, Digester, Node
from ally.exception import DevelException, InputException, Ref
from ally.ioc import injected
from xml.sax.saxutils import XMLGenerator
import logging

# --------------------------------------------------------------------

log = logging.getLogger(__name__)
_ = internationalization.translator(__name__)

# --------------------------------------------------------------------

@injected
class EncodingXMLHandler(EncodingBaseHandler):
    '''
    Provides the XML encoding.
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
            if not rsp.objType and isinstance(rsp.obj, dict):
                # Expecting a plain dictionary dictionary or list for rendering
                xml = self._xml(req, rsp)
                self._encodeDict(xml, rsp.obj)
                xml.endDocument()
                return
             
            if rsp.encoderPath:
                # TODO: see about the priority of the content location over the encoding of objects, the problem
                # is that at insert it will encode the href only without the actual property id.
                if rsp.contentLocation:
                    xml = self._xml(req, rsp)
                    pathName = self.normalizer.normalize(self.attrPath)
                    xml.startElement(pathName, {})
                    xml.characters(rsp.encoderPath.encode(rsp.contentLocation))
                    xml.endElement(pathName)
                    xml.endDocument()
                    return

                typ = rsp.objType
                if typ is None or isinstance(typ, TypeNone):
                    assert log.debug('Nothing to encode') or True
                    return
                if isinstance(typ, Iter):
                    assert isinstance(typ, Iter)
                    xml = None
                    if typ.isOf(Path):
                        xml = self._xml(req, rsp)
                        self._encodeListPath(xml, rsp.obj, rsp)
                    elif isPropertyTypeId(typ.itemType):
                        xml = self._xml(req, rsp)
                        self._encodeListIds(xml, rsp.obj, typ.itemType, req.resourcePath, rsp)
                    elif isinstance(typ.itemType, TypeProperty):
                        xml = self._xml(req, rsp)
                        self._encodeListProperty(xml, rsp.obj, typ.itemType, rsp)
                    elif isinstance(typ.itemType, TypeModel):
                        xml = self._xml(req, rsp)
                        self._encodeListModels(xml, rsp.obj, typ.itemType.model, req.resourcePath, rsp)
                    if xml:
                        xml.endDocument()
                        return
                    else:
                        assert log.debug('Cannot encode list item object type %r', typ.itemType) or True
                elif isinstance(typ, TypeProperty):
                    xml = self._xml(req, rsp)
                    if isPropertyTypeId(typ):
                        path = self.resourcesManager.findGetModel(req.resourcePath, typ.model)
                    else: path = None
                    self._encodeProperty(xml, rsp.obj, path, typ, rsp)
                    xml.endDocument()
                    return
                elif isinstance(typ, TypeModel):
                    xml = self._xml(req, rsp)
                    self._encodeModel(xml, rsp.obj, typ.model, req.resourcePath, rsp)
                    xml.endDocument()
                    return
                else:
                    assert log.debug('Cannot encode object type %r', typ) or True
            else:
                assert log.debug('Invalid response, has no path encoder') or True
        chain.process(req, rsp)

    def _xml(self, req, rsp):
        assert isinstance(rsp, Response)
        charSet = self._getCharSet(req, rsp)
        txt = TextIOWrapper(rsp.dispatch(), charSet, self.encodingError)
        # Need to stop the text close since this will close the socket, just a small hack to prevent this.
        txt.close = None
        xml = XMLGenerator(txt, charSet, short_empty_elements=True)
        xml.startDocument()
        return xml
    
    def _encodeDict(self, xml, d):
        assert isinstance(xml, XMLGenerator)
        assert isinstance(d, dict)
        for name, value in d.items():
            name = self.normalizer.normalize(name)
            if isinstance(value, list):
                self._encodeList(xml, name, value)
            else:
                xml.startElement(name, {})
                if isinstance(value, dict):
                    self._encodeDict(xml, value)
                elif isinstance(value, str):
                    xml.characters(value)
                else:
                    raise AssertionError('Cannot encode value %r' % value)
                xml.endElement(name)

    def _encodeList(self, xml, name, l):
        assert isinstance(xml, XMLGenerator)
        assert isinstance(l, list)
        xml.startElement(name, {})
        for value in l:
            if isinstance(value, dict):
                self._encodeDict(xml, value)
            elif isinstance(value, str):
                xml.characters(value)
            else:
                raise AssertionError('Cannot encode value %r' % value)
        xml.endElement(name)

    def _encodePath(self, xml, path, rsp, fullName=False, pathName=None):
        assert isinstance(xml, XMLGenerator)
        assert isinstance(path, Path), 'Invalid path %s' % path
        assert isinstance(rsp, Response)
        if not pathName:
            node = path.node
            assert isinstance(node, NodePath)
            if fullName:
                pathName = ''
                while node and isinstance(node, NodePath):
                    pathName = node.name + pathName
                    node = node.parent
            else:
                pathName = node.name
            pathName = self.normalizer.normalize(pathName)
        xml.startElement(pathName, {self.attrPath:rsp.encoderPath.encode(path)})
        xml.endElement(pathName)

    def _encodeListPath(self, xml, paths, rsp):
        assert isinstance(xml, XMLGenerator)
        listName = self.normalizer.normalize(self.tagResources)
        xml.startElement(listName, {})
        for path in paths:
            self._encodePath(xml, path, rsp, True)
        xml.endElement(listName)
    
    def _encodeProperty(self, xml, value, path, typProp, rsp):
        assert isinstance(xml, XMLGenerator)
        assert isinstance(rsp.contentConverter, Converter)
        assert isinstance(rsp, Response)
        assert isinstance(typProp, TypeProperty)
        if path is None:
            attrs = {}
        else:
            assert isinstance(path, Path)
            path.update(value, typProp)
            attrs = {self.attrPath:rsp.encoderPath.encode(path)}
        propName = self.normalizer.normalize(typProp.property.name)
        xml.startElement(propName, attrs)
        if isTypeIntId(typProp) or isPropertyTypeIntId(typProp):
            xml.characters(self.converterId.asString(value, typProp))
        else:
            xml.characters(rsp.contentConverter.asString(value, typProp))
        xml.endElement(propName)
        
    def _encodeProperties(self, xml, obj, properties, paths, rsp):
        assert isinstance(xml, XMLGenerator)
        assert isinstance(rsp.contentConverter, Converter)
        for prop in properties:
            assert isinstance(prop, Property)
            value = prop.get(obj)
            if value is not None:
                propName = self.normalizer.normalize(prop.name)
                path = paths.get(prop.name)
                if path is not None:
                    path.update(value, prop.type)
                    attrs = {self.attrPath:rsp.encoderPath.encode(path)}
                else:
                    attrs = {}
                xml.startElement(propName, attrs)
                if isTypeIntId(prop.type) or isPropertyTypeIntId(prop.type):
                    xml.characters(self.converterId.asString(value, prop.type))
                else:
                    xml.characters(rsp.contentConverter.asString(value, prop.type))
                xml.endElement(propName)
        
    def _encodeListIds(self, xml, ids, typProp, basePath, rsp):
        assert isinstance(xml, XMLGenerator)
        assert isinstance(typProp, TypeProperty)
        listName = self.normalizer.normalize(typProp.model.name + self.tagListSufix)
        xml.startElement(listName, {})
        path = self.resourcesManager.findGetModel(basePath, typProp.model)
        for id in ids:
            self._encodeProperty(xml, id, path, typProp, rsp)
        xml.endElement(listName)
        
    def _encodeListProperty(self, xml, values, typProp, rsp):
        assert isinstance(xml, XMLGenerator)
        assert isinstance(typProp, TypeProperty)
        listName = self.normalizer.normalize(typProp.property.name + self.tagListSufix)
        xml.startElement(listName, {})
        for value in values:
            self._encodeProperty(xml, value, None, typProp, rsp)
        xml.endElement(listName)
        
    def _encodeModel(self, xml, obj, model, basePath, rsp):
        assert isinstance(xml, XMLGenerator)
        assert isinstance(model, Model)
        
        properties = [prop for prop in model.properties.values() if prop.name not in rsp.objExclude]
        modelName = self.normalizer.normalize(model.name)
        xml.startElement(modelName, {})
        modelPaths = pathsFor(self.resourcesManager, properties, basePath)
        self._encodeProperties(xml, obj, properties, modelPaths, rsp)
        
        paths = self.resourcesManager.findGetAllAccessible(basePath)
        pathsModel = self.resourcesManager.findGetAccessibleByModel(model, obj)
        paths.extend([path for path in pathsModel if path not in paths])
        for path in paths: self._encodePath(xml, path, rsp, True)
        
        xml.endElement(modelName)
        
    def _encodeListModels(self, xml, objects, model, basePath, rsp):
        assert isinstance(xml, XMLGenerator)
        assert isinstance(model, Model)
        path = self.resourcesManager.findGetModel(basePath, model)
        if path is None: properties = list(model.properties.values())
        else: properties = [prop for prop in model.properties.values() if prop.name in rsp.objInclude]
        listName = self.normalizer.normalize(model.name + self.tagListSufix)
        xml.startElement(listName, {})
        if not properties:
            assert path, 'Nothing to render'
            pathName = self.normalizer.normalize(model.name)
            for obj in objects:
                path.update(obj, model)
                self._encodePath(xml, path, rsp, pathName=pathName)
        elif len(properties) == 1:
            prop = properties[0]
            assert isinstance(prop, Property)
            typProp = TypeProperty(model, prop)
            for obj in objects:
                if path is not None:
                    path.update(obj, model)
                self._encodeProperty(xml, prop.get(obj), path, typProp, rsp)
        elif len(properties) > 0:
            modelPaths = pathsFor(self.resourcesManager, properties, basePath)
            for obj in objects:
                if path is not None:
                    path.update(obj, model)
                    attrs = {self.attrPath:rsp.encoderPath.encode(path)}
                else: attrs = {}
                modelName = self.normalizer.normalize(model.name)
                xml.startElement(modelName, attrs)
                self._encodeProperties(xml, obj, properties, modelPaths, rsp)
                xml.endElement(modelName)
        xml.endElement(listName)

# --------------------------------------------------------------------

@injected
class DecodingXMLHandler(DecodingBaseHandler):
    '''
    Provides the decoder for XML content.
    
    @see: DecodingBaseHandler
    
    Provides on request: arguments
    Provides on response: NA
    
    Requires on request: invoker, content, [content.contentConverter], [content.charSet]
    Requires on response: contentConverter
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
        if self._isValidRequest(req):
            root = None
            
            nameModel = findLastModel(req.invoker)
            if nameModel:
                name, model = nameModel
                assert isinstance(req.content, ContentRequest)
                root = self._ruleModel(model, req.content.contentConverter or rsp.contentConverter)
                assert log.debug('Decoding model %s', model) or True
            else:
                assert log.debug('Expected a model for decoding the content, could not find one') or True
            
            if root:
                digester = Digester(root, False, False)
                try:
                    value = digester.parse(req.content.charSet or self.charSetDefault, req.content)
                    if len(digester.errors) > 0: raise InputException(*digester.errors)
                    req.arguments[name] = value
                    assert log.debug('Successfully decoded for input (%s) value %s', name, value) or True
                except DevelException as e:
                    rsp.setCode(BAD_CONTENT, e.message)
                except InputException as e:
                    rsp.setCode(BAD_CONTENT, e, 'Invalid data')
                return
        else:
            assert log.debug('Invalid request for the XML decoder') or True
        chain.process(req, rsp)
        
    def _ruleModel(self, model, converter):
        assert isinstance(model, Model)
        root = RuleRoot()
        rmodel = root.addRule(RuleModel(model), self.normalizer.normalize(model.name))
        for prop in model.properties.values():
            if isTypeIntId(prop.type) or isPropertyTypeId(prop.type):
                rmodel.addRule(RuleSetProperty(model, prop, self.converterId), \
                           self.normalizer.normalize(prop.name))
            else:
                rmodel.addRule(RuleSetProperty(model, prop, converter), \
                               self.normalizer.normalize(prop.name))
        return root

# --------------------------------------------------------------------

class RuleModel(Rule):
    '''
    Rule implementation that provides the creation of an object at begin.
    '''
    
    def __init__(self, model):
        '''
        @param model: Model
            The model to create instances for.
        '''
        assert isinstance(model, Model), 'Invalid model %s' % model
        self._model = model
        
    def begin(self, digester):
        '''
        @see: Rule.begin
        '''
        assert isinstance(digester, Digester)
        digester.stack.append(self._model.createModel())
        
    def end(self, node, digester):
        '''
        @see: Rule.end
        '''
        assert isinstance(node, Node)
        assert isinstance(digester, Digester)
        if len(digester.stack) > 1:
            digester.stack.pop()
            
# --------------------------------------------------------------------

class RuleSetProperty(Rule):
    '''
    Rule implementation that sets the content of an element to the closest stack object.
    '''
    
    def __init__(self, model, property, converter):
        '''
        @param model: Model
            The model of the property.
        @param property: Property
            The property to be used in setting the value, this will receive as the first argument the
            last stack object and as a second the value to set.
        @param converter: Converter
            The converter to be used in transforming the content to the required value type.
        '''
        assert isinstance(model, Model), 'Invalid model %s' % model
        assert isinstance(property, Property), 'Invalid property %s' % property
        assert isinstance(converter, Converter), 'Invalid value converter %s' % converter
        self._model = model
        self._property = property
        self._converter = converter
    
    def begin(self, digester):
        '''
        @see: Rule.begin
        '''
        digester.stack.append(None)
        
    def content(self, digester, content):
        '''
        @see: Rule.content
        '''
        assert isinstance(digester, Digester)
        assert len(digester.stack) > 0, \
        'Invalid structure there is no stack object to use for setting value on path %s' % digester.currentPath()
        digester.stack[-1] = content
            
    def end(self, node, digester):
        '''
        @see: Rule.end
        '''
        assert isinstance(digester, Digester)
        assert len(digester.stack) > 0, \
        'Invalid structure there is no stack object to use for setting value on path %s' % digester.currentPath()
        content = digester.stack.pop()
        try:
            self._property.set(digester.stack[-1], self._converter.asValue(content, self._property.type))
        except ValueError:
            digester.errors.append(Ref(_('Invalid value expected $1 type', str(self._property.type)),
                                       model=self._model, property=self._property))
            assert log.debug('Problems setting property %r from XML value %s', self._property.name, content) or True
