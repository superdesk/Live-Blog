'''
Created on Jan 27, 2012

@package: ally core
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the meta creation processor handler.
'''

from ally.api.type import TypeNone, Iter, Type, IterPart, List, typeFor
from ally.container.ioc import injected
from ally.core.spec.data_meta import returnSame, MetaLink, MetaValue, MetaModel, \
    MetaPath, MetaCollection
from ally.core.spec.resources import ResourcesManager, Path
from ally.core.spec.server import Processor, Request, Response, ProcessorsChain
from ally.support.core.util_resources import nodeLongName
import logging
from ally.api.operator.type import TypeModelProperty, TypeModel
from ally.api.operator.container import Model
from functools import partial

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

returnTotal = lambda part: part.total
# Function that returns the total count of a part.

rgetattr = lambda prop, obj: getattr(obj, prop)
# A simple lambda that just reverses the getattr parameters in order to be used with partial.

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

                if isinstance(itype, TypeModelProperty):
                    return MetaCollection(self.metaProperty(itype, resourcePath), returnSame, getTotal)

                elif isinstance(itype, TypeModel):
                    assert isinstance(itype, TypeModel)
                    return MetaCollection(self.metaModel(itype, resourcePath), returnSame, getTotal)

                elif itype.isOf(Path):
                    return MetaCollection(MetaLink(returnSame), returnSame, getTotal)
                else:

                    assert log.debug('Cannot encode list item object type %r', itype) or True

            elif isinstance(typ, TypeNone):
                assert log.debug('Nothing to encode') or True

            elif isinstance(typ, TypeModelProperty):
                return self.metaProperty(typ, resourcePath)

            elif isinstance(typ, TypeModel):
                assert isinstance(typ, TypeModel)
                return self.metaModel(typ, resourcePath)

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

        if isinstance(typ, TypeModelProperty):
            assert isinstance(typ, TypeModelProperty)

            if typ.container.propertyId == typ.property:
                path = self.resourcesManager.findGetModel(resourcePath, typ.container)
                if path: metaLink = MetaPath(path, typ, getValue)
                else: metaLink = None
            else: metaLink = None

            return MetaModel(typ.container, getValue, metaLink,
                             {typ.property: self.metaProperty(typ.type, resourcePath)})

        if isinstance(typ, TypeModel):
            assert isinstance(typ, TypeModel)
            typId = typeFor(getattr(typ.forClass, typ.container.propertyId))
            assert isinstance(typId, TypeModelProperty)
            path = self.resourcesManager.findGetModel(resourcePath, typ.container)
            if path: metaLink = MetaPath(path, typId, getValue)
            else: metaLink = None

            return MetaModel(typ.container, getValue, metaLink,
                             {typId.property: self.metaProperty(typId.type, resourcePath)})

        if isinstance(typ, List):
            assert isinstance(typ, List)
            return MetaCollection(MetaValue(typ.itemType, returnSame), getValue)
        return MetaValue(typ, getValue)

    def metaModel(self, typ, resourcePath, getModel=returnSame):
        '''
        Creates the meta for the provided model.
        
        @param typ: TypeModel
            The model to convert to provide the meta for.
        @param resourcePath: Path
            The path reference to get the paths.
        @param getModel: Callable(object)|None
            A callable that takes as an argument the object to extract the model instance.
        @return: MetaModel
            The meta object.
        '''
        assert isinstance(typ, TypeModel), 'Invalid type model %s' % typ
        assert isinstance(resourcePath, Path), 'Invalid resource path %s' % resourcePath
        model = typ.container
        assert isinstance(model, Model)

        metas = {}
        for prop, ptyp in model.properties.items():
            metas[prop] = self.metaProperty(ptyp, resourcePath, partial(rgetattr, prop))

        paths = self.resourcesManager.findGetAllAccessible(resourcePath)
        pathsModel = self.resourcesManager.findGetAccessibleByModel(model)
        paths.extend([path for path in pathsModel if path not in paths])
        metas.update({nodeLongName(path.node): MetaPath(path, typ, getModel) for path in paths})

        path = self.resourcesManager.findGetModel(resourcePath, model)
        if path: metaLink = MetaPath(path, typ, getModel)
        else: metaLink = None

        return MetaModel(model, getModel, metaLink, metas)
