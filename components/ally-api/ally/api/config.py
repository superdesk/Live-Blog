'''
Created on Jan 19, 2012

@package: ally api
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the decorators used for APIs in a much easier to use form.
'''

from .operator.container import Call, Service, Criteria, Query, Model, Container
from .operator.descriptor import Property, Reference, CriteriaEntry, \
    ContainerSupport, CriteriaSupport, QuerySupport
from .operator.extract import extractCriterias, extractProperties, \
    extractPropertiesInherited, extractContainersFrom, extractCriteriasInherited, \
    extractOuputInput, processGenericCall
from .operator.type import TypeModel, TypeProperty, TypeModelProperty, \
    TypeCriteria, TypeQuery, TypeCriteriaEntry, TypeService, TypeExtension
from .type import typeFor
from abc import ABCMeta, abstractmethod
from ally.api.type import List
from ally.exception import DevelError
from ally.support.util_sys import locationStack
from inspect import isclass, isfunction
from re import match
import logging

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

RULE_EXTENSION_PROPERTY = ('^[a-z]{1,}[\w]*$',
                           'The extension property name needs to start with a lower case, got "%s"')

# The available method actions.
GET = 1 << 1
INSERT = 1 << 2
UPDATE = 1 << 3
DELETE = 1 << 4

# The default limit
LIMIT_DEFAULT = 30

# The function name to method mapping.
NAME_TO_METHOD = {
                  '(^get[\w]*$)|(^find[\w]*$)':GET,
                  '(^insert[\w]*$)|(^persist[\w]*$)':INSERT,
                  '(^update[\w]*$)|(^merge[\w]*$)':UPDATE,
                  '(^delete[\w]*$)|(^remove[\w]*$)':DELETE
                  }

# --------------------------------------------------------------------

def model(*args, id=None, name=None, **hints):
    '''
    Used for decorating classes that are API models.
    
    ex:
        @model
        class Entity:
    
            Name = String
        
        @model(name=Entity)
        class Entity2(Entity):
    
            NewProperty = Integer

    @param id: string|None
        The name of the property to be considered the model id, if the id is not specified then the model will
        be limited in usage.
    @param name: string|None
        Provide a name under which the model will be known. If not provided the name of the model is the class name.
    @param hints: key word arguments
        Provides hints for the model.
        @keyword replace: class
            The model class to be replaced by this model class, should only be used whenever you need to prototype a
            model in order to be fully defined latter.
    '''
    def decorator(clazz):
        assert isclass(clazz), 'Invalid class %s' % clazz
        nonlocal id, name, hints
        
        if name is not None:
            if isclass(name):
                typ = typeFor(name)
                assert isinstance(typ, TypeModel), 'Invalid class %s to extract name, is not a model class' % name
                name = typ.container.name
            assert isinstance(name, str), 'Invalid model name %s' % name
        else:
            name = clazz.__name__
        if not match(RULE_MODEL[0], name): raise DevelError(RULE_MODEL[1] % name)
    
        containers = extractContainersFrom(clazz.__bases__, TypeModel)
        if id is None:
            for model in containers:
                assert isinstance(model, Model)
                if model.propertyId is not None:
                    id = model.propertyId
                    log.info('Inherited id \'%s\' for class %s', id, clazz)
                    break
            else: log.info('No id to be inherited for class %s', clazz)
                
        containers.reverse()  # We reverse since the priority is from first class to last
        properties, hintsInherited = {}, {}
        for model in containers:
            properties.update(model.properties)
            hintsInherited.update(model.hints)
        
        log.info('Extracted inherited properties %s and hints %s for class %s', properties, hintsInherited, clazz)
        
        properties.update(extractProperties(clazz.__dict__))
        hintsInherited.update(hints)
        hints = hintsInherited

        log.info('Extracted model properties %s and hints %s for class %s', properties, hints, clazz)
        for prop, typ in properties.items():
            if not match(RULE_MODEL_PROPERTY[0], prop): raise DevelError(RULE_MODEL_PROPERTY[1] % prop)
            if not (isinstance(typ, TypeModel) or typ.isPrimitive):
                raise DevelError('Invalid type %s for property \'%s\', only primitives or models allowed' % (typ, prop))
    
        replace = hints.pop('replace', None)
        if id is not None:
            assert isinstance(id, str), 'Invalid property id %s' % id
            assert id in properties, 'Invalid property id %s is not in model properties' % id
    
        if id is not None:
            if isinstance(properties[id], List):
                raise DevelError('The id cannot be a List type, got %s' % properties[id])
            if isinstance(properties[id], TypeModel):
                raise DevelError('The id cannot be a model reference, got %s' % properties[id])
    
        modelType = TypeModel(clazz, Model(properties, name, id, hints))
        if replace:
            assert isclass(replace), 'Invalid class %s' % replace
            typ = typeFor(replace)
            if not isinstance(typ, TypeModel): raise DevelError('Invalid replace class %s, not a model class' % replace)
            if clazz.__module__ != replace.__module__:
                raise DevelError('Replace is available only for classes in the same API module invalid replace class '
                                 '%s for replaced class' % (replace, clazz))
            typ.clazz = clazz
            typ.container = modelType.container
    
        reference = {}
        for prop, typ in properties.items():
            propType = TypeModelProperty(modelType, prop)
            reference[prop] = Reference(propType)
            if isinstance(typ, TypeModel):
                propType = TypeModelProperty(modelType, prop, typ.container.properties[typ.container.propertyId])
            setattr(clazz, prop, Property(propType))
    
        clazz._ally_type = modelType  # This specified the detected type for the model class by using 'typeFor'
        clazz._ally_reference = reference  # The references to be returned by the properties when used only with class
        clazz.__new__ = ContainerSupport.__new__
        clazz.__str__ = ContainerSupport.__str__
        clazz.__contains__ = ContainerSupport.__contains__
    
        return clazz
    if args: return decorator(*args)
    return decorator

