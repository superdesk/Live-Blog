'''
Created on Jan 19, 2012

@package: ally api
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the decorators used for APIs in a much easier to use form.
'''

from .operator.container import Call, Service, Criteria, Query, Model
from .operator.descriptor import Property, Reference, CriteriaEntry
from .operator.extract import extractCriterias, extractProperties, \
    extractPropertiesInherited, extractContainersFrom, \
    extractCriteriasInherited, extractOuputInput, processGenericCall
from .operator.type import TypeModel, TypeProperty, TypeModelProperty, TypeCriteria, TypeQuery, \
    TypeCriteriaEntry, TypeService
from .type import typeFor
from abc import ABCMeta, abstractmethod
from ally.exception import DevelError
from functools import partial
from inspect import isclass, isfunction
from re import match
import logging
from ally.api.operator.descriptor import ContainerSupport, CriteriaSupport, \
    QuerySupport

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# Defines the naming rules for the API configured classes.
RULE_MODEL = ('^[A-Z]{1,}[A-Za-z0-9]*$',
              'The model name needs to start with an upper case and be camel letter format, got "%s"')

RULE_MODEL_PROPERTY = ('^[A-Z]{1,}[A-Za-z0-9]*$',
                       'The model property name needs to start with an upper case and be camel letter format, got "%s"')

RULE_CRITERIA_PROPERTY = ('^[a-z]{1,}[\w]*$',
                          'The criteria property name needs to start with a lower case, got "%s"')

RULE_QUERY_CRITERIA = ('^[a-z]{1,}[\w]*$',
                       'The query criteria name needs to start with a lower case, got "%s"')

# The available method actions.
GET = 1
INSERT = 2
UPDATE = 4
DELETE = 8

# The function name to method mapping.
NAME_TO_METHOD = {
                  '(^get[\w]*$)|(^find[\w]*$)':GET,
                  '(^insert[\w]*$)|(^persist[\w]*$)':INSERT,
                  '(^update[\w]*$)|(^merge[\w]*$)':UPDATE,
                  '(^delete[\w]*$)|(^remove[\w]*$)':DELETE
                  }

# --------------------------------------------------------------------

def model(*args, name=None, **hints):
    '''
    Used for decorating classes that are API models.
    
    ex:
        @model
        class Entity:
    
            Name = String
        
        @model(name=Entity)
        class Entity2(Entity):
    
            NewProperty = Integer
            
    @param name: string|None
        Provide a name under which the model will be known. If not provided the name of the model is the class name.
    @param hints: key word arguments
        Provides hints for the model.
        @keyword id: string
            The name of the property to be considered the model id.
        @keyword replace: class
            The model class to be replaced by this model class, should only be used whenever you need to prototype a
            model in order to be fully defined latter.
    '''
    if not args: return partial(model, name=name, **hints)
    assert len(args) == 1, 'Expected only one argument that is the decorator class, got %s arguments' % len(args)
    clazz = args[0]
    assert isclass(clazz), 'Invalid class %s' % clazz

    if name is not None:
        if isclass(name):
            typ = typeFor(name)
            assert isinstance(typ, TypeModel), 'Invalid class %s to extract name, is not a model class' % name
            name = typ.container.name
        assert isinstance(name, str), 'Invalid model name %s' % name
    else:
        name = clazz.__name__
    if not match(RULE_MODEL[0], name): raise DevelError(RULE_MODEL[1] % name)

    properties = extractPropertiesInherited(clazz.__bases__, TypeModel)
    log.info('Extracted model inherited properties %s for class %s', properties, clazz)
    properties.update(extractProperties(clazz.__dict__))
    log.info('Extracted model properties %s for class %s', properties, clazz)
    for prop, typ in properties.items():
        if not match(RULE_MODEL_PROPERTY[0], prop): raise DevelError(RULE_MODEL_PROPERTY[1] % prop)
        if not (isinstance(typ, TypeModel) or typ.isPrimitive):
            raise DevelError('Invalid type %s for property \'%s\', only primitives or models allowed' % (typ, prop))

    propertyId, replace = hints.pop('id', None), hints.pop('replace', None)
    if propertyId is not None:
        assert isinstance(propertyId, str), 'Invalid property id %s' % propertyId
        assert propertyId in properties, 'Invalid property id %s is not in model properties' % propertyId
    else:
        typ = typeFor(clazz)
        if not isinstance(typ, TypeModel): raise DevelError('There is no id specified for %s' % clazz)
        assert isinstance(typ, TypeModel)
        propertyId = typ.container.propertyId

    modelType = TypeModel(clazz, Model(properties, propertyId, name, hints))
    if replace:
        assert isclass(replace), 'Invalid class %s' % replace
        typ = typeFor(replace)
        if not isinstance(typ, TypeModel): raise DevelError('Invalid replace class %s, not a model class' % replace)
        if clazz.__module__ != replace.__module__:
            raise DevelError('Replace is available only for classes in the same API module invalid replace class '
                             '%s for replaced class' % (replace, clazz))
        typ.forClass = clazz
        typ.container = modelType.container

    for prop, typ in properties.items():
        propType = propRefType = TypeModelProperty(modelType, prop)
        if isinstance(typ, TypeModel):
            propType = TypeModelProperty(modelType, prop, typ.container.properties[typ.container.propertyId])
        setattr(clazz, prop, Property(propType, Reference(propRefType)))

    clazz._ally_type = modelType # This specified the detected type for the model class by using 'typeFor'
    clazz.__new__ = ContainerSupport.__new__
    clazz.__repr__ = ContainerSupport.__repr__
    clazz.__contains__ = ContainerSupport.__contains__

    return clazz

