'''
Created on Jan 27, 2012

@package: ally core
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the meta creation processor handler.
'''

from ally.api.operator import Model, Property
from ally.api.type import TypeModel, TypeNone, Iter, TypeProperty, Type
from ally.container.ioc import injected
from ally.core.impl.node import NodePath
from ally.core.spec.data_meta import Object, Value, ValueLink, Link, List, \
    returnSame
from ally.core.spec.resources import ResourcesManager, Path, Node
from ally.core.spec.server import Processor, Request, Response, ProcessorsChain
from ally.support.api.util_type import isTypeId, isPropertyTypeId
from ally.support.core.util_resources import nodeLongName
import logging
from functools import partial

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
        self._cache = {}
        
    def process(self, req, rsp, chain):
        '''
        @see: Processor.process
        '''
        assert isinstance(req, Request), 'Invalid request %s' % req
        assert isinstance(rsp, Response), 'Invalid response %s' % rsp
        assert isinstance(chain, ProcessorsChain), 'Invalid processors chain %s' % chain
        
        if req.resourcePath is not None and rsp.objType is not None:
            path = req.resourcePath
            assert isinstance(path, Path), 'Invalid resource path %s' % path
            assert path.node, 'Invalid resource path has no node %s' % path
            idNode = id(path.node)
            cache = self._cache.get(idNode)
            if not cache: cache = self._cache[idNode] = {}
            
            if rsp.objType not in cache: cache[rsp.objType] = self.meta(rsp.obj, rsp.objType, path)
            
            rsp.objMeta = cloneMeta(cache[rsp.objType])

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
                    assert isinstance(itype, TypeProperty)
                    if self.setPropertyPath and isPropertyTypeId(itype):
                        path = self.resourcesManager.findGetModel(resourcePath, itype.model)
                    else: path = None
                    return List(self.metaProperty(itype, path))
                elif isinstance(itype, TypeModel):
                    assert isinstance(itype, TypeModel)
                    if self.setPropertyPath:
                        propertiesPaths = self.resourcesManager.findGetModelProperties(resourcePath, itype.model)
                        path = self.resourcesManager.findGetModel(resourcePath, itype.model)
                        if path:
                            assert isinstance(itype.model, Model)
                            idName = [name for name, prop in itype.model.properties.items() if isTypeId(prop.type)]
                            if len(idName) == 1: propertiesPaths[idName[0]] = path
                    else: propertiesPaths = None
                    if self.setAdditionalPaths:
                        paths = self.resourcesManager.findGetAllAccessible(resourcePath)
                        pathsModel = self.resourcesManager.findGetAccessibleByModel(itype.model)
                        paths.extend([path for path in pathsModel if path not in paths])
                    else: paths = None
                    
                    return List(self.metaModel(itype.model, propertiesPaths, paths))
                elif itype.isOf(Path):
                    return self.metaListPath(obj)
                else:
                    assert log.debug('Cannot encode list item object type %r', itype) or True
            elif isinstance(typ, TypeNone):
                assert log.debug('Nothing to encode') or True
            elif isinstance(typ, TypeProperty):
                assert isinstance(typ, TypeProperty)
                if self.setPropertyPath and isPropertyTypeId(typ):
                    path = self.resourcesManager.findGetModel(resourcePath, typ.model)
                else: path = None
                return self.metaProperty(typ, path)
            elif isinstance(typ, TypeModel):
                assert isinstance(typ, TypeModel)
                if self.setPropertyPath:
                    propertiesPaths = self.resourcesManager.findGetModelProperties(resourcePath, typ.model)
                else: propertiesPaths = None
                if self.setAdditionalPaths:
                    paths = self.resourcesManager.findGetAllAccessible(resourcePath)
                    pathsModel = self.resourcesManager.findGetAccessibleByModel(typ.model)
                    paths.extend([path for path in pathsModel if path not in paths])
                else: paths = None
                
                return self.metaModel(typ.model, propertiesPaths, paths)
            else:
                assert log.debug('Cannot encode object type %r', typ) or True
    
    def metaProperty(self, typ, path=None):
        '''
        Creates the meta for the provided property type.
        
        @param typ: TypeProperty
            The type property to convert.
        @param path: Path|None
            The reference path of the property type.
        @return: Object
            The meta object.
        '''
        assert isinstance(typ, TypeProperty), 'Invalid type property %s' % typ
        return Object(properties=
                {typ.property.name: ValueLink(typ, getLink=UpdatePath(path, typ)) if path is not None else Value(typ)})
    
    def metaModel(self, model, propertiesPaths=None, paths=None):
        '''
        Creates the meta for the provided model.
        
        @param model: Model
            The model to convert to provide the meta for.
        @param propertiesPaths: dictionary{string, Path}|None
            The reference paths of the properties.
        @param paths: list[Path]|tuple(Path)
            Additional resources paths to be included in the properties meta object.
        @return: Object
            The meta object.
        '''
        assert isinstance(model, Model), 'Invalid model %s' % model
        assert not propertiesPaths or isinstance(propertiesPaths, dict), 'Invalid properties paths %s' % propertiesPaths
        
        properties = {}
        for name, prop in model.properties.items():
            assert isinstance(prop, Property)
            
            path = propertiesPaths.get(name) if propertiesPaths else None
            if path:
                if isinstance(prop.type, TypeProperty): typ = prop.type
                else: typ = model.typeProperties[name]
                properties[name] = ValueLink(typ, prop.get, UpdatePath(path, typ, prop.get))
            else: properties[name] = Value(prop.type, prop.get)
            
        if paths:
            assert isinstance(paths, (list, tuple)), 'Invalid paths %s' % paths
            if __debug__:
                for path in paths:
                    assert isinstance(path, Path), 'Invalid path %s' % path
                    assert isinstance(path.node, NodePath), \
                    'Invalid path, it suppose to have a node path %s' % path.node
            properties.update({nodeLongName(path.node):Link(UpdatePath(path, model.type)) for path in paths})

        return Object(properties=properties)
    
    def metaListPath(self, paths):
        '''
        Creates the meta for the provided list of paths.
        
        @param paths: Iterable[path]
            The paths to create the meta for.
        @return: Object
            The meta object.
        '''
        if __debug__:
            for path in paths:
                assert isinstance(path, Path), 'Invalid path %s' % path
                assert isinstance(path.node, Node), 'Invalid path %s, has not node' % path
        getitem = lambda index, obj: list.__getitem__(obj, index)
        return Object(properties={nodeLongName(path.node): Link(partial(getitem, k)) for k, path in enumerate(paths)})
        
