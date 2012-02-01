'''
Created on Jun 1, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Nistor Gabriel

Provides the decorators used for APIs.
'''

from ..support.util import IS_PY3K, Attribute
from .operator import Call, Service, Criteria, Query, Model, Property, \
    CriteriaEntry, Properties, GET, INSERT, UPDATE, DELETE
from .type import TypeProperty, typeFor, TypeModel, List, Type, TypeQuery, Iter, \
    Input
from functools import wraps
from inspect import isfunction, isclass
import inspect
import logging

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

class APIModel:
    '''
    Used for decorating classes that are API models.
    
    ex:
        @APIModel()
        class Entity:
    
            name = APIProperty(Integer)
    '''
    
    def __init__(self, name=None):
        '''
        @param name: string
            Provide a name under which the model will be known.
        '''
        assert name is None or isinstance(name, str), 'Invalid model name %s' % name
        self.name = name
    
    def __call__(self, modelClass):
        '''
        What happens here is basically that the class that is considered an API model is first
        checked if it has any API properties, if that is the case than it will associate a model to this model class.
        
        @param modelClass: class
            The model class to be processed.
        @return: class
            The same model class.
        '''
        properties = _processProperties(modelClass)
        model = modelFor(modelClass)
        modelName = self.name or modelClass.__name__
        if model is None:
            # this is not an extended model
            assert not len(properties) == 0, 'There are no API properties on model class %s' % modelClass
            model = Model(modelClass, modelName, properties)
        else:
            assert isinstance(model, Model)
            # Cloning the inherited properties, since they have to belong now to this model.
            allProperties = {}
            for name, prop in model.properties.items():
                allProperties[name] = Property(prop.name, prop.type)
            allProperties.update(properties)
            model = Model(modelClass, modelName, allProperties)
            
        for name, typeProp in model.typeProperties.items():
            setattr(modelClass, name, typeProp)
        _init__original = getattr(modelClass, '__init__', None)
        def _init__model(self, *args, **keyargs):
            model = modelFor(self)
            assert isinstance(model, Model), 'Invalid model %s' % self
            for name in model.properties:
                self.__dict__[name] = None
            if _init__original:
                _init__original(self, *args, **keyargs)
        modelClass.__init__ = _init__model
        modelClass.__setattr__ = _setattr__properties
        modelClass.__delattr__ = _delattr__properties
        modelClass.__getstate__ = _getstate__properties
        modelClass.__contains__ = _contains__properties
        
        modelFor(modelClass, model)
        typeFor(modelClass, model.type)
    
        log.info('Created model %s for class %s containing %s API properties', model, modelClass, len(properties))
        return modelClass
        
# --------------------------------------------------------------------

class APIQuery:
    '''
    Used for decorating classes that are API queries.
    
    ex:
        @APIQuery()
        class ThemeQuery:
            
            name = OrderBy
    '''
    
    def __call__(self, queryClass):
        '''
        What happens here is basically that the class that is considered a API query is first
        checked if it has any entries declared, if that is the case than it associated a query to this class.
        
        @param queryClass: class
            The query class that contains the criteria class attributes.
        @return: class
            The query class processed.
        '''
        entries = _processEntries(queryClass)
        query = queryFor(queryClass)
        if query is None:
            # this is not an extended query
            query = Query(queryClass, entries)
        else:
            assert isinstance(query, Query)
            allEntries = {}
            allEntries.update(query.criteriaEntries)
            allEntries.update(entries)
            query = Query(queryClass, allEntries)
        queryFor(queryClass, query)
        typeFor(queryClass, TypeQuery(query))
        # We remove here the descriptions, since they should not be used anymore (unlike the Model).
        for entry in query.criteriaEntries.values():
            assert isinstance(entry, CriteriaEntry)
            if hasattr(queryClass, entry.name): delattr(queryClass, entry.name)
        queryClass.__init__ = _init__query
        queryClass.__getattr__ = _getattr__entry
        queryClass.__setattr__ = _setattr__entry
        queryClass.__delattr__ = _delattr__entry
        log.info('Created query %s for class %s containing %s API entries', query, queryClass, len(entries))
        return queryClass

# --------------------------------------------------------------------