def criteria(*args, main=None):
    '''
    Used for decorating classes that are API criteria's.
    
    ex:
        @criteria(main='order')
        class OrderBy:
    
            order = bool
            
    @param main: string|None
        Provide the name of the property that is to be considered the main property for the criteria. The main property
        is the property used whenever the criteria is used without a property. If the main property is None then it will
        be inherited if is the case from super criteria's otherwise is left unset.
    '''
    if not args: return partial(criteria, main=main)
    assert len(args) == 1, 'Expected only one argument that is the decorator class, got %s arguments' % len(args)
    clazz = args[0]
    assert isclass(clazz), 'Invalid class %s' % clazz

    properties = extractPropertiesInherited(clazz.__bases__, TypeCriteria)
    log.info('Extracted criteria inherited properties %s for class %s', properties, clazz)
    properties.update(extractProperties(clazz.__dict__))
    log.info('Extracted criteria properties %s for class %s', properties, clazz)
    for prop, typ in properties.items():
        if not match(RULE_CRITERIA_PROPERTY[0], prop): raise DevelError(RULE_CRITERIA_PROPERTY[1] % prop)
        if not typ.isPrimitive:
            raise DevelError('Invalid type %s for property \'%s\', only primitives allowed' % (typ, prop))

    if main is not None:
        assert isinstance(main, str), 'Invalid main property name %s' % main
        assert main in properties, 'Invalid main property %s is not in criteria properties' % main
    else:
        inherited = extractContainersFrom(clazz.__bases__, TypeCriteria)
        for crt in inherited:
            assert isinstance(crt, Criteria)
            if crt.main:
                main = crt.main
                break

    criteriaContainer = Criteria(properties, main)
    criteriaType = TypeCriteria(clazz, criteriaContainer)

    for prop in criteriaContainer.properties:
        propType = TypeProperty(criteriaType, prop)
        setattr(clazz, prop, Property(propType, Reference(propType)))

    clazz._ally_type = criteriaType # This specified the detected type for the model class by using 'typeFor'
    clazz.__new__ = CriteriaSupport.__new__
    clazz.__repr__ = CriteriaSupport.__repr__
    clazz.__contains__ = CriteriaSupport.__contains__

    return clazz

def query(*args):
    '''
    Used for decorating classes that are API queries.
    
    ex:
        @query
        class ThemeQuery:
            
            name = OrderBy
    '''
    if not args: return partial(query)
    assert len(args) == 1, 'Expected only one argument that is the decorator class, got %s arguments' % len(args)
    clazz = args[0]
    assert isclass(clazz), 'Invalid class %s' % clazz

    criterias = extractCriteriasInherited(clazz.__bases__)
    log.info('Extracted inherited criterias %s for query class %s', criterias, clazz)
    criterias.update(extractCriterias(clazz.__dict__))
    log.info('Extracted criterias %s for query class %s', criterias, clazz)
    for crt in criterias:
        if not match(RULE_QUERY_CRITERIA[0], crt): raise DevelError(RULE_QUERY_CRITERIA[1] % crt)

    queryContainer = Query(criterias)
    queryType = TypeQuery(clazz, queryContainer)

    for crt in queryContainer.criterias:
        critType = TypeCriteriaEntry(queryType, crt)
        setattr(clazz, crt, CriteriaEntry(critType))

    clazz._ally_type = queryType # This specified the detected type for the model class by using 'typeFor'
    clazz.__new__ = QuerySupport.__new__
    clazz.__repr__ = QuerySupport.__repr__
    clazz.__contains__ = QuerySupport.__contains__

    return clazz

