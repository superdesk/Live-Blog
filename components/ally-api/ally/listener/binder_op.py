'''
Created on Aug 24, 2011

@package Newscoop
@copyright 2011 Sourcefabric o.p.s.
@license http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides binding listener function to handle API operators validation.
'''

from ..internationalization import _, textdomain
from ..api.configure import modelFor, serviceFor, queryFor
from ..api.operator import Property, Model, Query, Service, Call, UPDATE, INSERT
from ..api.type import Input, TypeModel, TypeProperty, typeFor
from ..exception import InputException, Ref
from ..support.api.util_type import propertyOf
from .binder import bindListener, callListeners, registerProxyBinder, \
    bindBeforeListener, indexBefore, INDEX_DEFAULT
from collections import Sized
from inspect import isclass
import functools
    
# --------------------------------------------------------------------

INDEX_MODEL = indexBefore('model', INDEX_DEFAULT)
# The index for model listeners

INDEX_PROP = indexBefore('property', INDEX_DEFAULT)
# The index for property listeners
INDEX_PROP_MAX_LEN = indexBefore('prop_max_len', INDEX_PROP)
# The index for validation of max length
INDEX_PROP_REQUIRED = indexBefore('prop_required', INDEX_PROP_MAX_LEN)
# The index for validation of required properties
INDEX_PROP_MANAGED = indexBefore('prop_managed', INDEX_PROP_REQUIRED)
# The index for validation of the managed properties
INDEX_PROP_AUTO_ID = indexBefore('prop_auto_id', INDEX_PROP_MANAGED)
# The index for validation the auto id properties

EVENT_VALID_INSERT = 'valid_insert'
# Listener key used for the insert
EVENT_VALID_UPDATE = 'valid_update'
# Listener key used for the update

textdomain('errors')

# --------------------------------------------------------------------

def createModelMapping(modelClass):
    '''
    Creates a mapping class for the provided model class. The mapping class allows for bindings.
    
    @param modelClass: class
        The model class to create a mapping for.
    @return: class
        The mapping class.
    '''
    assert isclass(modelClass), 'Invalid model class %s' % modelClass
    model = modelFor(modelClass)
    assert isinstance(model, Model), 'Invalid class %s is not a model' % modelClass
    
    mappings = {}
    for name, typ in modelClass.__dict__.items():
        if isinstance(typ, TypeProperty):
            m = mappings[name] = Mapping()
            typeFor(m, typ)
    return type(modelClass.__name__, (modelClass,), mappings)

def createQueryMapping(queryClass):
    '''
    Creates a mapping class for the provided query class. The mapping class allows for bindings.
    
    @param queryClass: class
        The query class to create a mapping for.
    @return: class
        The mapping class.
    '''
    assert isclass(queryClass), 'Invalid query class %s' % queryClass
    query = queryFor(queryClass)
    assert isinstance(query, Query), 'Invalid class %s is not a query' % queryClass
    return type(queryClass.__name__, (queryClass,), {name: Mapping() for name in query.criteriaEntries})

class Mapping:
    '''
    Class that defines simple objects that allow mapping.
    '''

# --------------------------------------------------------------------

def validateModel(mappedClass, validator, key=(EVENT_VALID_INSERT, EVENT_VALID_UPDATE), index=INDEX_MODEL):
    '''
    @see: bindListener
    Binds a validation listener on the model that will be triggered for the provided event keys.
    
    @param mappedClass: class
        The model mapped class to bind to.
    @param validator: Callable|tuple(Callable)
        The validator(s) to use. 
    @param key: object immutable|tuple(object immutable)
        The event keys to bind the validation to.
    @param index: string
        The index at which to position the validation.
    '''
    assert isclass(mappedClass), 'Invalid mapped model class %s' % mappedClass
    assert isinstance(modelFor(mappedClass), Model), 'Invalid mapped model class %s, has no model' % mappedClass
    bindListener(mappedClass, key, validator, index)
    
def validateModelProperties(mappedClass):
    '''
    Binds a model properties validation on the model. The validation consists in calling all the validations found on
    properties of the model.
    
    @param mappedClass: class
        The model mapped class to bind to.
    '''
    validateModel(mappedClass, functools.partial(onModel, EVENT_VALID_INSERT), EVENT_VALID_INSERT)
    validateModel(mappedClass, functools.partial(onModel, EVENT_VALID_UPDATE), EVENT_VALID_UPDATE)

# --------------------------------------------------------------------

def validateProperty(refProp, validator, key=(EVENT_VALID_INSERT, EVENT_VALID_UPDATE), index=INDEX_PROP):
    '''
    @see: bindListener
    Binds a validation listener on the property that will be triggered for the provided event keys.
    
    @param refProp: @see: propertyOf
        The property reference to get the property to bind to.
    @param validator: Callable|tuple(Callable)
        The validator(s) to use. 
    @param key: object immutable|tuple(object immutable)
        The event keys to bind the validation to.
    @param index: string
        The index at which to position the validation.
    '''
    prop = propertyOf(refProp)
    if not prop: raise AssertionError('No property available for %s' % refProp) 
    bindListener(refProp, key, validator, index)