class APICriteria:
    '''
    Used for decorating classes that are API criteria's.
    Attention the declared criteria will have the __new__ redeclared in order to provide the criteria descriptor
    instead of the actual criteria, so do not create criteria instance only when is in the purpose of creating
    a query.
    Each decorated criteria instance will contain the fields 'query' containing the query that owns the criteria
    and 'entryName' the name under which the criteria has been declared.
    
    ex:
        @APICriteria()
        class OrderBy:
    
            order = APIProperty(bool)
    '''
    
    def __call__(self, criteriaClass):
        '''
        What happens here is basically that the class that is considered an API criteria is first
        checked if it has any API properties, if that is the case than it will associate a criteria to this
        criteria class.
        
        @param criteriaClass: class
            The criteria class to be processed.
        @return: class
            The criteria class processed.
        '''
        properties = _processProperties(criteriaClass)
        criteria = criteriaFor(criteriaClass)
        if criteria is None:
            # this is not an extended criteria
            assert not len(properties) == 0, 'There are no API properties on criteria class %s' % criteriaClass
            criteria = Criteria(criteriaClass, properties)
        else:
            assert isinstance(criteria, Criteria)
            allProperties = {}
            allProperties.update(criteria.properties)
            allProperties.update(properties)
            criteria = Criteria(criteriaClass, allProperties)
        criteriaFor(criteriaClass, criteria)
        for prop in criteria.properties.values():
            assert isinstance(prop, Property)
            if hasattr(criteriaClass, prop.name): delattr(criteriaClass, prop.name)
        _init__original = getattr(criteriaClass, '__init__', None)
        def _init__criteria(self, *args, **keyargs):
            criteria = criteriaFor(self)
            assert isinstance(criteria, Criteria), 'Invalid criteria %s' % self
            for name in criteria.properties:
                self.__dict__[name] = None
            if _init__original:
                _init__original(self, *args, **keyargs)
        criteriaClass.__init__ = _init__criteria
        criteriaClass.__setattr__ = _setattr__properties
        criteriaClass.__delattr__ = _delattr__properties
        log.info('Created criteria %s for class %s containing %s API conditions', criteria,
                 criteriaClass, len(properties))
        return criteriaClass
    
# --------------------------------------------------------------------

