'''
Created on Aug 9, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides utility methods for types and data associated with types.
'''

from ally.api.type import TypeId, TypeProperty, Iter, TypeModel

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
