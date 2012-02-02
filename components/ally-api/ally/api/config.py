'''
Created on Jan 19, 2012

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Nistor Gabriel

Provides the decorators used for APIs in a much easier to use form.
'''

from ally.api.configure import APIModel, APIQuery, APICriteria, APIService, \
    APICall
from functools import partial
from inspect import isclass, isfunction

# --------------------------------------------------------------------

def model(*args, name=None, **hints):
    '''
    Used for decorating classes that are API models.
    @see: APIModel
    
    ex:
        @model
        class Entity:
    
            name = APIProperty(Integer)
            
    @param name: string|None
        Provide a name under which the model will be known. If not provided the name of the model is the class name.
    '''
    if not args: return partial(model, name=name, **hints)
    assert len(args) == 1, 'Expected only one argument that is the decorator class, got %s arguments' % len(args)
    clazz = args[0]
    assert isclass(clazz), 'Invalid class %s' % clazz
    return APIModel(name, **hints)(clazz)

def query(*args):
    '''
    Used for decorating classes that are API queries.
    @see: APIQuery
    
    ex:
        @query
        class ThemeQuery:
            
            name = OrderBy
    '''
    if not args: return partial(query)
    assert len(args) == 1, 'Expected only one argument that is the decorator class, got %s arguments' % len(args)
    clazz = args[0]
    assert isclass(clazz), 'Invalid class %s' % clazz
    return APIQuery()(clazz)

def criteria(*args):
    '''
    Used for decorating classes that are API criteria's.
    @see: APICriteria
    
    ex:
        @criteria
        class OrderBy:
    
            order = APIProperty(bool)
    '''
    if not args: return partial(criteria)
    assert len(args) == 1, 'Expected only one argument that is the decorator class, got %s arguments' % len(args)
    clazz = args[0]
    assert isclass(clazz), 'Invalid class %s' % clazz
    return APICriteria()(clazz)

def service(*args, generic=None):
    '''
    Used for decorating classes that are API services.
    @see: APIService
    
    ex:
        @service
        class IEntityService:
    
            @call(Number, Entity.x)
            def multipy(self, x):
            
        
        @service((Entity, Issue))
        class IInheritingService(IEntityService):
    
            @call(Number, Issue.x)
            def multipy(self, x):
            
    @param generic: tuple|list((genericClass, replaceClass)|[...(genericClass, replaceClass)])
        The classes of that will be generically replaced. Can also be provided as arguments.
    '''
    if not args: return partial(service, generic=generic)
    assert not generic or isinstance(generic, (tuple, list)), 'Invalid generic %s' % generic
    if isclass(args[0]):
        assert len(args) == 1, 'Expected only one argument that is the decorator class, got %s arguments' % len(args)
        return APIService(*(generic or ()))(args[0])
    return partial(service, generic=args)

def call(*args, types=None, **hints):
    '''
    Used for decorating service methods that are used as APIs.
    @see: APICall
    
    ex:
        @call
        def updateX(self, x:int)->None:
            doc string
            <no method body required>
            
        @call(Entity, Entity.x, String, webName='unassigned')
        def findBy(self, x, name):
            doc string
            <no method body required>
            
        @call(Entity, Entity, OtherEntity, method=UPDATE, replaceFor=IAnotherService)
        def assign(self, entity, toEntity):
            doc string
            <no method body required>
            
    @param types: tuple|list(Type|Type reference)
        On the first position it will be considered the output type then the input types expected for the
        service call. Can also be provided as arguments.
    @param hints: key arguments
        Provides hints for the call, supported parameters:
            @keyword method: integer
                One of the operator module constants GET, INSERT, UPDATE, DELETE.
    '''
    if not args: return partial(call, types=types, **hints)
    assert not types or isinstance(types, (tuple, list)), 'Invalid types %s' % types
    if isfunction(args[0]):
        assert len(args) == 1, \
        'Expected only one argument that is the decorator function, got %s arguments' % len(args)
        return APICall(*(types or ()), **hints)(args[0])
    return partial(call, types=args, **hints)