def validateAutoId(refProp):
    '''
    Binds an auto id validation on the property. The auto id validation consists of:
     - the property will not accept any external value when inserting.
     - the property has to have a valid value when updating.
    
    @param refProp: @see: propertyOf
        The property reference to get the property to bind to.
    '''
    validateProperty(refProp, onPropertyUnwanted, EVENT_VALID_INSERT, INDEX_PROP_AUTO_ID)
    validateProperty(refProp, (onPropertyRequired, onPropertyNone), EVENT_VALID_UPDATE, INDEX_PROP_AUTO_ID)

def validateRequired(refProp):
    '''
    Binds a required validation on the property. The required validation consists of:
     - the property has to have a valid value when inserting.
     - if the property has a value when updating it has to be valid, if there is no value than no action is taken.
    
    @param refProp: @see: propertyOf
        The property reference to get the property to bind to.
    '''
    validateProperty(refProp, (onPropertyRequired, onPropertyNone), EVENT_VALID_INSERT, INDEX_PROP_REQUIRED)
    validateProperty(refProp, onPropertyNone, EVENT_VALID_UPDATE, INDEX_PROP_REQUIRED)
    
def validateMaxLength(refProp, length):
    '''
    Binds a maximum length validation on the property. The maximum length validation consists of:
     - if the property has a value when inserting or updating it has to be less then the specified length.
    
    @param refProp: @see: propertyOf
        The property reference to get the property to bind to.
    @param length: integer
        The maximum length allowed for the property value.
    '''
    assert isinstance(length, int), 'Invalid length %s' % length
    validateProperty(refProp, functools.partial(onPropertyMaxLength, length), index=INDEX_PROP_MAX_LEN)
    
def validateManaged(prop):
    '''
    Binds a managed validation on the property. The managed validation consists of:
     - the property is not allowed to have any value when inserting or updating.
    
    @param refProp: @see: propertyOf
        The property reference to get the property to bind to.
    '''
    validateProperty(prop, onPropertyUnwanted, index=INDEX_PROP_MANAGED)

# --------------------------------------------------------------------
# validation listener methods

def onPropertyUnwanted(entity, mappedClass, prop, errors):
    '''
    Validation for unwanted properties, whenever this validator is added will not allow the property to have a value on 
    the provided entity.
    
    @param entity: object
        The entity to check for the property value.
    @param mappedClass: class
        The model mapped class of the entity.
    @param prop: Property
        The property that is unwanted.
    @param errors: list[Ref]
        The list of errors.
    '''
    assert isclass(mappedClass), 'Invalid mapped class %s' % mappedClass
    model = modelFor(mappedClass)
    assert isinstance(model, Model), 'Invalid mapped class %s, has no model' % mappedClass
    assert isinstance(entity, model.modelClass), 'Invalid entity %s for model %s' % (entity, model)
    assert isinstance(prop, Property), 'Invalid property %s' % prop
    assert isinstance(errors, list), 'Invalid errors list %s' % errors
    if prop.has(entity):
        errors.append(Ref(_('No value expected'), model=model, property=prop))
        return False

def onPropertyRequired(entity, mappedClass, prop, errors):
    '''
    Validation for required properties, whenever this validator is added will require the property to have a value on the
    provided entity.
    
    @param entity: object
        The entity to check for the property value.
    @param mappedClass: class
        The model mapped class of the entity.
    @param prop: Property
        The property that is unwanted.
    @param errors: list[Ref]
        The list of errors.
    '''
    assert isclass(mappedClass), 'Invalid mapped class %s' % mappedClass
    model = modelFor(mappedClass)
    assert isinstance(model, Model), 'Invalid mapped class %s, has no model' % mappedClass
    assert isinstance(entity, model.modelClass), 'Invalid entity %s for model %s' % (entity, model)
    assert isinstance(prop, Property), 'Invalid property %s' % prop
    assert isinstance(errors, list), 'Invalid errors list %s' % errors
    if not prop.has(entity):
        errors.append(Ref(_('Expected a value'), model=model, property=prop))
        return False

def onPropertyNone(entity, mappedClass, prop, errors):
    '''
    Validation for properties that are allowed not to have a value but if they have then the None value is not allowed.
    
    @param entity: object
        The entity to check for the property value.
    @param mappedClass: class
        The model mapped class of the entity.
    @param prop: Property
        The property that is unwanted.
    @param errors: list[Ref]
        The list of errors.
    '''
    assert isclass(mappedClass), 'Invalid mapped class %s' % mappedClass
    model = modelFor(mappedClass)
    assert isinstance(model, Model), 'Invalid mapped class %s, has no model' % mappedClass
    assert isinstance(entity, model.modelClass), 'Invalid entity %s for model %s' % (entity, model)
    assert isinstance(prop, Property), 'Invalid property %s' % prop
    assert isinstance(errors, list), 'Invalid errors list %s' % errors
    if prop.has(entity) and prop.get(entity) is None:
        errors.append(Ref(_('Invalid value'), model=model, property=prop))
        return False

