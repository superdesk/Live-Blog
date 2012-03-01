'''
Created on Jan 27, 2012

@package: ally core
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the meta creation processor handler.
'''

from ally.api.operator import Model, Property
from ally.api.type import TypeModel, TypeNone, Iter, TypeProperty, Type, \
    IterPart, List
from ally.container.ioc import injected
from ally.core.spec.data_meta import returnSame, MetaLink, MetaValue, MetaModel, \
    MetaPath, MetaCollection
from ally.core.spec.resources import ResourcesManager, Path
from ally.core.spec.server import Processor, Request, Response, ProcessorsChain
from ally.support.api.util_type import isPropertyTypeId
from ally.support.core.util_resources import nodeLongName
import logging

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

returnTotal = lambda part: part.total
# Function that returns the total count of a part.

# --------------------------------------------------------------------

@injected
class MetaCreatorHandler(Processor):
    '''
    Provides the meta creation based on the response object type. 
    
    Provides on request: NA
    Provides on response: [objMeta]
    
    Requires on request: resourcePath
    Requires on response: [objType]
    '''
    
    resourcesManager = ResourcesManager
    # The resources manager used in locating the resource nodes for the id's presented.

    def __init__(self):
        assert isinstance(self.resourcesManager, ResourcesManager), \
        'Invalid resources manager %s' % self.resourcesManager
        
    def process(self, req, rsp, chain):
        '''
        @see: Processor.process
        '''
        assert isinstance(req, Request), 'Invalid request %s' % req
        assert isinstance(rsp, Response), 'Invalid response %s' % rsp
        assert isinstance(chain, ProcessorsChain), 'Invalid processors chain %s' % chain
        
        if req.resourcePath is not None and rsp.objType is not None:
            rsp.objMeta = self.meta(rsp.objType, req.resourcePath)

        chain.proceed()
    
    # ----------------------------------------------------------------

    def meta(self, typ, resourcePath):
        '''
        Create the meta object for the provided type.
        
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
                
                if isinstance(typ, IterPart): getTotal = returnTotal
                else: getTotal = None
                
                itype = typ.itemType
                
                if isinstance(itype, TypeProperty):
                    return MetaCollection(self.metaProperty(itype, resourcePath), returnSame, getTotal)
                
                elif isinstance(itype, TypeModel):
                    assert isinstance(itype, TypeModel)
                    return MetaCollection(self.metaModel(itype.model, resourcePath), returnSame, getTotal)
                    
                elif itype.isOf(Path):
                    return MetaCollection(MetaLink(returnSame), returnSame, getTotal)
                else:
                    
                    assert log.debug('Cannot encode list item object type %r', itype) or True
                    
            elif isinstance(typ, TypeNone):
                assert log.debug('Nothing to encode') or True
                
            elif isinstance(typ, TypeProperty):
                return self.metaProperty(typ, resourcePath)
            
            elif isinstance(typ, TypeModel):
                assert isinstance(typ, TypeModel)
                return self.metaModel(typ.model, resourcePath)
                
            else:
                assert log.debug('Cannot encode object type %r', typ) or True
    
    def metaProperty(self, typ, resourcePath, getValue=returnSame):
        '''
        Creates the meta for the provided property type.
        
        @param typ: Type
            The type to convert.
        @param resourcePath: Path
            The path reference to get the paths.
        @param getValue: Callable(object)
            A callable that takes as an argument the object to extract this property value instance.
        @return: Object
            The meta object.
        '''
        assert isinstance(typ, Type), 'Invalid type %s' % typ
        assert isinstance(resourcePath, Path), 'Invalid resource path %s' % resourcePath
        
        if isinstance(typ, TypeProperty):
            assert isinstance(typ, TypeProperty)
            
            if isPropertyTypeId(typ):
                path = self.resourcesManager.findGetModel(resourcePath, typ.model)
                if path: metaLink = MetaPath(path, typ, getValue)
                else: metaLink = None
            else: metaLink = None
            
            prop = typ.property
            assert isinstance(prop, Property)
            return MetaModel(typ.model, getValue, metaLink,
                             {prop.name: self.metaProperty(prop.type, resourcePath)})
        if isinstance(typ, List):
            assert isinstance(typ, List)
            return MetaCollection(MetaValue(typ.itemType, returnSame), getValue)
        return MetaValue(typ, getValue)

    def metaModel(self, model, resourcePath, getModel=returnSame):
        '''
        Creates the meta for the provided model.
        
        @param model: Model
            The model to convert to provide the meta for.
        @param resourcePath: Path
            The path reference to get the paths.
        @param getModel: Callable(object)|None
            A callable that takes as an argument the object to extract the model instance.
        @return: MetaModel
            The meta object.
        '''
        assert isinstance(model, Model), 'Invalid model %s' % model
        assert isinstance(resourcePath, Path), 'Invalid resource path %s' % resourcePath
        
        metas = {}
        for name, prop in model.properties.items():
            assert isinstance(prop, Property)
            metas[name] = self.metaProperty(prop.type, resourcePath, prop.get)
        
        paths = self.resourcesManager.findGetAllAccessible(resourcePath)
        pathsModel = self.resourcesManager.findGetAccessibleByModel(model)
        paths.extend([path for path in pathsModel if path not in paths])
        metas.update({nodeLongName(path.node): MetaPath(path, model.type, getModel) for path in paths})
        
        path = self.resourcesManager.findGetModel(resourcePath, model)
        if path: metaLink = MetaPath(path, model.type, getModel)
        else: metaLink = None
        
        return MetaModel(model, getModel, metaLink, metas)