class APICall:
    '''
    Used for decorating service methods that are used as APIs. When constructing the API service you have to
    specify the type of expected input value and the type of the output values. In the example below x value has
    to be a Number and the return value is None. Each call of the APICall methods will delegate to the API service
    implementation. The input types can be also function reference from model.
    The method action can be specified as a hint key word argument 'method', if not provided the API call will try
    to deduce that from the method name:
        if it starts with 'get' or 'find' the method is GET.
        if it starts with 'insert' or 'persist' is INSERT.
        if it starts with 'update' or 'merge' is UPDATE.
        if it starts with 'delete' or 'remove' is DELETE.
    If it cannot deduce it will raise an AssertionException.
    
    ex:
        @APICall(None, int)
        def updateX(self, x):
            doc string
            <no method body required>
            
        @APICall(Entity, Entity.x, String, name='unassigned')
        def findBy(self, x, name):
            doc string
            <no method body required>
            
        @APICall(Entity, Entity, OtherEntity, method=UPDATE, replaceFor=IAnotherService)
        def assign(self, entity, toEntity):
            doc string
            <no method body required>
    '''

    def __init__(self, *types, **hints):
        '''
        Constructs the API call decorator.

        @param types: arguments(Type|Type reference)
            On the first position it will be considered the output type then the input types expected for the
            service call.
        @param hints: key word arguments
            Provides hints for the call, supported parameters:
                @keyword method: integer
                    One of the operator module constants GET, INSERT, UPDATE, DELETE.
                @keyword webName: string
                    The name for locating the call, simply put this is the last name used in the resource path in
                    order to identify the call.
                @keyword replaceFor: class
                    The class to which the call should be replaced.

        @ivar inputTypes: list
            The Types obtained from the provided input.
        @ivar name: string
            The name of the call, it will be assigned when the decorator call is made.
        @ivar mandatoryCount: integer
            Provides the count of the mandatory input types, if the mandatory count is two and we have three input
            types it means that just the first two parameters need to be provided, at initialization the mandatory
            count is equal with the input count. It will be adjusted on the decorator call.
        '''
        if len(types) > 0:
            self.outputType = typeFor(types[0])
            self.inputTypes = []
            for type in types[1:]:
                typ = typeFor(type)
                assert isinstance(typ, Type), 'Could not obtain a valid Type for %s' % type
                self.inputTypes.append(typ)
            self.mandatoryCount = len(self.inputTypes)
        else:
            self.mandatoryCount = self.outputType = self.inputTypes = None
        self.name = None
        self.method = hints.pop('method', None)
        self.hints = hints

    def __call__(self, function):
        '''
        Constructs an API call that will have the provided input and output types. It will also provide a function
        that can be used for calling the service. The service call will be available only after a implementation
        is properly registered.
            
            @param function: FunctionType
                The function that performs the service.
        '''
        assert isfunction(function), 'Invalid function %s' % function
        if IS_PY3K:
            fnArgs = inspect.getfullargspec(function)
            args, varargs, keywords, defaults = fnArgs.args, fnArgs.varargs, fnArgs.varkw, fnArgs.defaults
            if self.outputType is None and self.inputTypes is None:
                self.outputType = typeFor(fnArgs.annotations.get('return'))
                self.inputTypes = []
                for arg in args:
                    if arg in fnArgs.annotations:
                        type = typeFor(fnArgs.annotations[arg])
                        typ = typeFor(type)
                        assert isinstance(typ, Type), 'Could not obtain a valid Type for %s' % type
                        self.inputTypes.append(typ)
                self.mandatoryCount = len(self.inputTypes)
            else:
                assert not fnArgs.annotations, \
                'The type can be either specified as annotations or as decorator type, cannot have both'
        else:
            fnArgs = inspect.getargspec(function)
            args, varargs, keywords, defaults = fnArgs
        assert 'self' == args[0], 'The call needs to be tagged in a class definition'
        assert len(args) == 1 + len(self.inputTypes), \
        'The functions parameters are not equal with the provided input types'
        assert varargs is None, 'No variable arguments are allowed'
        assert keywords is None, 'No keywords arguments are allowed'
        if defaults is not None:
            self.mandatoryCount -= len(defaults)
        self.name = function.__name__
        if self.method is None:
            mname = self.name.lower()
            if mname.startswith('get') or mname.startswith('find'):
                self.method = GET
            elif mname.startswith('insert') or mname.startswith('persist'):
                self.method = INSERT
            elif mname.startswith('update') or mname.startswith('merge'):
                self.method = UPDATE
            elif mname.startswith('delete') or mname.startswith('remove'):
                self.method = DELETE
            else:
                raise AssertionError('Cannot deduce method for function name (%s)' % function.__name__)

        self.inputs = []
        for k, name, typ in zip(range(0, len(args) - 1), args[1:], self.inputTypes):
            if k < self.mandatoryCount: self.inputs.append(Input(name, typ))
            else: self.inputs.append(Input(name, typ, True, defaults[k - self.mandatoryCount]))

        @wraps(function)
        def callFunction(srv, *args):
            '''
            Used for wrapping the actual service function call.
            '''
            assert isinstance(srv, ServiceSupport), \
            'Invalid service %s, maybe you forgot to decorate with APIService?' % srv
            service = serviceFor(srv)
            assert isinstance(service, Service), 'Invalid service instance for %s' % srv
            assert self.name in service.calls, \
            'Invalid service %s has no call for name <%s>' % (service, self.name)
            return service.calls[self.name].call(srv.implementation, args)
        callFunction.APICall = self
        return callFunction

