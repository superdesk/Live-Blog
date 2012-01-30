'''
Created on May 29, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Nistor Gabriel

Provides the containers that describe the APIs.
'''

from ..support.util import IS_PY3K, Attribute, immutable, immut
from ..type_legacy import Iterable, OrderedDict
from .type import Type, Input, Id, IdString, Boolean, Number, Integer, \
    Percentage, String, Time, Date, DateTime, TypeProperty, typeFor
from inspect import ismodule, getargspec, isclass
import logging
from ally.api.type import TypeModel

# --------------------------------------------------------------------

log = logging.getLogger(__name__)
    
# --------------------------------------------------------------------
# The available method actions.
GET = 1
INSERT = 2
UPDATE = 4
DELETE = 8

ATTR_HAS_SET = Attribute(__name__, 'hasSet', set)
# Keeps the set containing the name of the properties that have been set on the model.

NAME_ON_SET = '%sOnSet'
# The name used for property on set listener.
NAME_ON_DEL = '%sOnDel'
# The name used for property on delete listener.

# --------------------------------------------------------------------

@immutable
class Properties:
    '''
    Used for mapping the API properties.
    '''
    
    __immutable__ = ('properties',)

    def __init__(self, properties):
        '''
        Constructs a properties group.
        
        @param properties: dictionary
            A dictionary containing as a key the property name and as a value the property.
        '''
        assert isinstance(properties, dict), 'The properties %s need to be a dictionary' % properties
        if __debug__:
            for prop in properties.values():
                assert isinstance(prop, Property), 'Not a Property type for %s' % prop
        self.properties = immut(properties)
        
    def isPartial(self, model):
        '''
        Checks if the provided model instance is partially populated in relation with this properties. A model entity
        is partial if at least one property is no provided.
        
        @param model: object
            The model object to check.
        @return: boolean
            True if the model object is partial, false otherwise.
        '''
        for prop in self.properties.values():
            assert isinstance(prop, Property)
            if not prop.has(model): return True
        return False
    
    def copy(self, modelTo, modelFrom):
        '''
        Copies all the properties from model from that are set into model to. Basically if the model from has a
        property it will be copied into model to.
        
        @param modelTo: object
            The model object to copy to.
        @param modelFrom: object
            The model object to from.
        @return: object
            The modelTo object.
        '''
        for prop in self.properties.values():
            assert isinstance(prop, Property)
            if prop.has(modelFrom):
                prop.set(modelTo, prop.get(modelFrom))
        return modelTo
    
    def merge(self, modelTo, modelFrom):
        '''
        Merges into the modelTo all values from modeFrom that are not set in modelTo.
        
        @param modelTo: object
            The model object to be merged.
        @param modelFrom: object
            The model object to merge from.
        @return: object
            The modelTo object.
        '''
        for prop in self.properties.values():
            assert isinstance(prop, Property)
            if not prop.has(modelTo):
                prop.set(modelTo, prop.get(modelFrom))
        return modelTo
    
    def __eq__(self, other):
        if isinstance(other, self.__class__): return self.properties == other.properties
        return False
    
    def __str__(self): return '<%s %s>' % (self.__class__.__name__, [str(prop) for prop in self.properties.values()])

