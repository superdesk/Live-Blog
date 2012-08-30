'''
Created on Aug 24, 2011

@package ally api
@copyright 2011 Sourcefabric o.p.s.
@license http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides binding listener function to handle API operators validation.
'''

from ..api.config import INSERT, UPDATE
from ..api.operator.container import Call
from ..api.operator.type import TypeModel, TypeModelProperty, TypeService
from ..api.type import typeFor
from ..exception import InputError, Ref
from ..internationalization import _
from .binder import bindListener, callListeners, registerProxyBinder, \
    bindBeforeListener, indexBefore, INDEX_DEFAULT
from collections import Sized
from functools import partial
from inspect import isclass
import functools
from ally.container.binder import BindableSupport
from ally.api.type import Input

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

EVENT_MODEL_INSERT = 'model_insert'
# Listener key used for the model insert
EVENT_MODEL_UPDATE = 'model_update'
# Listener key used for the model update

EVENT_PROP_INSERT = 'insert:%s'
# Listener key used for the property insert
EVENT_PROP_UPDATE = 'update:%s'
# Listener key used for the property update

# --------------------------------------------------------------------

def validateModel(clazz, validator, key=(EVENT_MODEL_INSERT, EVENT_MODEL_UPDATE), index=INDEX_MODEL):
    '''
    @see: bindListener
    Binds a validation listener on the model that will be triggered for the provided event keys.
    
    @param clazz: class
        The model class to bind to.
    @param validator: Callable|tuple(Callable)
        The validator(s) to use. 
    @param key: object immutable|tuple(object immutable)
        The event keys to bind the validation to.
    @param index: string
        The index at which to position the validation.
    '''
    assert isclass(clazz), 'Invalid class %s' % clazz
    assert isinstance(typeFor(clazz), TypeModel), 'Invalid model class %s' % clazz
    bindListener(clazz, key, validator, index)

# --------------------------------------------------------------------

def validateProperty(refProp, validator, key=(EVENT_PROP_INSERT, EVENT_PROP_UPDATE), index=INDEX_PROP):
    '''
    @see: bindListener
    Binds a validation listener on the property that will be triggered for the provided event keys.
    
    @param refProp: TypeSupport|TypeModelProperty
        The property reference to get the property to bind to.
    @param validator: Callable|tuple(Callable)
        The validator(s) to use. 
    @param key: object immutable|tuple(object immutable)
        The event keys to bind the validation to.
    @param index: string
        The index at which to position the validation.
    '''
    typ = typeFor(refProp)
    assert isinstance(typ, TypeModelProperty), 'No model property available for %s' % refProp
    key = key if isinstance(key, (list, tuple)) else [key]
    key = [k % typ.property for k in key]
    bindListener(typ.parent.clazz, key, validator, index)

def validateAutoId(refProp):
    '''
    Binds an auto id validation on the property. The auto id validation consists of:
     - the property will not accept any external value when inserting.
     - the property has to have a valid value when updating.
    
    @param refProp: TypeSupport|TypeModelProperty
        The property reference to get the property to bind to.
    '''
    validateProperty(refProp, onPropertyUnwanted, EVENT_PROP_INSERT, INDEX_PROP_AUTO_ID)
    validateProperty(refProp, (onPropertyRequired, onPropertyNone), EVENT_PROP_UPDATE, INDEX_PROP_AUTO_ID)

def validateRequired(refProp):
    '''
    Binds a required validation on the property. The required validation consists of:
     - the property has to have a valid value when inserting.
     - if the property has a value when updating it has to be valid, if there is no value than no action is taken.
    
    @param refProp: TypeSupport|TypeModelProperty
        The property reference to get the property to bind to.
    '''
    validateProperty(refProp, (onPropertyRequired, onPropertyNone), EVENT_PROP_INSERT, INDEX_PROP_REQUIRED)
    validateProperty(refProp, onPropertyNone, EVENT_PROP_UPDATE, INDEX_PROP_REQUIRED)

def validateMaxLength(refProp, length):
    '''
    Binds a maximum length validation on the property. The maximum length validation consists of:
     - if the property has a value when inserting or updating it has to be less then the specified length.
    
    @param refProp: TypeSupport|TypeModelProperty
        The property reference to get the property to bind to.
    @param length: integer
        The maximum length allowed for the property value.
    '''
    assert isinstance(length, int), 'Invalid length %s' % length
    validateProperty(refProp, functools.partial(onPropertyMaxLength, length), index=INDEX_PROP_MAX_LEN)

def validateManaged(prop, key=(EVENT_PROP_INSERT, EVENT_PROP_UPDATE)):
    '''
    Binds a managed validation on the property. The managed validation consists of:
     - the property is not allowed to have any value when inserting or updating.
    
    @param refProp: TypeSupport|TypeModelProperty
        The property reference to get the property to bind to.
    '''
    validateProperty(prop, onPropertyUnwanted, key, INDEX_PROP_MANAGED)