class APIService:
    '''
    Used for decorating classes that are API services.
    
    ex:
        @APIService()
        class IEntityService:
    
            @call(Number, Entity.x)
            def multipy(self, x):
            
        
        @APIService((Entity, Issue))
        class IInheritingService(IEntityService):
    
            @call(Number, Issue.x)
            def multipy(self, x):
    '''
    
    def __init__(self, *generic):
        '''
        Creates the service instance based on the provided generic classes.
        
        @param generic: arguments(genericClass, replaceClass)|[...(genericClass, replaceClass)]
            The classes of that will be generically replaced.
        '''
        self.genericModel = []
        self.genericQuery = []
        for replaced, replacer in generic:
            model = modelFor(replaced)
            if model: 
                newModel = modelFor(replacer)
                assert isinstance(newModel, Model), \
                'Invalid generic replacer class %s, needs to be mapped as a model' % replacer
                self.genericModel.append((model, newModel))
            else:
                query = queryFor(replaced)
                assert isinstance(query, Query), \
                'Invalid generic replaced class %s, needs to be mapped as a model or query' % replaced
                newQuery = queryFor(replacer)
                assert isinstance(newQuery, Query), \
                'Invalid generic replacer class %s, needs to be mapped as a query' % replacer
                self.genericQuery.append((query, newQuery))
    
    def __call__(self, serviceClass):
        '''
        What happens here is basically that the class that is considered a API service is first
        checked if it has any API calls, if that is the case it will associate a service to this service class.
        
        @param serviceClass: class
            The service class that contains the API described service methods.
        @return: class
            The extended service class if is the case, the service class is forced to extend the Service support.
        '''
        calls = _processAPICalls(serviceClass)
        parentServices = (serviceFor(parent) for parent in serviceClass.__bases__)
        parentServices = [service for service in parentServices if service] 
        if len(parentServices) == 0:
            # this is not an extended service
            assert not len(calls) == 0, 'There are no API calls on service class %s' % calls
            service = Service(serviceClass, calls)
        else:
            allCalls = {}
            for parent in parentServices:
                assert isinstance(parent, Service)
                for name, call in parent.calls.items():
                    allCalls[name] = _processCallGeneric(call, self.genericModel, self.genericQuery)
            allCalls.update(calls)
            service = Service(serviceClass, allCalls)
        serviceFor(serviceClass, service)
        if not isinstance(serviceClass, ServiceSupport):
            newServiceClass = type(serviceClass.__name__, (serviceClass, ServiceSupport), {})
            newServiceClass.__module__ = serviceClass.__module__
            serviceClass = newServiceClass
        log.info('Created service %s for class %s ', service, serviceClass)
        return serviceClass
    
# --------------------------------------------------------------------

class ServiceSupport(object):
    '''
    Provides support for service. Basically all API services should extend this interface, or can be forced to do
    that by the APIService. This class will provide access to an implementation of the service. 
    '''
    
    def __init__(self, implementation):
        '''
        Constructs the API service class based on the provided implementation.
        
        @param implementation: object
            An instance of the class that implements all the methods required by the
            service.
        '''
        assert not implementation is None, 'Invalid implementation (None)'
        service = serviceFor(self)
        assert isinstance(service, Service), \
        'Cannot obtain an associated service for %s, maybe you are not using right this class' % self
        if __debug__:
            for call in service.calls.values():
                assert call.isCallable(implementation), \
                'The provided implementation %s is not suited for %s' % (implementation, call)
        self.implementation = implementation

# --------------------------------------------------------------------

# A list of names to be ignored when searching for properties or criteria
_IGNORE_NAMES = ['__dict__', '__module__', '__weakref__', '__doc__', 'PARTIAL']

def _processProperties(propertiesClass):
    '''
    ONLY FOR INTERNAL USE.
    Processes the properties in the properties model class.
    
    @param propertiesClass: class
        The properties class.
    @return: dictionary
        A dictionary containing as a key the property name and as a value the property.
    '''
    log.info('Processing properties for %s', propertiesClass)
    properties = {}
    for name, value in propertiesClass.__dict__.items():
        if name in _IGNORE_NAMES or isfunction(value):
            continue
        type = typeFor(value)
        if type is not None:
            properties[name] = Property(name, type)
            log.info('Created property based on found type %s for <%s>', type, name)
        else:
            log.warning('Cannot process property for class %s field <%s> of value %s', propertiesClass, name, value)
    return properties

