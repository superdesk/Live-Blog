'''
Created on May 9, 2012

@package: ally authentication
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides authentication support.
'''

from .operator.type import TypeModel, TypeModelProperty
from .type import typeFor, Type
from ally.api.operator.authentication.type import TypeModelAuth

# --------------------------------------------------------------------

def auth(obj):
    '''
    Converts the provided type to a authentication type.
    
    @param obj: object|class
        The class or object to extract the type to authenticate.
    @return: TypeModelAuth|TypeModelPropertyAuth
        The authenticated type.
    '''
    if isinstance(obj, Type): typ = obj
    else:
        typ = typeFor(obj)
        assert typ is not None, 'Invalid object %s' % obj

    isIdProperty = False
    if isinstance(typ, TypeModelProperty):
        assert isinstance(typ, TypeModelProperty)
        if typ.property == typ.parent.container.propertyId:
            typ = typ.parent
            isIdProperty = True

    if isinstance(typ, TypeModel):
        assert isinstance(typ, TypeModel)
        assert typ.baseClass is None, \
        'Required only plain API model types for authentication, illegal mapped API model type %s' % typ
        typ = TypeModelAuth(typ.forClass, typ.container)
        if isIdProperty: return typ.childTypeId()
        return typ

    raise TypeError('Invalid type %s to mark as authenticated' % typ)