def call(*args, types=None, **hints):
    '''
    Used for decorating service methods that are used as APIs.
    
    ex:
        Using the annotations:
            @call
            def updateX(self, x:int)->None:
                doc string
                <no method body required>
                
        Using specified types:
            @call(Entity, Entity.x, String, webName='unassigned')
            def findBy(self, x, name):
                doc string
                <no method body required>
                
            @call(Entity, Entity, OtherEntity, method=UPDATE)
            def assign(self, entity, toEntity):
                doc string
                <no method body required>
            
    @param types: tuple|list(Type|Type reference)
        On the first position it will be considered the output type then the input types expected for the
        service call. Can also be provided as arguments.
    @param hints: key arguments
        Provides hints for the call, supported parameters:
            @keyword exposed: boolean
                Indicates that the call is exposed for external interactions, usually all defined methods in a service
                that are not decorated with call are considered unexposed calls.
            @keyword method: integer
                One of the config module constants GET, INSERT, UPDATE, DELETE.
    '''
    if not args: return partial(call, types=types, **hints)
    assert not types or isinstance(types, (tuple, list)), 'Invalid types %s' % types
    if not isfunction(args[0]): return partial(call, types=args, **hints)
    assert len(args) == 1, \
    'Expected only one argument that is the decorator function, got %s arguments' % len(args)
    function = args[0]
    assert isfunction(function), 'Invalid function %s' % function

    name, method = function.__name__, hints.pop('method', None)
    if method is None:
        for regex, m in NAME_TO_METHOD.items():
            if match(regex, name):
                method = m
                break
        else: raise DevelError('Cannot deduce method for function name "%s"' % name)

    output, inputs = extractOuputInput(function, types, modelToId=method in (GET, DELETE))

    function._ally_call = Call(name, method, output, inputs, hints)
    return abstractmethod(function)

def service(*args, generic=None):
    '''
    Used for decorating classes that are API services.
    
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
    if not isclass(args[0]): return partial(service, generic=args)
    assert len(args) == 1, 'Expected only one argument that is the decorator class, got %s arguments' % len(args)
    clazz = args[0]
    assert isclass(clazz), 'Invalid class %s' % clazz
    if generic:
        assert isinstance(generic, (tuple, list)), 'Invalid generic %s' % generic
        if __debug__:
            for gen in generic:
                assert isinstance(gen, (tuple, list)), 'Invalid generic entry %s' % gen
                assert len(gen) == 2, 'Invalid generic entry %s has to many entries %s, expected 2' % (gen, len(gen))
                replaced, replacer = gen
                assert isclass(replacer) and isinstance(typeFor(replacer), (TypeModel, TypeQuery)), \
                'Invalid replacer class %s in generic entry %s' % (replacer, gen)
                assert isclass(replaced) and isinstance(typeFor(replaced), (TypeModel, TypeQuery)), \
                'Invalid replaced class %s in generic entry %s' % (replaced, gen)
                assert issubclass(replacer, replaced), \
                'Invalid replacer class %s does not extend the replaced class %s' % (replacer, replaced)
        generic = dict(generic)
    else:
        generic = {}

    calls = []
    for name, function in clazz.__dict__.items():
        if isfunction(function):
            if not hasattr(function, '_ally_call'):
                fnc = function.__code__
                raise DevelError('No call for method at:\nFile "%s", line %i, in %s' %
                                 (fnc.co_filename, fnc.co_firstlineno, name))
            calls.append(function._ally_call)
            del function._ally_call

    services = [typeFor(base) for base in clazz.__bases__]
    services = [typ.service for typ in services if isinstance(typ, TypeService)]
    names = {call.name for call in calls}
    for srv in services:
        assert isinstance(srv, Service)
        for call in srv.calls:
            assert isinstance(call, Call)
            if call.name not in names:
                calls.append(processGenericCall(call, generic))
                names.add(call.name)

    if type(clazz) != ABCMeta:
        attributes = dict(clazz.__dict__)
        del attributes['__dict__'] # Removing __dict__ since is a reference to the old class dictionary.
        del attributes['__weakref__']
        clazz = ABCMeta(clazz.__name__, clazz.__bases__, attributes)
    abstract = set(clazz.__abstractmethods__)
    abstract.update({call.name for call in calls})
    clazz.__abstractmethods__ = frozenset(abstract)

    clazz._ally_type = TypeService(clazz, Service(calls))
    # This specified the detected type for the model class by using 'typeFor'
    return clazz
