'''
Created on Jun 11, 2012

@package: utilities
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Module containing the support for a chained processors execution of context type objects.
'''

from ally.design.context import Context, Attribute, DEFINED, OPTIONAL, \
    ContextMetaClass, REQUIRED
from collections import Iterable, deque
from inspect import isclass, isfunction, getfullargspec, ismethod
import abc
import logging

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

class Processor:
    '''
    The processor specification.
    '''
    __slots__ = ('contexts', 'call', 'name', 'fileName', 'lineNumber')

    def __init__(self, contexts, call, name='', fileName='', lineNumber=0):
        '''
        Construct the processor for the provided context having the provided call. The name, fileName and lineNumber
        are used mainly as a reference whenever reporting a problem related to the processor.
        
        @param contexts: dictionary{string, Context class}
            The contexts to be associated with the processor.
        @param call: callable
            The call of the processor.
        @param name: string
            The call function name, used for error reporting references.
        @param fileName: string
            The file name where the function is located, used for error reporting references.
        @param lineNumber: integer
            The line number where the function is located, used for error reporting references.
        '''
        assert isinstance(contexts, dict), 'Invalid contexts %s' % contexts
        assert callable(call), 'Invalid call %s' % call
        assert isinstance(name, str), 'Invalid call name %s' % name
        assert isinstance(fileName, str), 'Invalid file name %s' % fileName
        assert isinstance(lineNumber, int), 'Invalid line number %s' % lineNumber
        if __debug__:
            for key, clazz in contexts.items():
                assert isinstance(key, str), 'Invalid context name %s' % key
                assert isinstance(clazz, ContextMetaClass), 'Invalid context class %s for %s' % (clazz, key)

        self.contexts = contexts
        self.call = call
        self.name = name
        self.fileName = fileName
        self.lineNumber = lineNumber

    def register(self, processing):
        '''
        Register the processor call into the provided processing. The order in which the register functions are called
        is provided by an assembler, so usually the call should be only appended to the processors deque in the
        processing.
        
        @param processing: Processing
            The processing to register to.
        '''
        assert isinstance(processing, Processing), 'Invalid processing %s' % processing
        processing.calls.append(self.call)

    def __eq__(self, other):
        if not isinstance(other, self.__class__): return False
        return self.contexts == other.contexts and self.call == other.call

class Function(Processor):
    '''
    A processor that takes as the call a function and automatically populates name, fileName and lineNumber.
    '''
    __slots__ = ()

    def __init__(self, contexts, function):
        '''
        Constructs a processor based on a function.
        @see: Processor.__init__
        
        @param function: function|method
            The function of the processor.
        '''
        assert isfunction(function) or ismethod(function), 'Invalid function %s' % function
        cd = function.__code__
        super().__init__(contexts, function, function.__name__, cd.co_filename, cd.co_firstlineno)

class Contextual(Function):
    '''
    A processor that takes as the call a function and uses the annotations on the function arguments to extract the
    contexts.
    '''
    __slots__ = ()

    def __init__(self, function):
        '''
        Constructs a processor based on a function.
        @see: Function.__init__
        
        @param function: function|method
            The function of the processor with the arguments annotated.
        '''
        assert isfunction(function) or ismethod(function), 'Invalid function %s' % function
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
        if not contexts: raise TypeError('Cannot have a function with no context')

        super().__init__(contexts, function)

# --------------------------------------------------------------------

class Processing:
    '''
    Container for processor's, provides chains for their execution.
    !!! Attention, never ever use a processing in multiple threads, only one thread is allowed to execute 
    a processing at one time.
    '''
    __slots__ = ('contexts', 'calls')

    def __init__(self, contexts):
        '''
        Construct the processing.
        
        @param contexts: dictionary{string, Context class}
            The contexts to be associated with the processing.
        '''
        assert isinstance(contexts, dict), 'Invalid contexts %s' % contexts
        if __debug__:
            for key, clazz in contexts.items():
                assert isinstance(key, str), 'Invalid context name %s' % key
                assert isinstance(clazz, ContextMetaClass), 'Invalid context class %s for %s' % (clazz, key)

        self.contexts = contexts
        self.calls = deque()

    def newChain(self):
        '''
        Constructs a new processors chain.
        
        @return: Chain
            The chain of processors.
        '''
        return Chain(self.calls)