def alias(*args, name=None, **hints):
    '''
    Used for decorating classes that are used as aliases of API models. The aliases can only be used as input parameters.
    
    ex:
        @alias
        class EntityAlias(Entity):
            !No definitions is allowed
    
    @param name: string|None
        Provide a name under which the alias will be known. If not provided the name of the alias is the class name.
    @param hints: key word arguments
        Provides hints for the alias.
    '''
    # TODO: implement alias
    return model(*args, name=name, **hints)

def criteria(*args, main=None):
    '''
    Used for decorating classes that are API criteria's.
    
    ex:
        @criteria(main='order')
        class OrderBy:
    
            order = bool
            
    @param main: string|tuple(string)|list[string]|None
        Provide the name of the property/properties that is to be considered the main property for the criteria. 
        The main property/properties is the property/properties used whenever the criteria is used without a property. 
        If the main property is None then it will be inherited if is the case from super criteria's otherwise is left
        unset.
    '''
    def decorator(clazz):
        assert isclass(clazz), 'Invalid class %s' % clazz
        nonlocal main
    
        properties = extractPropertiesInherited(clazz.__bases__, TypeCriteria)
        log.info('Extracted criteria inherited properties %s for class %s', properties, clazz)
        properties.update(extractProperties(clazz.__dict__))
        log.info('Extracted criteria properties %s for class %s', properties, clazz)
        for prop, typ in properties.items():
            if not match(RULE_CRITERIA_PROPERTY[0], prop): raise DevelError(RULE_CRITERIA_PROPERTY[1] % prop)
            if not typ.isPrimitive:
                raise DevelError('Invalid type %s for property \'%s\', only primitives allowed' % (typ, prop))
    
        if main is not None:
            if isinstance(main, str): main = [main]
        else:
            inherited = extractContainersFrom(clazz.__bases__, TypeCriteria)
            for crt in inherited:
                assert isinstance(crt, Criteria)
                if crt.main:
                    main = crt.main
                    break
            else: main = ()
    
        criteriaContainer = Criteria(properties, main)
        criteriaType = TypeCriteria(clazz, criteriaContainer)
    
        reference = {}
        for prop in criteriaContainer.properties:
            propType = TypeProperty(criteriaType, prop)
            reference[prop] = Reference(propType)
            setattr(clazz, prop, Property(propType))
    
        clazz._ally_type = criteriaType  # This specified the detected type for the model class by using 'typeFor'
        clazz._ally_reference = reference  # The references to be returned by the properties when used only with class
        clazz.__new__ = CriteriaSupport.__new__
        clazz.__str__ = CriteriaSupport.__str__
        clazz.__contains__ = CriteriaSupport.__contains__
    
        return clazz
    if args: return decorator(*args)
    return decorator

def query(owner):
    '''
    Used for decorating classes that are API queries.
    
    @param owner: TypeModel container
        The model that is the target of this query.
    
    ex:
        @query(Theme)
        class ThemeQuery:
            
            name = OrderBy
    '''
    queryOwner = typeFor(owner)
    assert isinstance(queryOwner, TypeModel), 'Invalid owner %s, has no type model' % owner

    def decorator(clazz):
        assert isclass(clazz), 'Invalid class %s' % clazz

        criterias = extractCriteriasInherited(clazz.__bases__)
        log.info('Extracted inherited criterias %s for query class %s', criterias, clazz)
        criterias.update(extractCriterias(clazz.__dict__))
        log.info('Extracted criterias %s for query class %s', criterias, clazz)
        for crt in criterias:
            if not match(RULE_QUERY_CRITERIA[0], crt): raise DevelError(RULE_QUERY_CRITERIA[1] % crt)

        queryContainer = Query(criterias)
        queryType = TypeQuery(clazz, queryContainer, queryOwner)

        for crt in queryContainer.criterias:
            critType = TypeCriteriaEntry(queryType, crt)
            setattr(clazz, crt, CriteriaEntry(critType))

        clazz._ally_type = queryType  # This specified the detected type for the model class by using 'typeFor'
        clazz.__new__ = QuerySupport.__new__
        clazz.__str__ = QuerySupport.__str__
        clazz.__contains__ = QuerySupport.__contains__

        return clazz

    return decorator

