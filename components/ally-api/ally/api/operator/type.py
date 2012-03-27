'''
Created on Mar 13, 2012

@package: ally api
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the operator types.
'''

from ..type import Type
from .container import Model, Container, Query, Criteria
from ally.api.operator.container import Service
from ally.api.type import typeFor
from inspect import isclass

# --------------------------------------------------------------------

class TypeContainer(Type):
    '''
    Provides the type for the properties container.
    '''

    __slots__ = Type.__slots__ + ('container',)

    def __init__(self, forClass, container):
        '''
        Constructs the container type for the provided container.
        @see: Type.__init__
        
        @param forClass: class
            The class associated with the container.
        @param container: Container
            The container that this type is constructed on.
        '''
        assert isinstance(container, Container), 'Invalid container provided %s' % container
        Type.__init__(self, forClass, False, True)

        self.container = container

class TypeModel(TypeContainer):
    '''
    Provides the type for the model.
    '''

    __slots__ = TypeContainer.__slots__ + ('baseClass',)

    def __init__(self, forClass, container, baseClass=None):
        '''
        Constructs the model type for the provided model.
        @see: Type.__init__
        
        @param forClass: class
            The model class associated with the model.
        @param container: Model
            The model that this type is constructed on.
        @param baseClass: class
            The base model class, a super type of the for class that needs to be considered valid for this model.
            This is used whenever a model is mapped to also validate classes that are API standard.
        '''
        assert isinstance(container, Model), 'Invalid model provided %s' % container
        assert baseClass is None or isclass(baseClass), 'Invalid base class %s' % baseClass
        TypeContainer.__init__(self, forClass, container)
        self.baseClass = baseClass

    def isOf(self, type):
        '''
        @see: Type.isOf
        '''
        if TypeContainer.isOf(self, type): return True
        if self.baseClass and isclass(type): return issubclass(type, self.baseClass)
        return False

    def isValid(self, obj):
        '''
        @see: Type.isValid
        '''
        if TypeContainer.isValid(self, obj): return True
        if self.baseClass: return isinstance(obj, self.baseClass)
        return False

class TypeCriteria(TypeContainer):
    '''
    Provides the type for the criteria.
    '''

    __slots__ = TypeContainer.__slots__

    def __init__(self, forClass, container):
        '''
        Constructs the criteria type for the provided criteria.
        @see: Type.__init__
        
        @param forClass: class
            The model class associated with the model.
        @param container: Criteria
            The criteria that this type is constructed on.
        '''
        assert isinstance(container, Criteria), 'Invalid criteria provided %s' % container
        TypeContainer.__init__(self, forClass, container)

class TypeQuery(Type):
    '''
    Provides the type for the query.
    '''

    __slots__ = Type.__slots__ + ('query',)

    def __init__(self, forClass, query):
        '''
        Constructs the query type for the provided query.
        @see: Type.__init__
        
        @param forClass: class
            The class associated with the query.
        @param query: Query
            The query that this type is constructed on.
        '''
        assert isinstance(query, Query), 'Invalid query %s' % query
        Type.__init__(self, forClass, False, False)

        self.query = query

# --------------------------------------------------------------------

class TypeProperty(Type):
    '''
    This type is used to wrap a container property as types.
    '''

    __slots__ = Type.__slots__ + ('parent', 'property', 'container', 'type')

    def __init__(self, parent, property, type=None):
        '''
        Constructs the property type for the provided property name and parent container type.
        @see: Type.__init__
        
        @param parent: TypeContainer
            The container of the property type.
        @param property: string
            The property name that this type represents.
        @param type: Type|None
            The type used by the property for validation, if not provided than it will use the type specified in the
            container.
        '''
        assert isinstance(parent, TypeContainer), 'Invalid container type %s' % parent
        assert isinstance(property, str), 'Invalid property %s' % property
        assert property in parent.container.properties, \
        'Property %s is not contained in container %s' % (property, parent.container)
        assert type is None or isinstance(type, Type), 'Invalid type %s' % type

        self.parent = parent
        self.property = property
        self.container = parent.container
        self.type = type or self.container.properties[property]
        Type.__init__(self, self.type.forClass, False, True)

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
        return hash((self.parent, self.property))

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.parent == other.parent and self.property == other.property
        return False

    def __str__(self):
        return '%s.%s' % (self.parent, self.property)

class TypeModelProperty(TypeProperty):
    '''
    This type is used to wrap a model property as types.
    '''

    __slots__ = TypeProperty.__slots__

    def __init__(self, parent, property, type=None):
        '''
        Constructs the property type for the provided property name and parent container type.
        @see: TypeProperty.__init__
        
        @param parent: TypeModel
            The model of the property type.
        '''
        assert isinstance(parent, TypeModel), 'Invalid model type %s' % parent
        TypeProperty.__init__(self, parent, property, type)

class TypeCriteriaEntry(Type):
    '''
    This type is used to wrap a query criteria as types.
    '''

    __slots__ = Type.__slots__ + ('parent', 'name', 'criteriaType', 'criteria')

    def __init__(self, parent, name):
        '''
        Constructs the criteria type for the provided criteria name and parent query type.
        @see: Type.__init__
        
        @param parent: TypeQuery
            The query type of the criteria type.
        @param name: string
            The criteria name represented by the type.
        '''
        assert isinstance(parent, TypeQuery), 'Invalid query type %s' % parent
        assert isinstance(name, str), 'Invalid name %s' % name
        assert name in parent.query.criterias, \
        'Criteria %s is not contained in query %s' % (name, parent.query)

        self.parent = parent
        self.name = name
        self.criteriaType = typeFor(parent.query.criterias[name])
        assert isinstance(self.criteriaType, TypeCriteria), 'Invalid criteria class %s' % self.criteriaClass
        self.criteria = self.criteriaType.container
        Type.__init__(self, self.criteriaType.forClass, False, False)

    def __hash__(self):
        return hash((self.parent, self.name))

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.parent == other.parent and self.name == other.name
        return False

    def __str__(self):
        return '%s.%s' % (self.parent, self.name)

# --------------------------------------------------------------------

class TypeService(Type):
    '''
    Provides the type for the service.
    '''

    __slots__ = Type.__slots__ + ('service',)

    def __init__(self, forClass, service):
        '''
        Constructs the service type for the provided service.
        @see: Type.__init__
        
        @param forClass: class
            The class associated with the container.
        @param service: Service
            The service that this type is constructed on.
        '''
        assert isinstance(service, Service), 'Invalid service provided %s' % service
        Type.__init__(self, forClass, False, False)

        self.service = service