class Chain:
    '''
    A chain that contains a list of processors (callables) that are executed one by one. Each processor will have
     the duty to proceed with the processing if is the case by calling the chain.
    '''
    __slots__ = ('_calls', '_consumed', '_proceed')

    def __init__(self, calls):
        '''
        Initializes the chain with the processors to be executed.
        
        @param calls: Iterable(callable)
            The iterable of callables to be executed. Attention the order in which the processors are provided
            is critical since one processor is responsible for delegating to the next.
        '''
        assert isinstance(calls, Iterable), 'Invalid processors %s' % calls
        self._calls = deque(calls)
        if __debug__:
            for proc in self._calls: assert callable(proc), 'Invalid processor %s' % proc
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
                call = self._calls.popleft()
                assert log.debug('Processing %s', call) or True
                call(self, **keyargs)
                assert log.debug('Processing finalized %r', call) or True

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

class Handler(metaclass=abc.ABCMeta):
    '''
    Handler base that provides a container for a processor.
    '''

    def __init__(self, processor):
        '''
        Construct the handler.
        
        @param processor: Processor
            The processor for the container.
        '''
        self.processor = processor

class HandlerProcessor(Handler):
    '''
    A handler that contains a processor derived on the contextual 'process' function.
    '''

    def __init__(self):
        '''
        Construct the handler with the processor automatically created from the 'process' function.
        '''
        super().__init__(Contextual(self.process))

    @abc.abstractclassmethod
    def process(self, chain, **keyargs):
        '''
        The contextual process function used by the handler.
        
        @param chain: Chain
            The processing chain.
        '''

# --------------------------------------------------------------------

EMPTY_SET = set()
# Empty set used when there is nothing to place

class AssemblyError(Exception):
    '''
    Raised when there is a assembly problem.
    '''

class Assembly:
    '''
    The assembly provides a container for the processors.
    '''

    def __init__(self):
        '''
        Construct the assembly.
        '''
        self._processors = []

    def add(self, *processors, before=None, after=None):
        '''
        Add to the assembly the provided processors.
        
        @param processors: arguments[Processor|Handler|list[Processor|Handler]|tuple(Processor|Handler)]
            The processor(s) to be added to the assembly.
        @param before: Processor|Handler
            The processor(s) will be ordered before this processor, you can only specify before or after.
        @param after: Processor|Handler
            The processor(s) will be ordered after this processor, you can only specify after or before.
        '''
        index = len(self._processors)
        if before is not None:
            before = self._processorFrom(before)
            assert after is None, 'Cannot have before and after at the same time'

            try: index = self._processors.index(before)
            except ValueError: raise AttributeError('Unknown before processor %s in assembly' % before)

        elif after is not None:
            after = self._processorFrom(after)

            try: index = self._processors.index(after) + 1
            except ValueError: raise AttributeError('Unknown after processor %s in assembly' % after)

        for processor in self._processorsFrom(processors):
            self._processors.insert(index, processor)
            index += 1

    def create(self, **contexts):
        '''
        Create a processing based on all the processors in the assembly.
        
        @param contexts: key arguments of context class
            Key arguments that have as a value the context classes that the processing chain will be used with.
        @return: Processing
            A processing created based on the current structure of the assembly.
        '''
        defines, requires = self._indexTypes(self._processors)
        self._indexContexts(contexts, defines, requires)
        missing = set(requires)
        missing.difference_update(defines)

        if missing:
            raise AssemblyError('Cannot resolve any definers for attributes:\n%s' %
                                '\n'.join('\t%s.%s' % key for key in missing))

        return



        dependencies = self._indexDependencies(self._processors)

        before = deque()
        for index in range(0, len(self._processors)):
            requiredAfter = dependencies[index]
            if requiredAfter:
                broken = requiredAfter.difference(requiredAfter.intersection(before))
                if broken:
                    raise AssemblyError('The processor at:%s\nneeds to have the processors after it, not before '
                                        'it:%s' % (self._location(index),
                                                   ''.join(self._location(bindex) for bindex in broken)))

            before.append(index)

