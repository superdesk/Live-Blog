'''
Created on Aug 9, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides utility methods for types and data associated with types.
'''
from ally.api.type import TypeId, TypeProperty, Iter, TypeModel
from ally.api.operator import Property
from ally.core.spec.resources import ResourcesManager

# --------------------------------------------------------------------

def isTypeId(typ):
    '''
    Checks if the provided type is a type id.
    
    @param typ: Type
        The type to check.
    @return: boolean
        True if the provided type is a type id, false otherwise.
    '''
    return isinstance(typ, TypeId)

def isTypeIntId(typ):
    '''
    Checks if the provided type is a type integer id.
    
    @param typ: Type
        The type to check.
    @return: boolean
        True if the provided type is a type integer id, false otherwise.
    '''
    return isinstance(typ, TypeId) and typ.isOf(int)

def isPropertyTypeId(typ, model=None):
    '''
    Checks if the provided type is a property type for a type id.
    
    @param typ: Type
        The type to check.
    @param model: Model|None
        The model for which the property type has to belong to, will not be checked if None.
    @return: boolean
        True if the provided type is a property for an id, false otherwise.
    '''
    typProp = None
    while isinstance(typ, TypeProperty):
        typProp = typ
        typ = typ.property.type
    if not (typProp and isTypeId(typ)):
        return False
    if model and not typProp.model == model:
        return False
    return True

def isPropertyTypeIntId(typ, model=None):
    '''
    Checks if the provided type is a property type for an integer type id.
    
    @param typ: Type
        The type to check.
    @param model: Model|None
        The model for which the property type has to belong to, will not be checked if None.
    @return: boolean
        True if the provided type is a property for an integer id, false otherwise.
    '''
    return isPropertyTypeId(typ) and typ.isOf(int)

# --------------------------------------------------------------------

def modelOfIter(typ):
    '''
    Extracts the model if the type is Iter with an item type of type model.
    
    @param typ: Type
        The type to check.
    @return: Model|None
        The model of the Iter if is a match or None if the type is not an Iter with type model.
    '''
    if isinstance(typ, Iter):
        assert isinstance(typ, Iter)
        typ = typ.itemType
        if isinstance(typ, TypeModel):
            return typ.model
    return None

def pathsFor(resourcesManager, properties, basePath):
    '''
    Extracts the paths that are linked with the provided properties. Basically any property that represents the id
    property type for a model is searched for a path.
    
    @param resourcesManager: ResourcesManager
        The resource manager used for searching the paths.
    @param properties: list[Property]
        The list of properties to search in.
    @param basePath: Path
        The base bath to perform the search from.
    '''
    assert isinstance(resourcesManager, ResourcesManager), 'Invalid resource manager %s' % resourcesManager
    assert isinstance(properties, list), 'Invalid properties list %s' % properties
    paths = {}
    for prop in properties:
        assert isinstance(prop, Property)
        if isPropertyTypeId(prop.type):
            path = resourcesManager.findGetModel(basePath, prop.type.model)
            if path is not None:
                paths[prop.name] = path
    return paths