@immutable
class Property:
    '''
    Provides the container for the API property types. It contains the operation that need to be
    applied on a model instance that relate to this property.
    The property operator also provides a listener mechanism whenever the represented property this to be notified
    for changes to the contained model. So if we have property 'name' automatically whenever the value is set if
    the model contains the 'nameOnSet' method it will be called, and on deletion the 'nameOnDel' is called.
    '''
    
    __immutable__ = ('type', 'name')

    def __init__(self, name, type):
        '''
        Constructs a property operations container.
        
        @param name: string
            The name of the property as it should be called by.
        @param type: Type
            The Type of the property.
        @ivar _var: string
            Contains the name of the attribute that will be used for keeping the property value.
        '''
        assert isinstance(name, str) and str != '', 'Provide a valid name'
        assert isinstance(type, Type), 'Invalid type %s' % type
        self.type = type
        self.name = name
        
    def has(self, model):
        '''
        Checks if the model contains a value for this property even if that value is None.
        
        @param model: object
            The model instance to provide the value for.
        @return: boolean
            True if a value is present, false otherwise.
        '''
        assert not model is None, 'Invalid model object (None)'
        has = ATTR_HAS_SET.getOwn(model, None)
        if has: return self.name in has
        return False
    
    def hasSet(self, model):
        '''
        Sets on the model the has flag for this property. This will also call the listeners.
        
        @param model: object
            The model instance to set the has flag on.
        '''
        assert not model is None, 'Invalid model object (None)'
        has = ATTR_HAS_SET.getOwn(model, None)
        if not has: has = ATTR_HAS_SET.setOwn(model, set())
        has.add(self.name)
        
        listener = getattr(model, NAME_ON_SET % self.name, None)
        if listener: listener()
    
    def get(self, model):
        '''
        Provides the value represented by this property for the provided instance.
        
        @param model: object
            The model instance to provide the value for.
        @return: object
            The value of the property.
        '''
        assert not model is None, 'Invalid model object (None)'
        assert hasattr(model, '__dict__'), 'Invalid model %s for %s' % (model, self) 
        return model.__dict__.get(self.name, None)
    
    def set(self, model, value):
        '''
        Set the value represented by this property for the provided model instance.
        
        @param model: object
            The model instance to set the value to.
        @param value: object
            The value to set, needs to be valid for this property.
        '''
        assert not model is None, 'Invalid model object (None)'
        if not value is None and not self.type.isValid(value):
            raise AssertionError('The property %r takes a parameter of type %s, illegal value %r' % 
                                 (self.name, self.type, value))
        object.__setattr__(model, self.name, value)
        self.hasSet(model)
        
        assert log.debug('Success on setting value (%s) for %s', value, self) or True
    
    def remove(self, model):
        '''
        Remove the value represented by this property from the provided model instance.
        
        @param model: object
            The model instance to remove the value from.
        @return: boolean
            True if there has been something to remove, false otherwise.
        '''
        assert not model is None, 'Invalid model object (None)'
        if self.name in model.__dict__:
            model.__dict__[self.name] = None
            has = ATTR_HAS_SET.getOwn(model, None)
            if has: has.remove(self.name)
            listener = getattr(model, NAME_ON_DEL % self.name, None)
            if listener: listener()
            assert log.debug('Success on removing value for %s', self) or True
            return True
        return False
    
    def __hash__(self): return hash((self.name, self.type))
    
    def __eq__(self, other):
        if isinstance(other, self.__class__): return self.name == other.name and self.type == other.type
        return False

    def __str__(self): return '<%s[%s = %s]>' % (self.__class__.__name__, self.name, self.type)

# --------------------------------------------------------------------

class Model(Properties):
    '''
    Used for mapping the API models.
    @attention: The model will allow only for primitive types.
    @see: Properties
    '''
    
    __immutable__ = Properties.__immutable__ + ('modelClass', 'name', 'typeProperties', 'type')

    def __init__(self, modelClass, modelName, properties):
        '''
        Constructs a properties model.
        @see: Properties.__init__
        
        @param modelClass: class
            The represented model class.
        @ivar name: string
            The name of the model.
        '''
        assert isclass(modelClass), 'Invalid model class %s' % modelClass
        assert isinstance(modelName, str) and len(modelName) > 0, 'Invalid model name %s' % modelName
        self.modelClass = modelClass
        self.name = modelName
        Properties.__init__(self, _sort(properties))
        if __debug__:
            for prop in properties.values():
                assert prop.type.isPrimitive, 'Not a primitive type for %s' % prop
        self.typeProperties = immut({name: TypeProperty(self, prop) for name, prop in self.properties.items()})
        self.type = TypeModel(self)
                
    def createModel(self):
        '''
        Creates a new model object based on the contained model class.
        
        @return: object
            The newly created model instance.
        '''
        assert log.debug('Created model instance for class %s', self.modelClass) or True
        return self.modelClass()
    
    def __hash__(self): return hash(self.modelClass)

    def __eq__(self, other):
        if Properties.__eq__(self, other):
            return self.modelClass == other.modelClass and self.name == other.name
        return False

    def __str__(self):
        return '<%s (%s) %s>' % (self.__class__.__name__, self.name, \
                                 [str(prop) for prop in self.properties.values()])
       
