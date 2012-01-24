'''
Created on Jun 25, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the invokers implementations.
'''

from _abcoll import Callable
from ally.api.operator import Service, Call, Property, Model
from ally.api.type import TypeProperty, Input, TypeModel
from ally.core.spec.resources import Invoker, Normalizer
from ally.exception import DevelException

# --------------------------------------------------------------------

class InvokerCall(Invoker):
    '''
    Provides invoking for API calls.
    '''
    
    def __init__(self, service, implementation, call):
        '''
        @see: Invoker.__init__
        
        @param service: Service
            The service for the call of the access.
        @param implementation: object
            The implementation for the call of the access.
        @param call: Call
            The call of the access.
        '''
        assert isinstance(service, Service), 'Invalid service %s' % service
        assert isinstance(call, Call), 'Invalid call %s' % call
        self.service = service
        self.implementation = implementation
        self.call = call
        super().__init__(call.outputType, call.name, call.inputs, call.mandatoryCount)

    def invoke(self, *args):
        '''
        @see: InvokerCall.invoke
        '''
        return self.call.call(self.implementation, args)

# --------------------------------------------------------------------

class InvokerFunction(Invoker):
    '''
    Provides invoking for API calls.
    '''
    
    def __init__(self, outputType, function, inputs, mandatoryCount):
        '''
        @see: Invoker.__init__
        
        @param function: Callable
            The Callable to invoke.
        '''
        assert isinstance(function, Callable), 'Invalid input callable provided %s' % function
        super().__init__(outputType, function.__name__, inputs, mandatoryCount)
        self.function = function

    def invoke(self, *args):
        '''
        @see: InvokerCall.invoke
        '''
        return self.function(*args)
        
# --------------------------------------------------------------------

class InvokerSetProperties(Invoker):
    '''
    Wraps an invoker that expects an entity as the input. This invoker will set on that entity the designated
    properties based on the arguments.
    As an example, if you have the wrapped invoker looking like 
    [...]%(..,Entity)
    to look like
    [...]%(..., Entity.propery..., Entity).
    '''
    
    def __init__(self, invoker, model, properties, normalizer):
        '''
        @see: Invoker.__init__
        
        @param invoker: Invoker
            The Invoker to be wrapped.
        @param model: Model
            The model of the properties to extend the invoker with.
        @param properties: list[Property]
            The list of properties to extend the invoker with.
        @param normalizer: Normalizer
            The normalizer used for transforming the content property names.
        '''
        assert isinstance(invoker, Invoker), 'Invalid invoker %s' % invoker
        assert isinstance(invoker.inputs[invoker.mandatoryCount - 1].type, TypeModel) and \
        invoker.inputs[invoker.mandatoryCount - 1].type.model == model, \
        'Invalid invoker %s, needs to have the last entry a type model for %s' % (invoker, model)
        assert isinstance(model, Model), 'Invalid model %s' % model
        assert isinstance(properties, list) and len(properties) > 0, \
        'Invalid properties %s, need at least one property' % properties
        assert isinstance(normalizer, Normalizer), 'Invalid Normalizer object %s' % normalizer
        inputs = invoker.inputs[0:invoker.mandatoryCount - 1]
        for prop in properties:
            assert isinstance(prop, Property), 'Invalid property %s' % prop
            inputs.append(Input(model.name + prop.name, TypeProperty(model, prop)))
        inputs.extend(invoker.inputs[invoker.mandatoryCount - 1:])
        super().__init__(invoker.outputType, invoker.name, inputs, invoker.mandatoryCount + len(properties))
        self.invoker = invoker
        self.properties = properties
        self.normalizer = normalizer
        
    def invoke(self, *args):
        '''
        @see: Invoker.invoke
        '''
        entity = args[self.mandatoryCount - 1]
        for k in range(0, len(self.properties)):
            prop = self.properties[k]
            arg = args[k + self.invoker.mandatoryCount - 1]
            assert isinstance(prop, Property)
            val = prop.get(entity)
            if val is not None:
                if val != arg:
                    raise DevelException('Cannot have two distinct values %r and %r for %r' % 
                                           (arg, val, self.normalizer.normalize(prop.name)))
            else:
                prop.set(entity, arg)
        wargs = list(args[0:self.invoker.mandatoryCount - 1])
        wargs.append(entity)
        wargs.extend(args[self.mandatoryCount:])
        return self.invoker.invoke(*wargs)