#        return
        #TODO: remove
        print('------------------------------------------------------------')
        print(''.join([self._location(index) for index in range(0, len(self._processors))]))

    def createWithAvailable(self, **contexts):
        '''
        Create a processing based on the processors in the assembly that are available. A processor is available
        if it has all the requirements of the contexts satisfied.
        
        @param contexts: key arguments of context class
            Key arguments that have as a value the context classes that the processing chain will be used with.
        @return: Processing
            A processing created based on the current structure of the assembly.
        '''
        processors = self._processors

        # First we filter for all processors that are available
        while True:
            defines, requires = self._indexTypes(processors)
            self._indexContexts(contexts, defines, requires)
            defined = set(requires)
            defined.intersection_update(defines)

            notDefined = set(requires)
            notDefined.difference_update(defined)

            filtered = self._filterByAttributes(processors, excludeIfRequires=notDefined)
            if len(filtered) == len(processors): break
            processors = filtered

        processors = filtered

        # We remove all processors that provide data that is not used
        de continuat cu filtratul procesoarelor care fac define la valori fara nimic
        si de asemenea si la creatul normal ar trebui validat the procesoare care nu fac nimic
        si de validat requires pentru contextele date ca parametri.

        #TODO: remove
        print('------------------------------------------------------------')
        print(defined)
        print('------------------------------------------------------------')
        print(''.join([self._location(proc) for proc in processors]))


    # ----------------------------------------------------------------

    def _processorFrom(self, processorOrHandler):
        '''
        Provides an the processor from the provided processor or container.
        
        @param processorOrHandler: Processor|Handler
            The processor or handler to get the processor for.
        '''
        if isinstance(processorOrHandler, Processor):
            return processorOrHandler

        elif isinstance(processorOrHandler, Handler):
            assert isinstance(processorOrHandler, Handler)
            assert isinstance(processorOrHandler.processor, Processor), \
            'Invalid handler %s processor %s' % (processorOrHandler, processorOrHandler.processor)
            return processorOrHandler.processor

        raise AssemblyError('Invalid processor  or handler %s' % processorOrHandler)

    def _processorsFrom(self, processorsOrHandlers):
        '''
        Provides an iterable of the processors obtained from the provided processors or processors containers.
        
        @param processorsOrHandlers: arguments[Processor|Handler|list[Processor|Handler]|tuple(Processor|Handler)]
            The processors or processors containers to be made in an iterable of processors.
        '''
        assert isinstance(processorsOrHandlers, Iterable), 'Invalid processors %s' % processorsOrHandlers

        for processorOrHandler in processorsOrHandlers:
            if isinstance(processorOrHandler, (list, tuple)):
                for processor in self.processorsFrom(processorOrHandler):
                    yield processor

            else:
                yield self._processorFrom(processorOrHandler)

    def _location(self, processor):
        '''
        Provides a processor location message used for exceptions.
        
        @param index: integer
            The processor index to have the location message.
        @return: string
            The location message.
        '''
        assert isinstance(processor, Processor), 'Invalid processor %s' % processor

        return '\n  File "%s", line %i, in %s' % (processor.fileName, processor.lineNumber, processor.name)

    # ----------------------------------------------------------------

    def _indexContexts(self, contexts, defines, requires):
        '''
        Indexes the provided contexts into the provided defines and requires dictionaries.
        
        @param defines: dictionary{tuple(string, string):set(class)}
        @param requires: dictionary{tuple(string, string):set(class)}
            The keys of the dictionaries are tuple having on the first position the context argument name and as the
            second position the attribute name within the context.
        '''
        assert isinstance(contexts, dict), 'Invalid contexts %s' % contexts
        assert isinstance(defines, dict), 'Invalid defines %s' % defines
        assert isinstance(requires, dict), 'Invalid requires %s' % requires

        for name, context in contexts.items():
            assert isinstance(context, ContextMetaClass), 'Invalid context class %s' % context

            for nameAttribute, attribute in context.__attributes__.items():
                assert isinstance(attribute, Attribute), 'Invalid attribute %s' % attribute

                key = (name, nameAttribute)

                checkRequiredvsDefined = False
                if attribute.status & REQUIRED:
                    typesRequired = requires.get(key)
                    if typesRequired is None: requires[key] = set(attribute.types)
                    else:
                        common = typesRequired.intersection(attribute.types)
                        if not common:
                            raise AssemblyError('The required attributes types %s are not compatible with the '
                            'context \'%s\' attribute \'%s\' required types %s' %
                            ([typ.__name__ for typ in typesRequired], name, nameAttribute,
                             [typ.__name__ for typ in attribute.types]))

                        requires[key] = common
                        checkRequiredvsDefined = True

                elif attribute.status & DEFINED:
                    typesDefined = defines.get(key)
                    if typesDefined is None: defines[key] = set(attribute.types)
                    else: typesDefined.update(attribute.types)

                    checkRequiredvsDefined = True

                if checkRequiredvsDefined:
                    typesRequired = requires.get(key)
                    if typesRequired: typesDefined = defines.get(key)
                    if typesRequired and typesDefined and typesRequired != typesDefined and \
                    typesDefined.issuperset(typesRequired):
                        raise AssemblyError('The defined attributes types %s are not compatible with the context'
                        ' \'%s\' attribute \'%s\' required types %s' %
                        ([typ.__name__ for typ in typesDefined], name, nameAttribute,
                         [typ.__name__ for typ in typesRequired]))

    def _indexTypes(self, processors):
        '''
        Indexes and combines the types for the provided processors.
        
        @param processors: Iterable(Processor)
            The list of processors to index the attributes types for.
        @return: tuple of two
            defines: dictionary{tuple(string, string):set(class)}
            requires: dictionary{tuple(string, string):set(class)}
            
            The keys of the dictionaries are tuple having on the first position the context argument name and as the
            second position the attribute name within the context.
        '''
        assert isinstance(processors, Iterable), 'Invalid processors %s' % processors

        defines, requires = {}, {}
        for processor in processors:
            assert isinstance(processor, Processor), 'Invalid processor %s' % processor
            assert isinstance(processor.contexts, dict), 'Invalid processor contexts %s' % processor.contexts

            try: self._indexContexts(processor.contexts, defines, requires)
            except AssemblyError as e:
                raise AssemblyError('Problems with processor at:%s\n%s' % (self._location(processor), e))

        return defines, requires

    def _indexAttributes(self, processors):
        '''
        Indexes the attributes dependencies for the provided processors.
        
        @param processors: Iterable(Processor)
            The list of processors to index the attributes for.
        @return: tuple of three
            definers: dictionary{integer, set(tuple(string, string))}
            optional: dictionary{integer, set(tuple(string, string))}
            requires: dictionary{integer, set(tuple(string, string))}
            
            The keys of the dictionaries are the index in the contained processors list of the processor that they
            represent. The values of the dictionaries are sets having tuples with the first position as the context 
            argument name and as the second position the attribute name within the context.
        '''
        assert isinstance(processors, Iterable), 'Invalid processors %s' % processors

        definers, optional, requires = {}, {}, {}
        for index, processor in enumerate(processors):
            assert isinstance(processor, Processor), 'Invalid processor %s' % processor
            assert isinstance(processor.contexts, dict), 'Invalid processor contexts %s' % processor.contexts

            for name, context in processor.contexts.items():
                assert isinstance(context, ContextMetaClass), 'Invalid context class %s' % context

                for nameAttribute, attribute in context.__attributes__.items():
                    assert isinstance(attribute, Attribute), 'Invalid attribute %s' % attribute

                    key = (name, nameAttribute)

                    # Indexing the definers, optional and requires for the attribute
                    if attribute.status & DEFINED:
                        attrs = definers.get(index)
                        if attrs is None: attrs = definers[index] = set()
                        attrs.add(key)
                    elif attribute.status & OPTIONAL:
                        attrs = optional.get(index)
                        if attrs is None: attrs = optional[index] = set()
                        attrs.add(key)
                    else:
                        attrs = requires.get(index)
                        if attrs is None: attrs = requires[index] = set()
                        attrs.add(key)

        return definers, optional, requires

    def _indexDependencies(self, processors):
        '''
        Indexes the dependencies of the processors of this assembly.
        
        @param processors: Iterable(Processor)
            The list of processors to index the dependencies for.
        @param dependencies: list[set(integer)]
            A list containing the dependencies for the processor, the list index is the index in the list of the
            processors list of the corresponding processor, the value is a set of integers representing the processors
            that are required to be before the indexed processor.
        '''
        assert isinstance(processors, Iterable), 'Invalid processors %s' % processors

        definers, optional, requires = self._indexAttributes(processors)
        assert isinstance(definers, dict), 'Invalid definers %s' % definers
        assert isinstance(optional, dict), 'Invalid optional %s' % optional
        assert isinstance(requires, dict), 'Invalid requires %s' % requires

        dependencies = []
        for index in range(0, len(processors)):
            beforeProcessor, afterProcessor = set(), set()
            definersProc = definers.get(index, EMPTY_SET)
            optionalProc = optional.get(index, EMPTY_SET)
            requiresProc = requires.get(index, EMPTY_SET)
            for indexOther in range(0, index):
                definersOther = definers.get(indexOther, EMPTY_SET)
                optionalOther = optional.get(indexOther, EMPTY_SET)
                requiresOther = requires.get(indexOther, EMPTY_SET)

                definesRequired = definersProc.intersection(requiresOther)
                otherDefinesRequired = definersOther.intersection(requiresProc)

                isSmaller, isOtherSmaller = False, False
                if otherDefinesRequired:
                    # Check if index defines anything for other index
                    isOtherSmaller = True
                    if definesRequired:
                        # The other index defines stuff for index we need to check if doesn't apply reversed
                        raise AssemblyError('First processor defines attributes %s required by the second processor'
                        ', but also the second processor defines attributes %s required by the first processor:'
                        '\nFirst processor at:%s\nSecond processor at:%s' %
                        (['%s.%s' % attr for attr in definesRequired], ['%s.%s' % attr for attr in otherDefinesRequired],
                        self._location(processors[index]), self._location(processors[indexOther])))

                elif definesRequired: isSmaller = True

                else:
                    # We check if there are some optional to be handled
                    definesOptional = definersProc.intersection(optionalOther)
                    if definesOptional: isSmaller = True
                    else:
                        otherDefinesOptional = definersOther.intersection(optionalProc)
                        if otherDefinesOptional and not definesRequired: isOtherSmaller = True

                if isOtherSmaller:
                    beforeProcessor.add(indexOther)
                if isSmaller:
                    afterProcessor.add(indexOther)
                    dependencies[indexOther].add(index)

            if beforeProcessor:
                for aindex in afterProcessor:
                    dependencies[aindex].update(beforeProcessor)

            dependencies.append(beforeProcessor)

        return dependencies

    # ----------------------------------------------------------------

    def _filterByAttributes(self, processors, excludeIfDefines=EMPTY_SET, excludeIfRequires=EMPTY_SET):
        '''
        Filters the list of processors based on the attributes.
        
        @param processors: Iterable(Processor)
            The list of processors to filter.
        @param excludeIfDefines: set(tuple(string, string))|None
            The attributes that need not to be defined by the filtered processors, if None will not filter by.
        @param excludeIfRequires: set(tuple(string, string))|None
            The attributes that need not to be required by the filtered processors, if None will not filter by.
            
            The sets contain tuples having on the first position the context argument name and as the second
            position the attribute name within the context.
        @return: list[Processor]
            The list of filtered processors.
        '''
        assert isinstance(processors, Iterable), 'Invalid processors %s' % processors
        assert isinstance(excludeIfDefines, set), 'Invalid exclude if defines %s' % excludeIfDefines
        assert isinstance(excludeIfRequires, set), 'Invalid exclude if  requires %s' % excludeIfRequires

        filtered = []
        for processor in processors:
            assert isinstance(processor, Processor), 'Invalid processor %s' % processor
            assert isinstance(processor.contexts, dict), 'Invalid processor contexts %s' % processor.contexts

            valid = True
            for name, context in processor.contexts.items():
                assert isinstance(context, ContextMetaClass), 'Invalid context class %s' % context

                for nameAttribute, attribute in context.__attributes__.items():
                    assert isinstance(attribute, Attribute), 'Invalid attribute %s' % attribute

                    key = (name, nameAttribute)

                    if attribute.status & REQUIRED:
                        if key in excludeIfRequires:
                            valid = False
                            break
                    elif attribute.status & DEFINED:
                        if key in excludeIfDefines:
                            valid = False
                            break
                if not valid: break

            if valid: filtered.append(processor)

        return filtered
