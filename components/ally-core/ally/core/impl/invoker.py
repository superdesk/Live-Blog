'''
Created on Jun 25, 2011

@package: ally core
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the invokers implementations.
'''

from ally.api.model import Part
from ally.api.operator.container import Call
from ally.api.operator.type import TypeService
from ally.api.type import Input, typeFor, Iter
from ally.core.spec.resources import Invoker
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
        super().__init__(call.name, call.method, call.output, call.inputs, call.hints)

        self.implementation = implementation
        self.call = call

        self.service = typ.service
        self.clazz = typ.forClass

    def invoke(self, *args):
        '''
        @see: InvokerCall.invoke
        '''
        return getattr(self.implementation, self.call.name)(*args)

    def location(self):
        '''
        @see: InvokerCall.location
        '''
        fnc = getattr(self.clazz, self.call.name).__code__
        try: name = fnc.__name__
        except AttributeError: name = self.call.name
        return (fnc.co_filename, fnc.co_firstlineno, name)

# --------------------------------------------------------------------

class InvokerFunction(Invoker):
    '''
    Provides invoking for API calls.
    '''

    def __init__(self, method, function, output, inputs, hints, name=None):
        '''
        @see: Invoker.__init__
        
        @param function: Callable
            The Callable to invoke.
        '''
        assert callable(function), 'Invalid input callable provided %s' % function
        super().__init__(name or function.__name__, method, output, inputs, hints)
        self.function = function

    def invoke(self, *args):
        '''
        @see: InvokerCall.invoke
        '''
        return self.function(*args)

    def location(self):
        '''
        @see: InvokerCall.location
        '''
        fnc = self.function.__code__
        try: name = self.function.__name__
        except AttributeError: name = '<NA>'
        return (fnc.co_filename, fnc.co_firstlineno, name)

# --------------------------------------------------------------------

class InvokerAssemblePart(Invoker):
    '''
    Delegates the invoking call to two other invokers, one will generate a list and the other will generate an integer
    which will be considered the total count of the limited list items, based on the results a single Part object will
    be returned.
    '''

    def __init__(self, invokerList, invokerCount):
        '''
        @see: Invoker.__init__
        
        @param invokerList: Invoker
            The Invoker that will generate the list items.
        @param invokerCount: Invoker
            The Invoker that will generate the total items count.
        '''
        assert isinstance(invokerList, Invoker), 'Invalid invoker list %s' % invokerList
        assert isinstance(invokerList.output, Iter), 'Invalid invoker list output type %s' % invokerList
        assert isinstance(invokerCount, Invoker), 'Invalid invoker count %s' % invokerCount

        super().__init__(invokerList.name, invokerList.method, invokerList.output, invokerList.inputs,
                         invokerList.hints)

        self.invokerList = invokerList
        self.invokerCount = invokerCount

        countArgs = set(input.name for input in invokerCount.inputs)
        self.positions = [k for k, input in enumerate(invokerList.inputs) if input.name in countArgs]

    def invoke(self, *args):
        '''
        @see: Invoker.invoke
        '''
        countArgs = []
        for k in self.positions:
            if k < len(args): countArgs.append(args[k])
            else: break
        return Part(self.invokerList.invoke(*args), self.invokerCount.invoke(*countArgs))

    def location(self):
        '''
        @see: InvokerCall.location
        '''
        return self.invokerList.location()

# --------------------------------------------------------------------

class InvokerRestructuring(Invoker):
    '''
    Invoker that provides the inputs restructuring based on a list of indexes.
    '''

    def __init__(self, invoker, inputs, indexes, indexesSetValue={}):
        '''
        @see: Invoker.__init__
        
        @param invoker: Invoker
            The Invoker to be wrapped.
        @param inputs: list[Input]|tuple(Input)
            The inputs that are represented by this restructuring invoker.
        @param indexes: list[integer]|tuple(integer)
            The indexes to restructure by, the value represents the index within the provided inputs and the 
            position in the list represents in the index in the provided invoker inputs.
        @param indexesSetValue: dictionary{integer:dictionary{string, integer}}
            A dictionary of indexes to be used for setting values in objects. The key is the index of the invoker input
            that contains the object to set the value to, as a value another dictionary that has as a value the property
            name of the value to set on the object and as a value the index form the provided inputs.
        '''
        assert isinstance(invoker, Invoker), 'Invalid invoker %s' % invoker
        assert isinstance(indexes, (list, tuple)), 'Invalid indexes %s' % indexes
        assert isinstance(indexesSetValue, dict), 'Invalid indexes for value set %s' % indexesSetValue
        assert len(indexes) == len(invoker.inputs), 'Invalid indexes %s' % indexes
        if __debug__:
            for index in indexes:
                assert isinstance(index, int), 'Invalid index %s' % index
                assert index >= 0 and index < len(inputs), 'Index out of inputs range %s' % index
            for index, toSet in indexesSetValue.items():
                assert isinstance(index, int), 'Invalid index %s' % index
                assert index >= 0 and index < len(invoker.inputs), 'Index out of invoker inputs range %s' % index
                for prop, fromIndex in toSet.items():
                    assert isinstance(prop, str), 'Invalid property %s' % prop
                    assert isinstance(fromIndex, int), 'Invalid index %s' % fromIndex
                    assert fromIndex >= 0 and fromIndex < len(inputs), 'Index out of inputs range %s' % fromIndex

        self.invoker = invoker
        self.indexes = indexes
        self.indexesSetValue = indexesSetValue

        super().__init__(invoker.name, invoker.method, invoker.output, inputs, invoker.hints)

    def invoke(self, *args):
        '''
        @see: Invoker.invoke
        '''
        lenArgs, wargs = len(args), []
        for index in self.indexes:
            if index < lenArgs: value = args[index]
            else:
                inp = self.inputs[index]
                assert isinstance(inp, Input)
                if not inp.hasDefault: raise DevelError('No value available for %r for %s' % (inp.name, self))
                value = inp.default

            wargs.append(value)

        for index, toSet in self.indexesSetValue.items():
            obj = wargs[index]
            for prop, fromIndex in toSet.items():
                arg = args[fromIndex]
                val = getattr(obj, prop)
                if val is None: setattr(obj, prop, arg)
                elif val != arg: raise DevelError('Cannot set value %s, expected value %s' % (val, arg))

        return self.invoker.invoke(*wargs)

    def location(self):
        '''
        @see: InvokerCall.location
        '''
        return self.invoker.location()