def _processEntries(queryClass):
    '''
    ONLY FOR INTERNAL USE.
    Processes the criteria entries in the provided query class.
    
    @param queryClass: class
        The query class.
    @return: dictionary
        A dictionary containing as a key the entry name and as a value the entry.
    '''
    log.info('Processing entries for query %s', queryClass)
    entries = {}
    for name, value in queryClass.__dict__.items():
        if name in _IGNORE_NAMES or isfunction(value):
            continue
        crtEntr = None
        if not isclass(value):
            value = value.__class__
        criteria = criteriaFor(value)
        if isinstance(criteria, Criteria):
            crtEntr = CriteriaEntry(criteria, name)
            log.info('Created entry based on found criteria %s class for <%s>', criteria, name)
        if crtEntr is not None:
            entries[name] = crtEntr
        else:
            log.warning('Cannot process entry for class %s field <%s> of value %s', queryClass, name, value)
    return entries

def _processAPICalls(serviceClass):
    '''
    ONLY FOR INTERNAL USE.
    Processes the API calls in the provided service class.
    
    @param serviceClass: class 
        The service class to search the calls for.
    @return: dictionary
        A dictionary containing all the Call's attached to the API calls found, as key is the name of the 
        API call decorated function.
    '''
    log.info('Processing calls for %s', serviceClass)
    calls = {}
    for name, func in serviceClass.__dict__.items():
        if isfunction(func):
            apiCall = None
            try:
                apiCall = func.APICall
                assert isinstance(apiCall, APICall), 'Expected API call %' % apiCall
                call = Call(name, apiCall.hints, apiCall.method, apiCall.outputType, apiCall.inputs,
                            apiCall.mandatoryCount)
                calls[name] = call
                log.info('Found call %s', call)
            except AttributeError:
                log.warn('Function %s is not an API call, maybe you forgot to decorated with APICall?', \
                         func.__name__)
    return calls

def _processCallGeneric(call, genericModel, genericQuery):
    '''
    ONLY FOR INTERNAL USE.
    Processes the provided call if is the case to a extended call based on the model class.
    If either the output or input is based on the provided super model than it will create new call that will have
    the super model replaced with the new model in the types of the call.
    
    @param call: Call
        The call to be analyzed.
    @param genericModel: [model, newModel]
        The list of generic model to process.
    @param genericQuery: query, newQuery]
        The list of generic queries to process.
    @return: Call
        If the provided call is not depended on the super model it will be returned as it is, if not a new call
        will be created with all the dependencies from super model replaced with the new model.
    '''
    assert isinstance(call, Call)
    updated = False
    outputType = _processTypeGeneric(call.outputType, genericModel, genericQuery)
    if outputType: updated = True
    else: outputType = call.outputType
    inputs = []
    for inp in call.inputs:
        assert isinstance(inp, Input)
        genericType = _processTypeGeneric(inp.type, genericModel, genericQuery)
        if genericType:
            inputs.append(Input(inp.name, genericType, inp.hasDefault, inp.default))
            updated = True
        else: inputs.append(inp)
    if updated:
        newCall = Call(call.name, call.hints, call.method, outputType, inputs, call.mandatoryCount)
        log.info('Generic call transformation from %s to %s' % (call, newCall))
        call = newCall
    return call

def _processTypeGeneric(typ, genericModel, genericQuery):
    '''
    ONLY FOR INTERNAL USE.
    Processes the type if is the case into a new type that is extended from the original but having the new
    model as reference instead of the super model.
    @see: _processCallGeneric
    
    @param typ: Type
        The type to process.
    @param genericModel: [model, newModel]
        The list of generic model to process.
    @param genericQuery: query, newQuery]
        The list of generic queries to process.
    @return: Type|None
        If the provided type was containing references to the super model than it will return a new type
        with the super model references changes to the new model, otherwise returns None.
    '''
    newType = None
    if isinstance(typ, TypeProperty):
        assert isinstance(typ, TypeProperty)
        newModel = __searchModel(genericModel, typ.model)
        if newModel:
            assert isinstance(newModel, Model)
            newType = newModel.typeProperties[typ.property.name]
    elif isinstance(typ, TypeModel):
        assert isinstance(typ, TypeModel)
        newModel = __searchModel(genericModel, typ.model)
        if newModel: newType = newModel.type
    elif isinstance(typ, TypeQuery):
        assert isinstance(typ, TypeQuery)
        for q, newQuery in genericQuery:
            if typ.query is q: 
                newType = TypeQuery(newQuery)
                break
    elif isinstance(typ, List):
        assert isinstance(typ, List)
        itemType = _processTypeGeneric(typ.itemType, genericModel, genericQuery)
        if itemType: newType = List(itemType)
    elif isinstance(typ, Iter):
        assert isinstance(typ, Iter)
        itemType = _processTypeGeneric(typ.itemType, genericModel, genericQuery)
        if itemType: newType = Iter(itemType)
    return newType

