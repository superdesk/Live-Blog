'''
Created on Jun 25, 2011

@package: ally core
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the invokers implementations.
'''

from ally.api.operator.container import Call
from ally.api.operator.type import TypeService
from ally.api.type import Input, typeFor
from ally.container.impl.proxy import proxiedClass
from ally.core.spec.resources import Invoker, InvokerInfo
from ally.exception import DevelError
from ally.support.util_sys import getAttrAndClass
from inspect import isclass, getdoc

# --------------------------------------------------------------------

class InvokerInfoMethod(InvokerInfo):
    '''
    Provides the info object for a class method.
    '''

    def __init__(self, name, clazz):
        '''
        Constructs the info function based on the provided function.
        
        @param name: string
            The class function name.
        @param clazz: class
            The class of the function.
        '''
        assert isinstance(name, str), 'Invalid function name %s' % name
        assert isclass(clazz), 'Invalid class %s' % clazz

        method, clazzDefiner = getAttrAndClass(clazz, name)
        super().__init__(name, method.__code__.co_filename, method.__code__.co_firstlineno, getdoc(method))

        self.clazz = clazz
        self.clazzDefiner = clazzDefiner

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

        infoIMPL = InvokerInfoMethod(call.name, proxiedClass(implementation.__class__))
        infoAPI = InvokerInfoMethod(call.name, typ.clazz)
        super().__init__(call.name, call.method, call.output, call.inputs, call.hints, infoIMPL, infoAPI)

        self.implementation = implementation
        self.call = call

    def invoke(self, *args):
        '''
        @see: Invoker.invoke
        '''
        return getattr(self.implementation, self.call.name)(*args)

class InvokerFunction(Invoker):
    '''
    Provides invoking for API calls.
    '''

    def __init__(self, method, function, output, inputs, hints, name=None, infoIMPL=None):
        '''
        @see: Invoker.__init__
        
        @param function: Callable
            The Callable to invoke.
        '''
        assert callable(function), 'Invalid input callable provided %s' % function

        name = name or function.__name__
        if infoIMPL is None:
            infoIMPL = InvokerInfo(name, function.__code__.co_filename, function.__code__.co_firstlineno,
                                   getdoc(function))
        else: assert isinstance(infoIMPL, InvokerInfo), 'Invalid invoker information %s' % infoIMPL
        super().__init__(name, method, output, inputs, hints, infoIMPL)
        self.function = function

    def invoke(self, *args):
        '''
        @see: Invoker.invoke
        '''
        return self.function(*args)

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
            that contains the object to set the value to, as a value another dictionary that has as a key the property
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

        super().__init__(invoker.name, invoker.method, invoker.output, inputs, invoker.hints,
                         invoker.infoIMPL, invoker.infoAPI)

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
                if not inp.hasDefault: raise DevelError('No value available for \'%s\' for %s' % (inp.name, self))
                value = inp.default

            wargs.append(value)

        for index, toSet in self.indexesSetValue.items():
            obj = wargs[index]
            for prop, fromIndex in toSet.items():
                arg = args[fromIndex]
                val = getattr(obj, prop)
                if val is None: setattr(obj, prop, arg)
                elif val != arg: raise DevelError('Cannot set value %s for \'%s\', expected value %s' % (val, prop, arg))

        return self.invoker.invoke(*wargs)
