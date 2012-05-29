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

    __slots__ = TypeModel.__slots__ + ('_childTypeId',)

    def __init__(self, clazz, container):
        '''
        Constructs the authenticated type model based on the provided type model.
        
        @see: TypeModel.__init__
        '''
        TypeModel.__init__(self, clazz, container)
        self._childTypeId = None

    def childTypeId(self):
        '''
        @see: TypeModel.childTypeId
        '''
        if self._childTypeId is None:
            typ = super().childTypeFor(self.container.propertyId)
            assert isinstance(typ, TypeModelProperty)
            self._childTypeId = TypeModelPropertyAuth(self, typ.property, typ.type)
        return self._childTypeId

    def childTypeFor(self, name):
        '''
        @see: TypeModel.childTypeFor
        '''
        if name == self.container.propertyId: return self.childTypeId()
        return super().childTypeFor(name)

    def __hash__(self):
        '''
        @see: Type.__hash__
        '''
        return super().__hash__()

    def __eq__(self, other):
        '''
        @see: Type.__eq__
        '''
        if isinstance(other, TypeModel): return self.clazz == other.clazz
        return False

class TypeModelPropertyAuth(TypeModelProperty, IAuthenticated):
    '''
    Provides the type model property that is marked to be authenticated.
    '''
    __slots__ = TypeModelProperty.__slots__

    def __init__(self, parent, property, type):
        '''
        Constructs the authenticated type model based on the provided type model.
        
        @see: TypeModelProperty.__init__
        '''
        TypeModelProperty.__init__(self, parent, property, type)

    def __hash__(self):
        '''
        @see: Type.__hash__
        '''
        return super().__hash__()

    def __eq__(self, other):
        '''
        @see: Type.__eq__
        '''
        if isinstance(other, TypeModelProperty):
            return self.parent == other.parent and self.property == other.property
        return False

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
        Type.__init__(self, False, False)

        self.type = type

    def isOf(self, type):
        '''
        @see: Type.isOf
        '''
        return self == type or self.type.isOf(type)

    def isValid(self, obj):
        '''
        @see: Type.isValid
        '''
        return self.type.isValid(obj)

    def __hash__(self):
        '''
        @see: Type.__hash__
        '''
        return hash(self.type)

    def __eq__(self, other):
        '''
        @see: Type.__eq__
        '''
        if isinstance(other, self.__class__):
            return self.type == other.type
        return False

    def __str__(self):
        '''
        @see: Type.__str__
        '''
        return 'auth<%s>' % self.type

