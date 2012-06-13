'''
Created on Jun 11, 2012

@package: utilities
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Module containing the support for a chained processors execution of context type objects.
'''

from ally.design.context import Context, Attribute, DEFINED, OPTIONAL
from ally.support.util_sys import callerLocals
from collections import Iterable, deque
from inspect import isclass, isfunction, getfullargspec
import abc
import logging

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

class Call:
    '''
    Container for a call.
    '''
    __slots__ = ('call', 'contexts')

    def __init__(self, call, contexts):
        '''
        Construct the call.
        
        @param call: callable
            The callable of the call.
        @param contexts: dictionary{string, context class}
            The contexts to be associated with the call.
        '''
        assert callable(call), 'Invalid call %s' % call
        assert isinstance(contexts, dict), 'Invalid contexts %s' % contexts
        if __debug__:
            for key, context in contexts.items():
                assert isinstance(key, str), 'Invalid context name %s' % key
                assert isclass(context), 'Invalid class %s for %s' % (context, key)
                assert issubclass(context, Context), 'Invalid context class %s for %s' % (context, key)

        self.call = call
        self.contexts = contexts

class Calls:
    '''
    Container for the the processor calls with contexts specifications.
    '''
    __slots__ = ('calls',)

    def __init__(self):
        '''
        Construct the calls container.
        '''
        self.calls = []

    def add(self, call, contexts):
        '''
        Add to the calls container the provided call that will be associated with the contexts.
        
        @param call: callable
            The call to be added.
        @param contexts: dictionary{string, context class}
            The contexts to be associated with the call.
        '''
        self.calls.append(Call(call, contexts))

class IHandler(metaclass=abc.ABCMeta):
    '''
    The handler prepares the processing that will be used for creating execution chains.
    '''

    @abc.abstractmethod
    def prepare(self, calls):
        '''
        Prepare the calls for processing.
        
        @param calls: Calls
            The processors calls to prepare.
        '''

# --------------------------------------------------------------------

class Contexts:
    '''
    Container for the context classes.
    '''

    def __init__(self, **contexts):
        '''
        Construct the contexts container.
        
        @param contexts: key arguments of contexts
            The key arguments to be used in calling the processors.
        '''
        for name, context in contexts.items(): setattr(self, name, context)

    if __debug__:

        def __setattr__(self, name, value):
            '''
            Used for validating that all values that are set are of the context type.
            '''
            assert isinstance(name, str), 'Invalid name %s' % name
            assert isinstance(value, Context), 'Invalid context %s' % value

            object.__setattr__(self, name, value)

class Processing:
    '''
    Container for processor's, provides chains for their execution.
    !!! Attention, never ever use a processing in multiple threads, only one thread is allowed to execute 
    a processing at one time.
    '''
    __slots__ = ('ctxs', 'processors')

    def __init__(self, ctxs, processors):
        '''
        @param ctxs: Contexts
            The context classes associated with the processing.
        @param processors: list[callable]
            The processors used by this processing.
        '''
        assert isinstance(ctxs, Contexts), 'Invalid contexts %s' % ctxs
        assert isinstance(processors, list), 'Invalid processors %s' % processors
        if __debug__:
            for proc in processors: assert callable(proc), 'invalid processor %s' % proc

        self.ctxs = ctxs
        self.processors = processors

    def newChain(self):
        '''
        Constructs a new processors chain.
        
        @return: Chain
            The chain of processors.
        '''
        return Chain(self.processors)

class Chain:
    '''
    A chain that contains a list of processors (callables) that are executed one by one. Each processor will have
     the duty to proceed with the processing if is the case by calling the chain.
    '''

    def __init__(self, processors):
        '''
        Initializes the chain with the processors to be executed.
        
        @param processors: Iterable(callable)
            The iterable of callables to be executed. Attention the order in which the processors are provided
            is critical since one processor is responsible for delegating to the next.
        '''
        assert isinstance(processors, Iterable), 'Invalid processors %s' % processors
        self._processors = deque(processors)
        if __debug__:
            for proc in self._processors: assert callable(proc), 'Invalid processor %s' % proc
        self._consumed = False

    def proceed(self):
        '''
        Indicates to the chain that it should proceed with the chain execution after a processor has returned. 
        The proceed is available only when the chain is in execution. The execution is continued with the same
        arguments.
        '''
        self._proceed = True

    def process(self, **keyargs):
        '''
        Called in order to execute the next processors in the chain. This method will stop processing when all
        the processors have been executed.
        
        @param keyargs: key arguments
            The key arguments that are passed on to the next processors.
        '''
        proceed = True
        while proceed:
            proceed = self._proceed = False
            if len(self._calls) > 0:
                processor = self._processors.popleft()
                assert log.debug('Processing %s', processor) or True
                processor.process(self, **keyargs)
                assert log.debug('Processing finalized %r', processor) or True

                if self._proceed:
                    assert log.debug('Proceed signal received, continue execution') or True
                    proceed = self._proceed
            else:
                assert log.debug('Processing finalized by consuming') or True
                self._consumed = True

    def isConsumed(self):
        '''
        Checks if the chain is consumed.
        
        @return: boolean
            True if all processors from the chain have been executed, False if a processor from the chain has stopped
            the execution of the other processors.
        '''
        return self._consumed

# --------------------------------------------------------------------