def onPropertyMaxLength(length, entity, mappedClass, prop, errors):
    '''
    Validation for properties that are allowed a maximum length for their value. If the property has a value and that
    value is of type @see: Sized it will be checked for the maximum lenght.
    
    @param length: integer
        The maximum length allowed for the property value.
    @param mappedClass: class
        The model mapped class of the entity.
    @param model: Model
        The model of the entity.
    @param prop: Property
        The property that is unwanted.
    @param errors: list[Ref]
        The list of errors.
    '''
    assert isinstance(length, int), 'Invalid length %s' % length
    assert isclass(mappedClass), 'Invalid mapped class %s' % mappedClass
    model = modelFor(mappedClass)
    assert isinstance(model, Model), 'Invalid mapped class %s, has no model' % mappedClass
    assert isinstance(entity, model.modelClass), 'Invalid entity %s for model %s' % (entity, model)
    assert isinstance(prop, Property), 'Invalid property %s' % prop
    assert isinstance(errors, list), 'Invalid errors list %s' % errors
    if prop.has(entity):
        val = prop.get(entity)
        if isinstance(val, Sized) and len(val) > length:
            errors.append(Ref(_('Maximum length allowed is %(maximum)i but got length %(provided)i') %
                              dict(maximum=length, provided=len(val)), model=model, property=prop))
            return False

def onModel(event, entity, mappedClass):
    '''
    This is a validation that triggers the validations found on the properties of the model.
    
    @param event: object immutable
        The event to trigger on the properties of the model.
    @param entity: object
        The entity to check for the property value.
    @param mappedClass: class
        The model mapped class of the entity.
    @raise InputException: the input exception with all the errors indicated by the properties validation.
    '''
    assert isclass(mappedClass), 'Invalid mapped class %s' % mappedClass
    model = modelFor(mappedClass)
    assert isinstance(model, Model), 'Invalid mapped class %s, has no model' % mappedClass
    assert isinstance(entity, model.modelClass), 'Invalid entity %s for model %s' % (entity, model)
    errors = []
    for name, prop in model.properties.items():
        callListeners(getattr(mappedClass, name), event, entity, mappedClass, prop, errors)
    if errors: raise InputException(*errors)
    
# --------------------------------------------------------------------

def processModelCall(call, mappedClass, argEntityIndex, args, keyargs):
    '''
    Process the validation for a model for the specified call.
    
    @param call: Call
        The call to process the model for.
    @param mappedClass: class
        The model mapped class of the entity.
    @param argEntityIndex: integer
        The index in the arguments (args) where to find the model entity to perform validations on.
    @param args: arguments
        The arguments of the call invocation.
    @param keyargs: key arguments
        The key arguments of the call invocation.
    '''
    assert isinstance(argEntityIndex, int), 'Invalid argument entity index %s' % argEntityIndex
    if len(args) > argEntityIndex:
        # Check the arguments length just in case the entity argument has a default.
        assert isinstance(call, Call), 'Invalid call %s' % call
        assert isclass(mappedClass), 'Invalid mapped class %s' % mappedClass
        model = modelFor(mappedClass)
        assert isinstance(model, Model), 'Invalid mapped class %s, has no model' % mappedClass
        entity = args[argEntityIndex]
        assert isinstance(entity, model.modelClass), 'Invalid entity %s for model %s' % (entity, model)
        if call.method == INSERT:
            return callListeners(mappedClass, EVENT_VALID_INSERT, entity, mappedClass)
        if call.method == UPDATE:
            return callListeners(mappedClass, EVENT_VALID_UPDATE, entity, mappedClass)

def bindValidations(proxyService, mappings):
    '''
    Binds the registered model validations to the provided service. Basically all models detected to be used by the
    service in insert and update methods will have their validations triggered whenever this methods are called.
    
    @param proxyService: proxy service
        The proxy of the service to bind the validations to.
    @param mappings: dictionary{class, class}
        A dictionary containing as a key the model API class and as a value the mapping class for the model.
    '''
    registerProxyBinder(proxyService)
    service = serviceFor(proxyService)
    assert isinstance(service, Service), 'Invalid service proxy %s, has no service attached' % proxyService
    assert isinstance(mappings, dict), 'Invalid mappings %s' % mappings
    for name, call in service.calls.items():
        assert isinstance(call, Call)
        for index, inp in enumerate(call.inputs):
            assert isinstance(inp, Input)
            if isinstance(inp.type, TypeModel):
                mappedClass = mappings.get(inp.type.model.modelClass)
                if isclass(mappedClass):
                    bindBeforeListener(getattr(proxyService, name),
                                       functools.partial(processModelCall, call, mappedClass, index))
