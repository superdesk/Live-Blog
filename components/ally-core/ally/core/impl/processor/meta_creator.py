'''
Created on Jan 27, 2012

@package: ally core
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the meta creation processor handler.
'''

from ally.api.operator import Model
from ally.api.type import TypeModel, TypeNone, Iter, TypeProperty, Type
from ally.container.ioc import injected
from ally.core.impl.node import NodePath
from ally.core.spec.data_meta import returnSame, MetaLink, MetaValue, MetaModel, \
    MetaPath, MetaList
from ally.core.spec.resources import ResourcesManager, Path
from ally.core.spec.server import Processor, Request, Response, ProcessorsChain
from ally.support.api.util_type import isTypeId, isPropertyTypeId
from ally.support.core.util_resources import nodeLongName
import logging

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

@injected
class MetaCreatorHandler(Processor):
    '''
    Provides the meta creation based on the response object type and in some special cases uses also the object value. 
    
    Provides on request: NA
    Provides on response: [objMeta]
    
    Requires on request: resourcePath
    Requires on response: [objType], [obj]
    '''
    
    resourcesManager = ResourcesManager
    # The resources manager used in locating the resource nodes for the id's presented.
    setPropertyPath = True
    # Flag indicating that the properties that are linked with other models should have the paths to those models placed.
    setAdditionalPaths = True
    # Flag indicating that the models that have additional resources linked with them should have those paths present.

    def __init__(self):
        assert isinstance(self.resourcesManager, ResourcesManager), \
        'Invalid resources manager %s' % self.resourcesManager
        assert isinstance(self.setPropertyPath, bool), 'Invalid set property path flag %s' % self.setPropertyPath
        assert isinstance(self.setAdditionalPaths, bool), 'Invalid set additional paths flag %s' % self.setAdditionalPaths
        
    def process(self, req, rsp, chain):
        '''
        @see: Processor.process
        '''
        assert isinstance(req, Request), 'Invalid request %s' % req
        assert isinstance(rsp, Response), 'Invalid response %s' % rsp
        assert isinstance(chain, ProcessorsChain), 'Invalid processors chain %s' % chain
        
        if req.resourcePath is not None and rsp.objType is not None:
            rsp.objMeta = self.meta(rsp.obj, rsp.objType, req.resourcePath)

        chain.process(req, rsp)
    
    # ----------------------------------------------------------------

    def meta(self, obj, typ, resourcePath):
        '''
        Create the meta object for the provided type.
        
        @param obj: object
            The object to create the meta for.
        @param typ: object
            The type of the object to create the meta for.
        @param resourcePath: Path
            The resource path from where the value originated.
        @return: object
            The meta object.
        '''
        assert isinstance(resourcePath, Path), 'Invalid resource path %s' % resourcePath
        
        if isinstance(typ, Type):
            if isinstance(typ, Iter):
                assert isinstance(typ, Iter)
                itype = typ.itemType
                
                if isinstance(itype, TypeProperty):
                    return MetaList(self.metaProperty(itype, self.linkProperty(itype, resourcePath)), returnSame)
                
                elif isinstance(itype, TypeModel):
                    assert isinstance(itype, TypeModel)
                    model = itype.model
                    return MetaList(self.addPaths(self.metaModel(model, self.linkModel(model, resourcePath, True)),
                                                  self.pathsModel(model, resourcePath)), returnSame)
                    
                elif itype.isOf(Path):
                    return MetaList(MetaLink(returnSame), returnSame)
                else:
                    
                    assert log.debug('Cannot encode list item object type %r', itype) or True
                    
            elif isinstance(typ, TypeNone):
                assert log.debug('Nothing to encode') or True
                
            elif isinstance(typ, TypeProperty):
                return self.metaProperty(typ, self.linkProperty(typ, resourcePath))
            
            elif isinstance(typ, TypeModel):
                assert isinstance(typ, TypeModel)
                model = typ.model
                return self.addPaths(self.metaModel(model, self.linkModel(model, resourcePath)),
                                     self.pathsModel(model, resourcePath))
                
            else:
                assert log.debug('Cannot encode object type %r', typ) or True
    
    def linkProperty(self, typ, resourcePath, getValue=returnSame):
        '''
        Provides the meta link for the property type.
        
        @param typ: TypeProperty
            The property type to provide the meta link for.
        @param resourcePath: Path
            The path reference to get the paths.
        @param getValue: Callable(object)
            A callable that takes as an argument the object to extract this property value instance.
        @return: MetaLink|None
            The meta link or None if is not available for the provided property type.
        '''
        assert isinstance(typ, TypeProperty), 'Invalid property type %s' % typ
        assert isinstance(resourcePath, Path), 'Invalid resource path %s' % resourcePath
        if self.setPropertyPath:
            while isinstance(typ.property.type, TypeProperty): typ = typ.property.type
            if isTypeId(typ.property.type):
                return MetaPath(self.resourcesManager.findGetModel(resourcePath, typ.model), typ, getValue)
    
    def linkModel(self, model, resourcePath, addIds=False):
        '''
        Provides the meta links for the model properties.
        
        @param model: Model
            The model to provide the meta links for.
        @param resourcePath: Path
            The path reference to get the model paths.
        @return: dictionary{string, MetaLink}
            A dictionary having the properties meta links.
        '''
        assert isinstance(model, Model), 'Invalid model %s' % model
        assert isinstance(resourcePath, Path), 'Invalid resource path %s' % resourcePath
        links = {}
        if self.setPropertyPath:
            for name, prop in model.properties.items():
                if isPropertyTypeId(prop.type) or (addIds and isTypeId(prop.type)):
                    linkProp = self.linkProperty(model.typeProperties[name], resourcePath, prop.get)
                    if linkProp: links[name] = linkProp
        return links
    
    def pathsModel(self, model, resourcePath):
        '''
        Provides the additional paths for the model.
        
        @param model: Model
            The model to provide the path for.
        @param resourcePath: Path
            The path reference to get the model paths.
        @return: list[Path]
            A list of the additional paths.
        '''
        assert isinstance(model, Model), 'Invalid model %s' % model
        assert isinstance(resourcePath, Path), 'Invalid resource path %s' % resourcePath
        if self.setAdditionalPaths:
            paths = self.resourcesManager.findGetAllAccessible(resourcePath)
            pathsModel = self.resourcesManager.findGetAccessibleByModel(model)
            paths.extend([path for path in pathsModel if path not in paths])
            return paths
        return []
    
    def metaProperty(self, typ, metaLink=None, getValue=returnSame):
        '''
        Creates the meta for the provided property type.
        
        @param typ: Type
            The type to convert.
        @param metaLink: MetaLink|None
            The meta link of the property type value.
        @param getValue: Callable(object)
            A callable that takes as an argument the object to extract this property value instance.
        @return: Object
            The meta object.
        '''
        assert isinstance(typ, Type), 'Invalid type %s' % typ
        if isinstance(typ, TypeProperty):
            assert isinstance(typ, TypeProperty)
            return MetaModel(typ.model, returnSame,
                             {typ.property.name: self.metaProperty(typ.property.type, metaLink, getValue)})
        return MetaValue(typ, getValue, metaLink)

    def metaModel(self, model, metaLinks={}, getModel=returnSame):
        '''
        Creates the meta for the provided model.
        
        @param model: Model
            The model to convert to provide the meta for.
        @param metaLinks: dictionary{string, MetaLink}
            The meta links for the model properties.
        @param getModel: Callable(object)|None
            A callable that takes as an argument the object to extract the model instance.
        @param getProperty: Callable(object)|None
            A callable that takes as an argument the object to extract all the properties values.
        @return: MetaModel
            The meta object.
        '''
        assert isinstance(model, Model), 'Invalid model %s' % model
        assert isinstance(metaLinks, dict), 'Invalid meta links %s' % metaLinks
        
        metas = {name: self.metaProperty(prop.type, metaLinks.get(name), prop.get)
                 for name, prop in model.properties.items()}
        return MetaModel(model, getModel, metas)
    
    def addPaths(self, metaModel, paths):
        '''
        Adds paths to a meta model.
        
        @param metaModel: MetaModel
            The meta model to add the paths to.
        @param paths: list[Path]|tuple(Path)
            The list of paths to add.
        @return: MetaModel
            The updated meta model.
        '''
        assert isinstance(metaModel, MetaModel), 'Invalid meta model %s' % metaModel
        assert isinstance(paths, (list, tuple)), 'Invalid paths %s' % paths
        if __debug__:
            for path in paths:
                assert isinstance(path, Path), 'Invalid path %s' % path
                assert isinstance(path.node, NodePath), \
                'Invalid path, it suppose to have a node path %s' % path.node
        type, getModel = metaModel.model.type, metaModel.getModel
        metaModel.update({nodeLongName(path.node): MetaPath(path, type, getModel) for path in paths})
        return metaModel
