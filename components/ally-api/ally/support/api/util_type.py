'''
Created on Aug 9, 2011

@package: ally api
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides utility methods for types and data associated with types.
'''

from ally.api.operator import Property, Model
from ally.api.type import TypeId, TypeProperty, Iter, TypeModel, typeFor

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

def propertyOf(refProp):
    '''
    Provides the property found in the provided property reference.
    
    @param ref: Property|TypeProperty
        The reference to get the property from.
    @return: Property|None
        The property found for the reference, None if the reference cannot provide a property.       
    '''
    if isinstance(refProp, Property): return refProp
    else:
        typ = typeFor(refProp)
        if isinstance(typ, TypeProperty): return typ.property

def modelOf(refModel):
    '''
    Provides the model found in the provided model reference.
    
    @param refModel: Model|TypeModel
        The reference to get the model from.
    @return: Model|None
        The model found for the reference, None if the reference cannot provide a model.       
    '''
    if isinstance(refModel, Model): return refModel
    else:
        typ = typeFor(refModel)
        if isinstance(typ, TypeModel): return typ.model

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
        if isinstance(typ.itemType, TypeModel):
            return typ.itemType.model
    return None