# --------------------------------------------------------------------
# Helper functions used by the created meta objects.

class UpdatePath:
    '''
    Callable class that returns a updated path.
    '''
    
    def __init__(self, path, type, getValue=returnSame):
        '''
        Construct the update path callable.
        
        @param path: Path
            The path to be updated and returned.
        @param type: TypeProperty|TypeModel
            The type of the object to be updated.
        @param getValue: Callable(object)
            A callable that takes as an argument the object to extract the value for the path.
        '''
        assert isinstance(path, Path), 'Invalid path %s' % path
        assert isinstance(type, (TypeProperty, TypeModel)), 'Invalid type %s' % type
        assert callable(getValue), 'Invalid get value callable %s' % getValue
        self.type = type
        self.path = path
        self.getValue = getValue
        
    def __call__(self, obj):
        '''
        Process the update.
        
        @param obj: object
            The object to update with.
        @return: Path
            The updated path.
        '''
        self.path.update(self.getValue(obj), self.type)
        return self.path
    
    def clone(self):
        '''
        Clones the update path call.
        '''
        return UpdatePath(self.path.clone(), self.type, self.getValue)

def cloneMeta(meta):
    '''
    Clones the meta object. Attention the cloning is performed only for the meta objects that require that, for instance
    for Object meta and Link meta. So this is not a general purpose cloning for meta objects.
    
    @param meta: meta object
        The meta object to clone.
    @return: meta object
        The cloned meta object.
    '''
    if isinstance(meta, Object):
        assert isinstance(meta, Object)
        return Object(meta.getObject, {name:cloneMeta(m) for name, m in meta.properties.items()})
    elif isinstance(meta, Link):
        assert isinstance(meta, Link)
        if isinstance(meta.getLink, UpdatePath):
            assert isinstance(meta.getLink, UpdatePath)
            if isinstance(meta, ValueLink):
                assert isinstance(meta, ValueLink)
                return ValueLink(meta.type, meta.getValue, meta.getLink.clone())
            else:
                return Link(meta.getLink.clone())
    return meta
