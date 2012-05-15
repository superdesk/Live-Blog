'''
Created on May 10, 2012

@package: ally authentication
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the conversion to authenticated types.
'''

from .type import IAuthenticated, TypeModelAuth
from ally.api.operator.authentication.type import TypeModelPropertyAuth
from ally.api.operator.container import Model
from ally.api.operator.descriptor import Property, Reference
from ally.api.operator.type import TypeModel
from ally.api.type import typeFor

# --------------------------------------------------------------------

def asAuthenticated(typeModel):
    '''
    Converts the provided model type to a authenticated model type. All the properties for the authenticated model type
    class will point to the authenticated model type, so even if a property from an authenticated type model is used it
    will show that the parent model type is authenticated.
    
    @param typeModel: TypeModel
        The model type to make authenticated.
    @return: TypeModelAuth
        The authenticated model type.
    '''
    assert isinstance(typeModel, TypeModel), 'Invalid model type %s' % typeModel
    assert typeModel.baseClass is None, \
    'Required only plain API model types for authentication, illegal mapped API model type %s' % typeModel
    # If we have a base type it means that the type model is mapped, which is not allowed.

    # If is already authenticated type then we returned as it is.
    if isinstance(typeModel, IAuthenticated): return typeModel

    clazz, model = typeModel.forClass, typeModel.container
    assert isinstance(model, Model)

    try: return typeFor(clazz._ally_authentificated)
    except AttributeError: pass

    # We create a new model class where we provide the authenticated types.
    classAuth = type(clazz.__name__ + '$Auth', (clazz,), {'__module__': clazz.__module__})
    typeModelAuth = TypeModelAuth(classAuth, model)

    propId = model.propertyId
    propIdDesc = clazz.__dict__[propId]
    assert isinstance(propIdDesc, Property)
    propIdType = typeFor(propIdDesc.reference)

    propIdTypeAuth = TypeModelPropertyAuth(typeModelAuth, propIdType)
    propIdDescAuth = Property(propIdDesc.type, Reference(propIdTypeAuth))

    setattr(classAuth, propId, propIdDescAuth)

    classAuth._ally_type = typeModelAuth
    clazz._ally_authentificated = classAuth
    return typeModelAuth