# --------------------------------------------------------------------

@immutable
class Query:
    '''
    Used for mapping the API query.
    '''
    
    __immutable__ = ('queryClass', 'criteriaEntries')

    def __init__(self, queryClass, criteriaEntries):
        '''
        Initialize the criteria's of this query.
        
        @param queryClass: class
            The represented query class.
        @param criteriaEntries: dictionary
            The criteria's dictionary that belong to this query, as a key is the criteria name (how is been 
            declared in the query) and as a value the criteria entry.
        '''
        assert isclass(queryClass), 'Invalid query class %s' % queryClass
        assert isinstance(criteriaEntries, dict), \
        'The criteria entries %s needs to be a dictionary' % criteriaEntries
        if __debug__:
            for crt in criteriaEntries.values():
                assert isinstance(crt, CriteriaEntry), 'Not a CriteriaEntry %s' % crt
        self.queryClass = queryClass
        self.criteriaEntries = immut(criteriaEntries)
        
    def createQuery(self):
        '''
        Creates a new query object based on the contained query class.
        
        @return: object
            The newly created query instance.
        '''
        assert log.debug('Created query instance for class %s', self.queryClass) or True
        return self.queryClass()
    
    def __hash__(self): return hash(self.queryClass)
    
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.queryClass == other.queryClass and self.criteriaEntries == other.criteriaEntries
        return False

    def __str__(self):
        return '<%s %s>' % (self.queryClass.__class__.__name__, [str(entry) for entry in self.criteriaEntries.values()])
 
class CriteriaEntry(Property):
    '''
    Contains a criteria entry in a query. 
    @see: Property
    '''
    
    __immutable__ = Property.__immutable__ + ('criteria',)
    
    def __init__(self, criteria, name):
        '''
        Constructs a criteria entry.
        @see: Property.__init__
        
        @param criteria: Criteria
            The criteria that is being used by this entry.
        '''
        assert isinstance(criteria, Criteria), 'Invalid criteria %s' % criteria
        self.criteria = criteria
        Property.__init__(self, name, Type(criteria.criteriaClass))
        
    def obtain(self, query):
        '''
        If there is already a value for the criteria property it will provide that if there is no value available it
        will create one.
        
        @param query: object
            The query instance to provide the value for.
        '''
        assert not query is None, 'Invalid query object (None)'
        criteria = self.get(query)
        if criteria is None:
            criteria = self.criteria.createCriteria(query, self)
            self.set(query, criteria)
        return criteria

class Criteria(Properties):
    '''
    Used for mapping the API criteria.
    @attention: The criteria will allow only for primitive types.
    @see: Properties
    '''
    
    __immutable__ = Properties.__immutable__ + ('criteriaClass',)

    def __init__(self, criteriaClass, properties):
        '''
        Initialize the criteria instance by providing the name under which the criteria has been declared.
        @see: Properties.__init__
        
        @param criteriaClass: class
            The represented criteria class.
        '''
        assert isclass(criteriaClass), 'Invalid criteria class %s' % criteriaClass
        self.criteriaClass = criteriaClass
        Properties.__init__(self, properties)
        if __debug__:
            for prop in properties.values():
                assert prop.type.isPrimitive, 'Not a primitive type for %s' % prop

    def createCriteria(self, query, criteriaEntry):
        '''
        Creates a new criteria object based on the contained criteria class.
        
        @param query: object
            The query object of the criteria.
        @param criteriaEntry: CriteriaEntry
            The criteria entry creating the criteria instance.
        @return: object
            The newly created criteria instance.
        '''
        assert not query is None, 'Invalid query object (None)'
        assert isinstance(criteriaEntry, CriteriaEntry), 'Invalid criteria entry %s' % criteriaEntry
        criteria = self.criteriaClass()
        criteria.query = query
        criteria.entryName = criteriaEntry.name
        assert log.debug('Created criteria with name (%s) for query %s as class %s', \
                         criteriaEntry.name, query, self.criteriaClass) or True
        return criteria

    def __hash__(self): return hash(self.criteriaClass)
    
    def __eq__(self, other):
        if Properties.__eq__(self, other): return self.criteriaClass == other.criteriaClass
        return False
    