def __searchModel(models, model):
    '''
    ONLY FOR INTERNAL USE.
    '''
    for m, newModel in models:
        if model is m: return newModel
    return None
    
# --------------------------------------------------------------------

def _setattr__properties(self, name, value):
    '''
    ONLY FOR INTERNAL USE.
    Function for setting attributes on properties object.
    '''
    properties = propertiesFor(self)
    assert isinstance(properties, Properties), 'Invalid object %r, has no properties' % self
    prop = properties.properties.get(name, None)
    if isinstance(prop, Property):
        prop.set(self, value)
    else:
        self.__dict__[name] = value
    
def _delattr__properties(self, name):
    '''
    ONLY FOR INTERNAL USE.
    Function for deleting attributes on properties object.
    '''
    properties = propertiesFor(self)
    assert isinstance(properties, Properties), 'Invalid object %r, has no properties' % self
    prop = properties.properties.get(name, None)
    if isinstance(prop, Property):
        prop.remove(self)
    else:
        if not self.__dict__.has_key(name):
            raise AttributeError(name)
        del self.__dict__[name]

def _getstate__properties(self):
    '''
    ONLY FOR INTERNAL USE.
    Function for properly pickling a properties container. Based on the pickle specifications.
    '''
    properties = propertiesFor(self)
    assert isinstance(properties, Properties), 'Invalid object %r, has no properties' % self
    return dict([(name, getattr(self, name))for name in properties.properties])

def _contains__properties(self, key):
    '''
    ONLY FOR INTERNAL USE.
    Function for using the 'in' keyword for detecting if a property is found in a entity.
    '''
    properties = propertiesFor(self)
    assert isinstance(properties, Properties), 'Invalid object %r, has no properties' % self
    typ = typeFor(key)
    if isinstance(typ, TypeProperty):
        return typ.property.has(self)
    return False

# --------------------------------------------------------------------

# Whenever the set is called on the criteria descriptor than this condition property will be used.
DEFAULT_CONDITIONS = []

def _init__query(self, **keyargs):
    '''
    ONLY FOR INTERNAL USE.
    Function for setting query values from constructor.
    '''
    query = queryFor(self)
    assert isinstance(query, Query), 'Invalid instance %s, is not associated with a query' % self
    for name, value in keyargs.items():
        crtEntry = query.criteriaEntries.get(name, None)
        if not isinstance(crtEntry, CriteriaEntry):
            raise AssertionError('Invalid query name %r for %r' % (name, self.__class__.__name__))
        _setattr__entry(self, name, value)

def _getattr__entry(self, name):
    '''
    ONLY FOR INTERNAL USE.
    Function for setting attributes on criteria entry object.
    '''
    query = queryFor(self)
    assert isinstance(query, Query), 'Invalid instance %s, is not associated with a query' % self
    crtEntry = query.criteriaEntries.get(name, None)
    if isinstance(crtEntry, CriteriaEntry):
        return crtEntry.obtain(self)
    if not self.__dict__.has_key(name):
        raise AttributeError(name)
    return self.__dict__[name]
    
def _setattr__entry(self, name, value):
    '''
    ONLY FOR INTERNAL USE.
    Function for setting attributes on criteria entry object.
    '''
    query = queryFor(self)
    assert isinstance(query, Query), 'Invalid instance %s, is not associated with a query' % self
    crtEntry = query.criteriaEntries.get(name, None)
    if isinstance(crtEntry, CriteriaEntry):
        active = crtEntry.obtain(self)
        criterias = crtEntry.criteria
        for cond in DEFAULT_CONDITIONS:
            assert isinstance(criterias, Properties)
            crt = criterias.properties.get(cond, None)
            if crt is not None:
                assert isinstance(crt, Property)
                crt.set(active, value)
                break
        else:
            raise AssertionError('No default conditions %s found in criteria %s' % (DEFAULT_CONDITIONS, active))
    else:
        self.__dict__[name] = value
    
