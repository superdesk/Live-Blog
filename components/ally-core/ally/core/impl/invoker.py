'''
Created on Jun 25, 2011

@package: ally core
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the invokers implementations.
'''

from ally.api.type import Input, typeFor
from ally.core.spec.resources import Invoker, Normalizer
from ally.api.operator.container import Call, Model
from ally.api.operator.type import TypeService, TypeModel
from ally.exception import DevelError

# --------------------------------------------------------------------

class InvokerCall(Invoker):
    '''
    Provides invoking for API calls.
    '''

    def __init__(self, implementation, call):
        '''
        @see: Invoker.__init__
        
        @param implementation: object
            The implementation for the call of the access.
        @param call: Call
            The call of the access.
        '''
        typ = typeFor(implementation)
        assert isinstance(typ, TypeService), 'Invalid service implementation %s' % implementation
        assert isinstance(call, Call), 'Invalid call %s' % call
        super().__init__(call.output, call.name, call.inputs)

        self.implementation = implementation
        self.call = call

        self.service = typ.service
        self.clazz = typ.forClass
        self.invoke = getattr(self.implementation, self.call.name)
        # We just assign the invoke method to the actual service method

    def invoke(self, *args):
        '''
        @see: InvokerCall.invoke
        '''
        raise TypeError('Improper invoker initialization, this should have never been called')

# --------------------------------------------------------------------

class InvokerFunction(Invoker):
    '''
    Provides invoking for API calls.
    '''

    def __init__(self, output, function, inputs):
        '''
        @see: Invoker.__init__
        
        @param function: Callable
            The Callable to invoke.
        '''
        assert callable(function), 'Invalid input callable provided %s' % function
        super().__init__(output, function.__name__, inputs)
        self.invoke = function

    def invoke(self, *args):
        '''
        @see: InvokerCall.invoke
        '''
        raise TypeError('Improper invoker initialization, this should have never been called')

# --------------------------------------------------------------------

class InvokerSetId(Invoker):
    '''
    Wraps an invoker that expects an entity as the input. This invoker will set on that entity the designated
    properties based on the arguments.
    As an example, if you have the wrapped invoker looking like 
    [...]%(..,Entity)
    to look like
    [...]%(..., Entity.propery..., Entity).
    '''

    def __init__(self, invoker, normalizer):
        '''
        @see: Invoker.__init__
        
        @param invoker: Invoker
            The Invoker to be wrapped.
        @param normalizer: Normalizer
            The normalizer used for transforming the content property names.
        '''
        assert isinstance(invoker, Invoker), 'Invalid invoker %s' % invoker
        typeModel = invoker.inputs[invoker.mandatory - 1].type
        assert isinstance(typeModel, TypeModel), \
        'Invalid invoker %s, needs to have as the last entry a type model' % invoker
        assert isinstance(normalizer, Normalizer), 'Invalid Normalizer object %s' % normalizer

        model = typeModel.container
        assert isinstance(model, Model)

        inputs = list(invoker.inputs[:invoker.mandatory - 1])
        inputId = Input(model.name + model.propertyId, typeFor(getattr(typeModel.forClass, model.propertyId)))
        inputs.insert(invoker.mandatory - 1, inputId)
        super().__init__(invoker.output, invoker.name, inputs)

        self.invoker = invoker
        self.normalizer = normalizer
        self.propertyId = model.propertyId

    def invoke(self, *args):
        '''
        @see: Invoker.invoke
        '''
        obj = args[self.mandatory - 1]
        arg = args[self.invoker.mandatory - 1]
        val = getattr(obj, self.propertyId)
        if val is not None:
            if val != arg:
                raise DevelError('Cannot have two distinct values %r and %r for %r' %
                                 (arg, val, self.normalizer.normalize(self.propertyId)))
            setattr(obj, self.propertyId, arg)

        wargs = list(args[:self.invoker.mandatory - 1])
        wargs.append(obj)
        wargs.extend(args[self.mandatory:])
        return self.invoker.invoke(*wargs)
