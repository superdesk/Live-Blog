'''
Created on May 10, 2012

@package: ally authentication
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the types that are authenticated.
'''

from ally.api.operator.type import TypeModel, TypeModelProperty
from ally.api.type import Type

# --------------------------------------------------------------------

class IAuthenticated:
    '''
    Specification class used to mark the authenticated types.
    '''

class TypeModelAuth(TypeModel, IAuthenticated):
    '''
    Provides the type model that is marked to be authenticated.
    '''

    def __init__(self, forClass, container):
        '''
        Constructs the authenticated type model based on the provided type model.
        
        @see: TypeModel.__init__
        '''
        TypeModel.__init__(self, forClass, container)

class TypeModelPropertyAuth(TypeModelProperty, IAuthenticated):
    '''
    Provides the type model property that is marked to be authenticated.
    '''

    def __init__(self, parent, typeProperty):
        '''
        Constructs the authenticated type model based on the provided type model.
        
        @see: TypeModelProperty.__init__
        
        @param typeProperty: TypeModelProperty
            The type model property that is the based of the authenticated type.
        '''
        assert isinstance(typeProperty, TypeModelProperty), 'Invalid type model property %s' % typeProperty
        TypeModelProperty.__init__(self, parent, typeProperty.property, typeProperty.type)

# --------------------------------------------------------------------

class TypeAuthentication(Type):
    '''
    Used in marking the authentication object value in the invokers inputs.
    '''

    def __init__(self, type):
        '''
        Constructs the authentication type.
        @see: Type.__init__
        
        @param type: TypeModel|TypeModelProperty
            The type of the authentication.
        '''
        assert isinstance(type, (TypeModel, TypeModelProperty)), 'Invalid type %s' % type
        Type.__init__(self, type.forClass, False, False)