def _delattr__entry(self, name):
    '''
    ONLY FOR INTERNAL USE.
    Function for deleting attributes on criteria entry object.
    '''
    query = queryFor(self)
    assert isinstance(query, Query), 'Invalid instance %s, is not associated with a query' % self
    crtEntry = query.criteriaEntries.get(name, None)
    if isinstance(crtEntry, CriteriaEntry):
        crtEntry.remove(self)
    else:
        if not self.__dict__.has_key(name):
            raise AttributeError(name)
        del self.__dict__[name]

# --------------------------------------------------------------------

ATTR_PROPERTIES = Attribute(__name__, 'properties', Properties)
# Provides attribute for properties.

def propertiesFor(obj, properties=None):
    '''
    If the properties are provided it will be associate with the obj, if the properties is not provided than this 
    function will try to provide if it exists the properties associated with the obj.
    
    @param obj: object|class
        The class to associate or extract the model.
    @param properties: Properties
        The properties to associate with the obj.
    @return: Properties|None
        If the properties has been associate then the return will be none, if the properties is being extracted it 
        can return either the Properties or None if is not found.
    '''
    if properties is None: return ATTR_PROPERTIES.get(obj, None)
    assert not ATTR_PROPERTIES.hasOwn(obj), 'Already has a properties %s' % obj
    ATTR_PROPERTIES.set(obj, properties)
    return properties

def modelFor(obj, model=None):
    '''
    Same as @see: propertiesFor but particularized for @see: Model
    '''
    model = propertiesFor(obj, model)
    assert not model or isinstance(model, Model), 'Invalid model %s' % model
    return model

def criteriaFor(obj, criteria=None):
    '''
    Same as @see: propertiesFor but particularized for @see: Criteria
    '''
    criteria = propertiesFor(obj, criteria)
    assert not criteria or isinstance(criteria, Criteria), 'Invalid criteria %s' % criteria
    return criteria

ATTR_QUERY = Attribute(__name__, 'query', Query)
# Provides attribute for query.

def queryFor(obj, query=None):
    '''
    If the query is provided it will be associate with the obj, if the query is not provided than this function
    will try to provide if it exists the query associated with the obj.
    
    @param obj: object|class
        The class to associate or extract the query.
    @param query: Query
        The Query to associate with the obj.
    @return: Query|None
        If the query has been associate then the return will be none, if the query is being extracted it can
        return either the Query or None if is not found.
    '''
    if query is None: return ATTR_QUERY.get(obj, None)
    assert not ATTR_QUERY.hasOwn(obj), 'Already has a query %s' % obj
    ATTR_QUERY.set(obj, query)

ATTR_SERVICE = Attribute(__name__, 'service', Service)
# Provides attribute for service.

def serviceFor(obj, service=None):
    '''
    If the service is provided it will be associate with the obj, if the service is not provided than this function
    will try to provide if it exists the service associated with the obj.
    
    @param obj: object|class
        The class to associate or extract the query.
    @param service: Service
        The Service to associate with the obj.
    @return: Service|None
        If the service has been associate then the return will be none, if the service is being extracted it can
        return either the Service or None if is not found.
    '''
    if service is None: return ATTR_SERVICE.get(obj, None)
    assert not ATTR_SERVICE.hasOwn(obj), 'Already has a service %s' % obj
    ATTR_SERVICE.set(obj, service)

# --------------------------------------------------------------------

def update(propertyType, toType):
    '''
    Used whenever there is the need to define a model property outside the class definition.
    
    @param property: TypeProperty
        The type property to update the property to.
    @param toType: Type
        The type to update the property to.
    '''
    assert isinstance(propertyType, TypeProperty), 'Invalid type property %s' % propertyType
    typ = typeFor(toType)
    assert isinstance(typ, Type), 'Invalid type to update to %s' % toType
    #TODO: maybe a better way to set own properties in model. The property is immutable so we make a hack to set it
    propertyType.property.__dict__['type'] = typ