# --------------------------------------------------------------------

@immutable
class Call:
    '''
    Provides the container for a service call. This class will basically contain all the
    Property types that are involved in input and output from the call.
    '''
    
    __immutable__ = ('name', 'hints', 'method', 'outputType', 'inputs', 'mandatoryCount')
    
    def __init__(self, name, hints, method, outputType, inputs, mandatoryCount):
        '''
        Constructs an API call that will have the provided input and output types.
        
        @param name: string
            The name of the function that will be called on the service implementation.
        @param hint: dictionary{string, object}
            The hints associated with the call.
        @param method: integer
            The method of the call, can be one of GET, INSERT, UPDATE or DELETE constants in this module.
        @param outputType: Type
            The output type for the service call.
        @param inputs: list
            A list containing all the Input's of the call.
        @param mandatoryCount: integer
            Provides the count of the mandatory input types, if the mandatory count is two and we have three input
            types it means that just the first two parameters need to be provided.
        '''
        assert isinstance(name, str) and str != '', 'Provide a valid name'
        assert isinstance(hints, dict), 'Invalid hints %s' % hints
        assert isinstance(method, int), 'Invalid method %s' % method
        assert method in (GET, INSERT, UPDATE, DELETE), \
        'Invalid method %s, is not one of the known constants' % method
        assert isinstance(outputType, Type), 'Invalid output Type %s' % outputType
        assert isinstance(inputs, list), 'Invalid inputs %s, needs to be a list' % inputs
        assert isinstance(mandatoryCount, int), 'Invalid mandatory count <%s>, needs to be integer' % mandatoryCount
        assert mandatoryCount >= 0 and mandatoryCount <= len(inputs), \
        'Invalid mandatory count <%s>, needs to be greater than 0 and less than ' % (mandatoryCount, len(inputs))
        if __debug__:
            for input in inputs: assert isinstance(input, Input), 'Not an input %s' % input
            for hintn in hints: assert isinstance(hintn, str), 'Invalid hint name %s' % hintn
        self.name = name
        self.hints = immut(hints)
        self.method = method
        self.outputType = outputType
        self.inputs = tuple(inputs)
        self.mandatoryCount = mandatoryCount

    def isCallable(self, impl):
        '''
        Checks if the provided implementation class contains the required function
        to be called by this call container.
        
        @param impl: class|module
            Either the instance or module that implements the API service method.
        '''
        if ismodule(impl): func = self._findModuleFunction(impl)
        else: func = self._findClassFunction(impl.__class__)
        return func is not None
    
    def call(self, impl, args):
        '''
        Performs the check of the input and output parameters for a service call
        and calls the representative method from the provided implementation.
        
        @param impl: object
            The implementation that reflects the service call that is
            contained by this call.
        @param args: list
            The arguments to be used in invoking the service 
        '''
        assert not impl is None, 'Provide the service implementation to be used foe calling the represented function'
        assert isinstance(args, Iterable), 'The arguments %s need to be iterable' % str(args)
        valid = False
        if len(args) >= self.mandatoryCount and len(self.inputs) >= len(args):
            valid = True
            for k, inp, value in zip(range(len(self.inputs)), self.inputs, args):
                assert isinstance(inp, Input)
                if value is None and k >= self.mandatoryCount:
                    continue
                if not inp.type.isValid(value):
                    valid = False
                    break
        if not valid:
            raise AssertionError('The arguments %r provided are not compatible with the expected inputs %r' % 
                                 (args, self.inputs))
        if ismodule(impl): func = getattr(impl, self.name)
        else: func = getattr(impl, self.name)
        
        ret = func.__call__(*args)
            
        if not self.outputType.isValid(ret):
            raise AssertionError('The return %s provided is not compatible with the expected output type %s \
for call %s' % (ret, self.outputType, self))
        
        assert log.debug('Success calling %r with arguments %s and return class %s', \
                         func.__name__, args, ret.__class__.__name__) or True
        return ret
        
    def _findClassFunction(self, implClass):
        '''
        Finds the class function that is represented by this call.
        
        @return: function|None
            Returns the function if found for the provided class or None
            if no such function could be located.
        '''
        func = getattr(implClass, self.name, None)
        if not func is None:
            fnArgs = getargspec(func)
            if IS_PY3K: args, varargs, keywords, defaults = fnArgs.args, fnArgs.varargs, fnArgs.keywords, fnArgs.defaults
            else: args, varargs, keywords, defaults = fnArgs
            if len(args) == 1 + len(self.inputs) and not varargs or keywords:
                if defaults is None:
                    if len(self.inputs) - self.mandatoryCount == 0:
                        return func
                elif len(self.inputs) - self.mandatoryCount == len(defaults):
                    return func
                        
    def _findModuleFunction(self, implModule):
        '''
        Finds the module function that is represented by this call.
        
        @return: function|None
            Returns the function if found for the provided module or None
            if no such function could be located.
        '''
        func = getattr(implModule, self.name, None)
        if not func is None:
            fnArgs = getargspec(func)
            if IS_PY3K: args, varargs, keywords, defaults = fnArgs.args, fnArgs.varargs, fnArgs.keywords, fnArgs.defaults
            else: args, varargs, keywords, defaults = fnArgs
            if len(args) == len(self.inputs) and not varargs or keywords:
                if defaults is None:
                    if len(self.inputs) - self.mandatoryCount == 0:
                        return func
                elif len(self.inputs) - self.mandatoryCount == len(defaults):
                    return func
    
    def __hash__(self): return hash((self.name, self.outputType, self.inputs, self.mandatoryCount))
    
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.name == other.name and self.outputType == other.outputType \
                and self.inputs == other.inputs and self.mandatoryCount == other.mandatoryCount
        return False
    
    def __str__(self):
        return '<Call[%s %s(%s)]>' % (self.outputType, self.name, ', '.join([
                ''.join(('defaulted:' if i >= self.mandatoryCount else '', inp.name, '=', str(inp.type))) 
                        for i, inp in enumerate(self.inputs)]))