def call(*args, method=None, **hints):
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

    @param method: integer
        One of the config module constants GET, INSERT, UPDATE, DELETE.
    @param hints: key arguments
        Provides hints for the call, the hints are used for assembly.
            @keyword exposed: boolean
                Indicates that the call is exposed for external interactions, usually all defined methods in a service
                that are not decorated with call are considered unexposed calls.
    '''
    function = None
    if not args: types = None
    elif not isfunction(args[0]): types = args
    else:
        types = None
        assert len(args) == 1, \
        'Expected only one argument that is the decorator function, got %s arguments' % len(args)
        function = args[0]

    def decorator(function):
        assert isfunction(function), 'Invalid function %s' % function
        nonlocal method
        name = function.__name__
        if method is None:
            for regex, m in NAME_TO_METHOD.items():
                if match(regex, name):
                    method = m
                    break
            else: raise DevelError('Cannot deduce method for function name "%s"' % name)

        output, inputs = extractOuputInput(function, types, modelToId=method in (GET, DELETE))

        function._ally_call = Call(name, method, output, inputs, hints)
        return abstractmethod(function)

    if function is not None: return decorator(function)
    return decorator

def service(*generic):
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
            
    @param generic: arguments((genericClass, replaceClass)|[...(genericClass, replaceClass)])
        The classes of that will be generically replaced. Can also be provided as arguments.
    '''
    if generic:
        if len(generic) == 1 and isclass(generic[0]):
            clazz = generic[0]
            generic = {}
        else:
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
            clazz = None
    else:
        generic = {}
        clazz = None

    def decorator(clazz):
        assert isclass(clazz), 'Invalid class %s' % clazz
    
        calls = []
        for name, function in clazz.__dict__.items():
            if isfunction(function):
                try: calls.append(function._ally_call)
                except AttributeError: raise DevelError('No call for method at:\n%s' % locationStack(function))
                del function._ally_call
    
        services = [typeFor(base) for base in clazz.__bases__]
        services = [typ.service for typ in services if isinstance(typ, TypeService)]
        names = {call.name for call in calls}
        for srv in services:
            assert isinstance(srv, Service)
            for name, call in srv.calls.items():
                assert isinstance(call, Call)
                if name not in names:
                    calls.append(processGenericCall(call, generic))
                    names.add(name)
    
        service = Service(calls)
        if type(clazz) != ABCMeta:
            attributes = dict(clazz.__dict__)
            attributes.pop('__dict__', None)  # Removing __dict__ since is a reference to the old class dictionary.
            attributes.pop('__weakref__', None)
            clazz = ABCMeta(clazz.__name__, clazz.__bases__, attributes)
        abstract = set(clazz.__abstractmethods__)
        abstract.update(service.calls)
        clazz.__abstractmethods__ = frozenset(abstract)
    
        clazz._ally_type = TypeService(clazz, service)
        # This specified the detected type for the model class by using 'typeFor'
        return clazz
    if clazz: return decorator(clazz)
    return decorator

def extension(*args):
    '''
    Used for decorating classes that are API extensions. The extension is used as a model but only with primitive
    properties that is rendered in the response in different manners. Also the extension is not specified in the API
    and can be returned by the implementation in a dynamic manner.
    
    ex:
        @extension
        class CollectionWithTotal(Iterable):
    
            total = int
            
            def __init__(self, iter):
                self.iter = iter
                
            def __iter__(self): return self.iter()
    '''
    def decorator(clazz):
        assert isclass(clazz), 'Invalid class %s' % clazz
    
        properties = extractPropertiesInherited(clazz.__bases__, TypeExtension)
        log.info('Extracted extension inherited properties %s for class %s', properties, clazz)
        properties.update(extractProperties(clazz.__dict__))
        log.info('Extracted extension properties %s for class %s', properties, clazz)
        for prop, typ in properties.items():
            if not match(RULE_EXTENSION_PROPERTY[0], prop): raise DevelError(RULE_EXTENSION_PROPERTY[1] % prop)
            if not typ.isPrimitive:
                raise DevelError('Invalid type %s for property \'%s\', only primitives allowed' % (typ, prop))
    
        extensionContainer = Container(properties)
        extensionType = TypeExtension(clazz, extensionContainer)
    
        reference = {}
        for prop in extensionContainer.properties:
            propType = TypeProperty(extensionType, prop)
            reference[prop] = Reference(propType)
            setattr(clazz, prop, Property(propType))
    
        clazz._ally_type = extensionType  # This specified the detected type for the model class by using 'typeFor'
        clazz._ally_reference = reference  # The references to be returned by the properties when used only with class
        clazz.__new__ = ContainerSupport.__new__
    
        return clazz
    if args: return decorator(*args)
    return decorator
