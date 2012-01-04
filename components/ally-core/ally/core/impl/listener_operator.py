'''
Created on Aug 24, 2011

@package Newscoop
@copyright 2011 Sourcefabric o.p.s.
@license http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides listener methods to handle API operators validation.
'''

from _abcoll import Sized
from ally import internationalization
from ally.api.configure import serviceFor
from ally.api.operator import Property, Model, Service, Call, UPDATE, INSERT, \
    DELETE
from ally.api.type import Input, TypeModel, TypeProperty, typeFor
from ally.exception import InputException, Ref
from ally.listener import callListeners, ProxyCall, addListener, wrapInstance, \
    wrapMethod, ProxyListener
import functools

# --------------------------------------------------------------------
# TODO: properly document functions
EVENT_VALID_INSERT = '_EVENT_valid_insert'
EVENT_VALID_UPDATE = '_EVENT_valid_update'

_ = internationalization.translator(__name__)

# --------------------------------------------------------------------
    
def validateProperty(prop, validator, key=(EVENT_VALID_INSERT, EVENT_VALID_UPDATE), index=4):
    prop = _getProperty(prop)
    addListener(prop, key, validator, index)

def validateAutoId(prop, index=1):
    validateProperty(prop, _onPropertyUnwanted, EVENT_VALID_INSERT, index)
    validateProperty(prop, (_onPropertyRequired, _onPropertyNone), EVENT_VALID_UPDATE, index)

def validateRequired(prop, index=2):
    validateProperty(prop, (_onPropertyRequired, _onPropertyNone), EVENT_VALID_INSERT, index)
    validateProperty(prop, _onPropertyNone, EVENT_VALID_UPDATE, index)
    
def validateMaxLength(prop, length, index=3):
    validateProperty(prop, functools.partial(_onPropertyMaxLength, length), index)
    
def validateManaged(prop, index=1):
    validateProperty(prop, _onPropertyUnwanted, index)
    
# --------------------------------------------------------------------

def validateModel(model, validator, key=(EVENT_VALID_INSERT, EVENT_VALID_UPDATE), index=2):
    model = _getModel(model)
    addListener(model, key, validator, index)

def validateModelProperties(model, index=1):
    validateModel(model, functools.partial(_onModel, EVENT_VALID_INSERT), EVENT_VALID_INSERT, index)
    validateModel(model, functools.partial(_onModel, EVENT_VALID_UPDATE), EVENT_VALID_UPDATE, index)

# --------------------------------------------------------------------

def validateService(service):
    srv = serviceFor(service)
    assert isinstance(srv, Service), 'Invalid service instance %s, has no service attached' % service
    proxy = wrapInstance(service)
    for name, call in srv.calls.items():
        assert isinstance(call, Call)
        for index, inp in enumerate(call.inputs):
            assert isinstance(inp, Input)
            if isinstance(inp.type, TypeModel):
                proxyCall = wrapMethod(proxy, name)
                assert isinstance(proxyCall, ProxyCall)
                proxyCall.addBeforeListener(functools.partial(_onCallModel, call, inp.type.model, index))
    return proxy

# --------------------------------------------------------------------
    
def bindLock(proxyListener, lock):
    '''
    Binds the provided proxy listener to the provided lock. Basically all proxies binded will execute one after
    another regardless of the execution thread.
    
    @param proxyCall: ProxyListener
        The proxy listener obtained by wrapping the desired instance or method.
    @param lock: RLock
        The lock object.
    '''
    assert isinstance(proxyListener, ProxyListener), 'Invalid proxy listener %s' % proxyListener
    def _lock(*args):
        lock.acquire()
    def _unlock(*args):
        lock.release()
    proxyListener.addBeforeListener(_lock, index= -1)
    proxyListener.addAfterListener(_unlock, index=1001)
    proxyListener.addExceptionListener(_unlock, index=1001)

def bindLockForService(service, lock, methods=(INSERT, DELETE)):
    '''
    Binds lock on the service calls that are of the specified methods.
    
    @see: bindLock
    '''
    for call in serviceFor(service).calls.values():
        assert isinstance(call, Call)
        if call.method in methods: bindLock(wrapMethod(service, call.name), lock)

# --------------------------------------------------------------------

def _getProperty(propRef):
    if not isinstance(propRef, Property):
        typ = typeFor(propRef)
        if isinstance(typ, TypeProperty): prop = typ.property
    else:
        prop = propRef
    assert isinstance(prop, Property), 'No property available for %s' % propRef
    return prop

def _getModel(modelRef):
    if not isinstance(modelRef, Model):
        typ = typeFor(modelRef)
        if isinstance(typ, TypeModel): model = typ.model
    else:
        model = modelRef
    assert isinstance(model, Model), 'No model available for %s' % modelRef
    return model
    
# --------------------------------------------------------------------

def _onPropertyUnwanted(entity, model, prop, errors):
    assert isinstance(prop, Property)
    if prop.has(entity):
        errors.append(Ref(_('No value expected'), model=model, property=prop))
        return False

def _onPropertyRequired(entity, model, prop, errors):
    assert isinstance(prop, Property)
    if not prop.has(entity):
        errors.append(Ref(_('Expected a value'), model=model, property=prop))
        return False

def _onPropertyNone(entity, model, prop, errors):
    assert isinstance(prop, Property)
    if prop.has(entity) and prop.get(entity) is None:
        errors.append(Ref(_('Invalid value'), model=model, property=prop))
        return False

def _onPropertyMaxLength(length, entity, model, prop, errors):
    assert isinstance(prop, Property)
    if prop.has(entity):
        val = prop.get(entity)
        if isinstance(val, Sized) and len(val) > length:
            errors.append(Ref(_('Maximum length allowed is $1 but got length $2', length, len(val)),
                              model=model, property=prop))
            return False

def _onModel(event, entity, model):
    assert isinstance(model, Model)
    errors = []
    for prop in model.properties.values():
        callListeners(prop, event, entity, model, prop, errors)
    if errors: raise InputException(*errors)

def _onCallModel(call, model, index, args, keyargs):
    if len(args) > index:
        assert isinstance(call, Call)
        if call.method == INSERT:
            return callListeners(model, EVENT_VALID_INSERT, args[index], model)
        if call.method == UPDATE:
            return callListeners(model, EVENT_VALID_UPDATE, args[index], model)