@immutable
class Service:
    '''
    Used for mapping the API calls.
    '''

    __immutable__ = ('serviceClass', 'calls')

    def __init__(self, serviceClass, calls):
        '''
        Constructs the API service class based on the provided implementation.
        
        @param calls: dictionary
            The calls dictionary that belong to this service class, the key is the call name.
        '''
        assert isclass(serviceClass), 'Invalid service class %s' % serviceClass
        assert isinstance(calls, dict), 'The calls %s need to be a dictionary' % calls
        if __debug__:
            for call in calls.values():
                assert isinstance(call, Call), 'Not a Call type for %s' % call
        #self.model = model
        self.serviceClass = serviceClass
        self.calls = immut(calls)
    
    def __hash__(self): return hash(self.serviceClass)
    
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.serviceClass == other.serviceClass and self.calls == other.calls
        return False
    
    def __str__(self):
        return '<Service[%s %s calls]>' % \
            (self.serviceClass.__name__, len(self.calls))

# --------------------------------------------------------------------

TYPE_ORDER = [Id, IdString, Boolean, Integer, Number, Percentage, String, Time, Date, DateTime, TypeProperty]
def __sortKey(item):
    '''
    FOR INTERNAL USE.
    Provides the sorting key.
    '''
    for k, ord in enumerate(TYPE_ORDER):
        if typeFor(ord) == item[1].type:
            break
    else:
        k = len(TYPE_ORDER)
    return '%02d' % k + item[0]
def _sort(properties):
    '''
    FOR INTERNAL USE.
    Used for sorting the properties dictionary.
    '''
    assert isinstance(properties, dict), 'Invalid properties dictionary %s' % properties
    items = sorted(properties.items(), key=__sortKey)
    ordered = OrderedDict()
    for name, property in items:
        ordered[name] = property
    return ordered