def processor(function):
    '''
    Decorator used for marking processors functions inside a class in order to be used by handler.
    For detection of argument classes the arguments need to be annotated with the required or mokup classes.
    '''
    assert isfunction(function), 'Invalid function %s' % function
    fnArgs = getfullargspec(function)

    assert len(fnArgs.args) > 2, 'The processor function needs at least two arguments (self, chain)'
    assert 'self' == fnArgs.args[0], \
    'The processor needs to be tagged in a class definition (needs self as the first argument)'

    contexts = {}
    for name in fnArgs.args[2:]:
        clazz = fnArgs.annotations.get(name)
        if clazz is None: raise TypeError('Expected an annotation of class for argument %s' % name)
        if not isclass(clazz): raise TypeError('Not a class %s for argument %s' % (clazz, name))
        if not issubclass(clazz, Context): raise TypeError('Not a context class %s for argument %s' % (clazz, name))
        contexts[name] = clazz
    if not contexts: raise TypeError('Cannot have a processor with no context')

    locals = callerLocals()
    processors = locals.get('processors')
    if processors is None: locals['processors'] = processors = {}

    processors[function.__name__] = (function, contexts)

    return function

class Handler(IHandler):
    '''
    Implementation for a @see: IHandler that provides the preparing based on functions that have been decorated with 
    @see: processor.
    '''

    def prepare(self, calls):
        '''
        @see: IHandler.prepare
        '''
        assert hasattr(self, 'processors'), 'No processors available of handler %s' % self
        assert isinstance(calls, Calls), 'Invalid calls %s' % calls

        for call, contexts in self.processors.values(): calls.add(call, contexts)

# --------------------------------------------------------------------

class AssembleError(Exception):
    '''
    Raised when there is an assemble problem.
    '''

def assemble(handlers, **context):
    '''
    Assemble the handlers with the provided contexts.
    
    @param handlers: Iterable(IHandler)
        The handlers to assemble with the contexts.
    @param context: key arguments of context classes
        The context to assemble for the handlers.
    @return: Processing
        The processing for handling the contexts with the handlers.
    '''
    def callMessage(call):
        if isfunction(call):
            cd = call.__code__
            return '\n  File "%s", line %i, in %s' % (cd.co_filename, cd.co_firstlineno, call.__name__)
        return str(call)

    assert isinstance(handlers, Iterable), 'Invalid handlers %s' % handlers
    if __debug__:
        for key, ctx in context.items():
            assert isclass(ctx), 'Invalid class %s for %s' % (ctx, key)
            assert issubclass(ctx, Context), 'Invalid context class %s for %s' % (ctx, key)

    calls = Calls()
    for handler in handlers:
        assert isinstance(handler, IHandler), 'Invalid handler %s' % handler
        handler.prepare(calls)


    # First we obtain all the attributes of the contexts, while checking for types compatibility we also index the
    # calls based on attribute definers, optional and attribute requires.
    attributeTypes, definers, optionals, requires = {}, {}, {}, {}
    for k, call in enumerate(calls.calls):
        assert isinstance(call, Call), 'Invalid call %s' % call
        for name, contex in call.contexts.items():
            for nameAttribute, attribute in contex.__attributes__.items():
                assert isinstance(attribute, Attribute), 'Invalid attribute %s' % attribute
                key = (name, nameAttribute)
                types = attributeTypes.get(key)
                if types is None: attributeTypes[key] = set(attribute.types)
                else:
                    # Checking the attribute types
                    common = types.intersection(attribute.types)
                    if not common:
                        typNames = [typ.__name__ for typ in types]
                        attrNames = [typ.__name__ for typ in attribute.types]
                        raise AssembleError('The attributes types %s are not compatible with types %s for'
                                            ' attribute \'%s\' of \'%s\' at:%s' %
                                            (typNames, attrNames, nameAttribute, name, callMessage(call.call)))
                    attributeTypes[key] = common

                # Indexing the definers, optional and requires for the attribute
                if attribute.status & DEFINED:
                    attrs = definers.get(k)
                    if attrs is None: attrs = definers[k] = set()
                    attrs.add(key)
                elif attribute.status & OPTIONAL:
                    attrs = optionals.get(k)
                    if attrs is None: attrs = optionals[k] = set()
                    attrs.add(key)
                else:
                    attrs = requires.get(k)
                    if attrs is None: attrs = requires[k] = set()
                    attrs.add(key)

    # Now we sort the calls based on the indexed calls.
    i, ordered = 0, list(range(0, len(calls.calls)))
    while i < len(ordered):
        for j in range(i + 1, len(ordered)):
            call1, call2 = ordered[i], ordered[j]
            definer1, require1 = definers.get(call1), requires.get(call1)
            definer2, require2 = definers.get(call2), requires.get(call2)

            # Check if call2 defines anything for call1
            if definer2 and require1 and not definer2.isdisjoint(require1):
                # The call2 defines stuff for call1 we need to check if doesn't apply reversed
                if definer1 and not definer1.isdisjoint(require2):
                    first = ['%s.%s' % attr for attr in definer2.intersection(require1)]
                    second = ['%s.%s' % attr for attr in definer1.intersection(require2)]
                    raise AssembleError('First call defines attributes %s required by the second call, but also '
                                        'the second call defines attributes %s required by the first call:'
                                        '\nFirst call at:%s\nSecond call at:%s' % (first, second,
                                        callMessage(calls.calls[call1].call)), callMessage(calls.calls[call2].call))

                k, ordered[i] = ordered[i], ordered[j]
                ordered[j] = k
                i -= 1
                break

        i += 1

    print(ordered)