def bindValidations(proxy, mappings=None):
    '''
    Binds the registered model validations to the provided service. Basically all models detected to be used by the
    service in insert and update methods will have their validations triggered whenever this methods are called.
    
    @param proxy: proxy service
        The proxy of the service to bind the validations to.
    @param mappings: dictionary{class, class}
        A dictionary containing mapping classes, as a key the class to be replaced and as a value the replacing class.
    '''
    typ = typeFor(proxy)
    assert isinstance(typ, TypeService), 'Invalid service proxy %s' % proxy
    if mappings is None: mappings = {}
    else: assert isinstance(mappings, dict), 'Invalid mappings %s' % mappings
    assert isinstance(proxy, typ.clazz), 'Invalid proxy %s for service %s' % (proxy, typ.clazz)
    registerProxyBinder(proxy)

    for call in typ.service.calls:
        assert isinstance(call, Call)
        if call.method in (INSERT, UPDATE):
            positions = {}
            for k, inp in enumerate(call.inputs):
                assert isinstance(inp, Input)
                typ = inp.type
                if isinstance(typ, TypeModel):
                    if typ.clazz in mappings:
                        typ = typeFor(mappings[typ.clazz])
                        assert isinstance(typ, TypeModel), 'Invalid model mapping class %s' % mappings[typ.clazz]
                    if isinstance(typ.clazz, BindableSupport):
                        positions[k] = typ
            if positions:
                bindBeforeListener(getattr(proxy, call.name),
                                   partial(onCallValidateModel, call.method == INSERT, positions))

# --------------------------------------------------------------------
# validation listener methods

def onPropertyUnwanted(prop, obj, errors):
    '''
    Validation for unwanted properties, whenever this validator is added will not allow the property to have a value on 
    the provided entity.

    @param prop: string
        The property name that is unwanted.
    @param obj: object
        The entity to check for the property value.
    @param errors: list[Ref]
        The list of errors.
    '''
    assert isinstance(prop, str), 'Invalid property name %s' % prop
    assert obj is not None, 'None is not a valid object'
    assert isinstance(errors, list), 'Invalid errors list %s' % errors

    if getattr(obj.__class__, prop) in obj:
        errors.append(Ref(_('No value expected'), ref=getattr(obj.__class__, prop)))
        return False

def onPropertyRequired(prop, obj, errors):
    '''
    Validation for required properties, whenever this validator is added will require the property to have a value on the
    provided entity.

    @param prop: string
        The property that is required.
    @param clazz: class
        The model class of the object entity.
    @param obj: object
        The entity to check for the property value.
    @param errors: list[Ref]
        The list of errors.
    '''
    assert isinstance(prop, str), 'Invalid property name %s' % prop
    assert obj is not None, 'None is not a valid object'
    assert isinstance(errors, list), 'Invalid errors list %s' % errors

    if not getattr(obj.__class__, prop) in obj:
        errors.append(Ref(_('Expected a value'), ref=getattr(obj.__class__, prop)))
        return False

def onPropertyNone(prop, obj, errors):
    '''
    Validation for properties that are allowed not to have a value but if they have then the None value is not allowed.
    
    @param prop: string
        The property to check if has a None value.
    @param clazz: class
        The model class of the object entity.
    @param obj: object
        The entity to check for the property value.
    @param errors: list[Ref]
        The list of errors.
    '''
    assert isinstance(prop, str), 'Invalid property name %s' % prop
    assert obj is not None, 'None is not a valid object'
    assert isinstance(errors, list), 'Invalid errors list %s' % errors

    if getattr(obj.__class__, prop) in obj and getattr(obj, prop) is None:
        errors.append(Ref(_('Invalid value'), ref=getattr(obj.__class__, prop)))
        return False

def onPropertyMaxLength(length, prop, obj, errors):
    '''
    Validation for properties that are allowed a maximum length for their value. If the property has a value and that
    value is of type @see: Sized it will be checked for the maximum lenght.
    
    @param length: integer
        The maximum length allowed for the property value.
    @param prop: string
        The property name that has to be checked for maximum length.
    @param clazz: class
        The model class of the object entity.
    @param obj: object
        The entity to check for the property value.
    @param errors: list[Ref]
        The list of errors.
    '''
    assert isinstance(length, int), 'Invalid length %s' % length
    assert isinstance(prop, str), 'Invalid property name %s' % prop
    assert obj is not None, 'None is not a valid object'
    assert isinstance(errors, list), 'Invalid errors list %s' % errors

    if getattr(obj.__class__, prop) in obj:
        val = getattr(obj, prop)
        if isinstance(val, Sized) and len(val) > length:
            errors.append(Ref(_('Maximum length allowed is %(maximum)i but got length %(provided)i') %
                              {'maximum':length, 'provided':len(val)}, ref=getattr(obj.__class__, prop)))
            return False

# --------------------------------------------------------------------

def onCallValidateModel(onInsert, positions, args, keyargs):
    '''
    Process the validation for a model for the specified call.
    
    @param onInsert: boolean
        Flag indicating that the validation should be performed for insert if True, False for update.
    @param positions: dictionary{integer:TypeModel}
        As a key the indexes in the arguments (args) where to find the model(s) entity(s) to perform validations on and
        as a value the TypeModel for that position.
    @param args: arguments
        The arguments of the call invocation.
    @param keyargs: key arguments
        The key arguments of the call invocation.
    '''
    assert isinstance(onInsert, bool), 'Invalid on insert flag %s' % onInsert
    assert isinstance(positions, dict), 'Invalid argument positions %s' % positions
    errors = []
    for k, obj in enumerate(args):
        if obj is None: continue
        typ = positions.get(k)
        if typ is None: continue

        assert isinstance(typ, TypeModel), 'Invalid model type %s for index %s' % (typ, k)
        assert typ.isValid(obj), 'Invalid object %s for %s' % (obj, typ)
        if onInsert:
            if callListeners(typ.clazz, EVENT_MODEL_INSERT, obj, errors):
                for prop in typ.container.properties:
                    callListeners(typ.clazz, EVENT_PROP_INSERT % prop, prop, obj, errors)
        else:
            if callListeners(typ.clazz, EVENT_MODEL_UPDATE, obj, errors):
                for prop in typ.container.properties:
                    callListeners(typ.clazz, EVENT_PROP_UPDATE % prop, prop, obj, errors)

    if errors: raise InputError(*errors)
