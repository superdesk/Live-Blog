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
        
        @param contexts: dictionary{string, ContextMetaClass}
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

    @staticmethod
    def contextsFrom(arguments, annotations):
        '''
        Provides the contexts based on the provided list of arguments and annotations.
        '''
        contexts = {}
        for name in arguments:
            clazz = annotations.get(name)
            if clazz is None: raise TypeError('Expected an annotation of class for argument %s' % name)
            if not isclass(clazz): raise TypeError('Not a class %s for argument %s' % (clazz, name))
            if not issubclass(clazz, Context): raise TypeError('Not a context class %s for argument %s' % (clazz, name))
            contexts[name] = clazz
        if not contexts: raise TypeError('Cannot have a function with no context')

        return contexts

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

        super().__init__(self.contextsFrom(fnArgs.args[2:], fnArgs.annotations), function)

class ContextualProceed(Processor):
    '''
    A processor that takes as the call a function and uses the annotations on the function arguments to extract the
    contexts. The function will not receive the chain as an argument and will always proceed.
    '''

    def __init__(self, function):
        '''
        Constructs a processor based on a function.
        @see: Processor.__init__
        
        @param function: function|method
            The function of the processor with the arguments annotated.
        '''
        assert isfunction(function) or ismethod(function), 'Invalid function %s' % function
        fnArgs = getfullargspec(function)

        assert len(fnArgs.args) > 1, 'The processor function needs at least one argument (self)'
        assert 'self' == fnArgs.args[0], \
        'The processor needs to be tagged in a class definition (needs self as the first argument)'

        def call(chain, **keyargs):
            assert isinstance(chain, Chain), 'Invalid processors chain %s' % chain
            function(**keyargs)
            chain.proceed()
        assert isfunction(function) or ismethod(function), 'Invalid function %s' % function
        cd = function.__code__
        super().__init__(Contextual.contextsFrom(fnArgs.args[1:], fnArgs.annotations), call, function.__name__,
                         cd.co_filename, cd.co_firstlineno)

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

class HandlerProcessorProceed(Handler):
    '''
    A handler that contains a processor derived on the contextual 'process' function.
    '''

    def __init__(self):
        '''
        Construct the handler with the processor automatically created from the 'process' function.
        '''
        super().__init__(ContextualProceed(self.process))

    @abc.abstractclassmethod
    def process(self, **keyargs):
        '''
        The contextual process function used by the handler, this process will not require a chain and will always
        proceed with the execution.
        '''

# --------------------------------------------------------------------

NO_INPUT_CONTEXTS_VALIDATION = 1 << 1
# Assembly create flag that dictates that no input contexts missing validation should be performed.
NO_MISSING_VALIDATION = 1 << 2
# Assembly create flag that dictates that no missing validation should be performed.
NO_VALIDATION = NO_INPUT_CONTEXTS_VALIDATION | NO_MISSING_VALIDATION
# Assembly create flag that dictates that no validation should be performed.

ONLY_AVAILABLE = 1 << 3
# Assembly create flag that dictates that only the available processors should be used.
CREATE_REPORT = 1 << 4
# Assembly create flag that dictates that a report should be created, this will modify the return value for the create.

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
        index = self._indexFrom(before, after)
        for processor in self._processorsFrom(processors):
            self._processors.insert(index, processor)
            index += 1

    def move(self, processor, before=None, after=None):
        '''
        Moves in to the assembly the provided processor.
        
        @param processor: Processor|Handler
            The processor to be moved in to the assembly.
        @param before: Processor|Handler
            The processor(s) will be moved before this processor, you can only specify before or after.
        @param after: Processor|Handler
            The processor(s) will be moved after this processor, you can only specify after or before.
        '''
        assert before is not None or after is not None, 'You need to provide an after or a before processor in order to move'
        processor = self._processorFrom(processor)
        try: self._processors.remove(processor)
        except ValueError: raise AttributeError('Unknown processor %s in assembly' % processor)
        index = self._indexFrom(before, after)
        self._processors.insert(index, processor)

    def replace(self, replaced, replacer):
        '''
        Replaces in to the assembly the provided processors.
        
        @param replaced: Processor|Handler
            The processor to be replaced in to the assembly.
        @param replacer: Processor|Handler
            The processor that will replace.
        '''
        try: index = self._processors.index(self._processorFrom(replaced))
        except ValueError: raise AssemblyError('Invalid replaced processor %s' % replaced)
        self._processors[index] = self._processorFrom(replacer)

    def create(self, *flags, **contexts):
        '''
        Create a processing based on all the processors in the assembly.
        
        @param flags: arguments[integer]
            Flags that dictate the behavior of the processing creation.
        @param contexts: key arguments of ContextMetaClass
            Key arguments that have as a value the context classes that the processing chain will be used with.
        @return: Processing|tuple of two
            processing: Processing
            A processing created based on the current structure of the assembly.
            report: string
            A text containing the report for the processing creation
        '''
        flag = 0
        for f in flags:
            assert isinstance(f, int), 'Invalid flag %s' % f
            flag |= f

        processors = self._processors
        assContext = AssemblyContext()

        if flag & (ONLY_AVAILABLE | CREATE_REPORT):
            # Contains the unavailable processors as a tuples having on the first position the list of processors that
            # are not available and on the second the attributes that determined the unavailability.
            processorsAvailable, processorsUnavailable = list(processors), []
            while True:
                assContext.clear().add(processorsAvailable, contexts)

                requiredOnly = assContext.requiredOnly()
                if not requiredOnly: break
                processorsAvailable, excluded = self._filterIfAny(processorsAvailable, requiredOnly)
                if not excluded: break

                processorsUnavailable.append((excluded, requiredOnly))

            if flag & ONLY_AVAILABLE: processors = processorsAvailable

        assContext.clear().addProcessors(processors)
        missing = assContext.required() if flag & NO_INPUT_CONTEXTS_VALIDATION else None
        assContext.addContexts(contexts)

        if not (flag & NO_MISSING_VALIDATION):
            if missing is None: missing = assContext.required()
            missing.difference_update(assContext.defined())
            if missing:
                raise AssemblyError('Cannot resolve any definers for attributes:\n%s' % 
                                    '\n'.join('\t%s.%s' % key for key in missing))

        self._validateOrder(processors)

        if not processors: raise AssemblyError('No processors available to create a processing')

        processing = Processing(assContext.create())
        for processor in processors:
            assert isinstance(processor, Processor), 'Invalid processor %s' % processor
            processor.register(processing)

        if flag & CREATE_REPORT:
            report = []

            if processorsUnavailable:
                entries = []
                for procs, attrs in processorsUnavailable:
                    entry = 'Processors at:%s' % ''.join(location(proc) for proc in procs)
                    entry = '%s\n\t-required attributes: %s' % (entry, ', '.join('%s.%s' % key for key in sorted(attrs)))
                    entries.append(entry)
                report.append('\nThe following processors have been removed because they require attributes that are '
                              'not defined by any other processor:\n%s' % '\n'.join(entries))

            definedOnly = assContext.definedOnly()
            if definedOnly:
                report.append('\nThe following attributes are not used by any processor:\n\t%s' % 
                              ', '.join('%s.%s' % key for key in sorted(definedOnly)))

            if not report: report.append('Nothing to report, everything fits nicely')

            report.insert(0, '-' * 50 + ' Assembly report')
            report.append('-' * 50)
            report.append('')

            return processing, '\n'.join(report)

        return processing

    # ----------------------------------------------------------------

    def _processorFrom(self, processor):
        '''
        Provides an the processor from the provided processor or container.
        
        @param processor: Processor|Handler
            The processor or handler to get the processor for.
        '''
        if isinstance(processor, Processor): return processor

        elif isinstance(processor, Handler):
            assert isinstance(processor, Handler)
            assert isinstance(processor.processor, Processor), \
            'Invalid handler %s processor %s' % (processor, processor.processor)
            return processor.processor

        raise AssemblyError('Invalid processor or handler %s' % processor)

    def _processorsFrom(self, processors):
        '''
        Provides an iterable of the processors obtained from the provided processors or processors containers.
        
        @param processorsOrHandlers: Iterable[Processor|Handler|Assembly|
                                              list[Processor|Handler|Assembly]|tuple(Processor|Handler|Assembly)]
            The processors or processors containers to be made in an iterable of processors.
        '''
        assert isinstance(processors, Iterable), 'Invalid processors %s' % processors

        for processor in processors:
            if isinstance(processor, (list, tuple)):
                for processor in self.processorsFrom(processor): yield processor

            elif isinstance(processor, Assembly):
                assert isinstance(processor, Assembly)
                for processor in  processor._processors: yield processor
            else: yield self._processorFrom(processor)

    def _indexFrom(self, before=None, after=None):
        '''
        Provides the index where to insert based on the provided before and after processors.
        
        @param before: Processor|Handler
            The processor(s) will be moved before this processor, you can only specify before or after.
        @param after: Processor|Handler
            The processor(s) will be moved after this processor, you can only specify after or before.
        @return: integer
            The index where to insert.
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
        return index

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

        definers, _optional, requires = self._indexAttributes(processors)
        assert isinstance(definers, dict), 'Invalid definers %s' % definers
        assert isinstance(requires, dict), 'Invalid requires %s' % requires

        dependencies = []
        for index in range(0, len(processors)):
            beforeProcessor, afterProcessor = set(), set()
            definersProc = definers.get(index, frozenset())
            requiresProc = requires.get(index, frozenset())
            for indexOther in range(0, index):
                definersOther = definers.get(indexOther, frozenset())
                requiresOther = requires.get(indexOther, frozenset())

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
                        location(processors[index]), location(processors[indexOther])))

                elif definesRequired: isSmaller = True

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

    def _filterIfAny(self, processors, requires):
        '''
        Filters the processors by excluding based on the attributes.
        
        @param processors: Iterable(Processor)
            The list of processors to filter.
        @param requires: set(tuple(string, string))
            The attributes that need not to be required by the filtered processors.
            The sets contain tuples having on the first position the context argument name and as the second
            position the attribute name within the context.
        @return: tuple of two
            filtered: list[Processor]
                The list of filtered processors.
            excluded: list[Processor]
                The list of excluded processors.
        '''
        assert isinstance(processors, Iterable), 'Invalid processors %s' % processors
        assert isinstance(requires, set), 'Invalid requires %s' % requires

        filtered, excluded = [], []
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
                        if key in requires:
                            valid = False
                            break
                if not valid: break

            if valid: filtered.append(processor)
            else: excluded.append(processor)

        return filtered, excluded

    def _validateOrder(self, processors):
        '''
        Validates if the order of the processors is correct.
        
        @param processors: list[Processor]
            The list of processors to check for the order.
        '''
        assert isinstance(processors, list), 'Invalid processors %s' % processors

        dependencies = self._indexDependencies(processors)

        before = deque()
        for index in range(0, len(processors)):
            requiredAfter = dependencies[index]
            if requiredAfter:
                broken = requiredAfter.difference(requiredAfter.intersection(before))
                if broken:
                    raise AssemblyError('The processor at:%s\nneeds to have the processors after it, not before '
                                        'it:%s' % (location(processors[index]),
                                                   ''.join(location(processors[bindex]) for bindex in broken)))

            before.append(index)

class AssemblyContext:
    '''
    Contains the data for an attribute assembly.
    '''
    __slots__ = ('attributes',)

    def __init__(self):
        '''
        Construct the attributes assembly.
        '''
        self.attributes = {}

    definedOnly = lambda self: set(key for key, attr in self.attributes.items() if attr.status == DEFINED)
    defined = lambda self: set(key for key, attr in self.attributes.items() if attr.status & DEFINED)
    optionalOnly = lambda self: set(key for key, attr in self.attributes.items() if attr.status == OPTIONAL)
    optional = lambda self: set(key for key, attr in self.attributes.items() if attr.status & OPTIONAL)
    requiredOnly = lambda self: set(key for key, attr in self.attributes.items() if attr.status == REQUIRED)
    required = lambda self: set(key for key, attr in self.attributes.items() if attr.status & REQUIRED)

    def create(self):
        '''
        Creates the contexts based on this assembly.
        '''
        assert self.attributes, 'No attributes available'

        contexts = {}
        for key, assAttr in self.attributes.items():
            assert isinstance(assAttr, AssemblyAttribute)

            name, nameAttribute = key

            attributes = contexts.get(name)
            if attributes is None: attributes = contexts[name] = dict(__module__=__name__)

            try: attributes[nameAttribute] = assAttr.create()
            except AssemblyError:
                raise AssemblyError('Cannot create attribute \'%s\' from context \'%s\'' % (nameAttribute, name))

        return {name: ContextMetaClass('Generated$%s%s' % (name[0].upper(), name[1:]), (Context,), attributes)
                            for name, attributes in contexts.items()}

    # ----------------------------------------------------------------

    def add(self, processors=None, contexts=None):
        '''
        Adds processors or contexts or both to this assembly.
        
        @param processors: Iterable(Processor)|None
            The processors to add.
        @param contexts: dictionary{string, ContextMetaClass}|None
            The contexts to add.
        '''
        if processors is not None: self.addProcessors(processors)
        if contexts is not None: self.addContexts(contexts)

    def addProcessors(self, processors):
        '''
        Add the processors to this attributes assembly.
        
        @param processors: Iterable(Processor)
            The processors to add.
        '''
        assert isinstance(processors, Iterable), 'Invalid processors %s' % processors

        for processor in processors:
            assert isinstance(processor, Processor), 'Invalid processor %s' % processor
            assert isinstance(processor.contexts, dict), 'Invalid processor contexts %s' % processor.contexts

            try: self.addContexts(processor.contexts)
            except AssemblyError:
                raise AssemblyError('Cannot assemble attributes for processor at:%s' % location(processor))

    def addContexts(self, contexts):
        '''
        Add the contexts to this attributes assembly.
        
        @param contexts: dictionary{string, ContextMetaClass}
            The contexts to add.
        '''
        assert isinstance(contexts, dict), 'Invalid contexts %s' % contexts

        for name, context in contexts.items():
            assert isinstance(name, str), 'Invalid context name %s' % name
            assert isinstance(context, ContextMetaClass), 'Invalid context class %s' % context

            for nameAttribute, attribute in context.__attributes__.items():
                assert isinstance(attribute, Attribute), 'Invalid attribute %s' % attribute

                key = (name, nameAttribute)

                assAttr = self.attributes.get(key)
                if not assAttr: assAttr = self.attributes[key] = AssemblyAttribute()

                try: assAttr.add(attribute)
                except AssemblyError:
                    raise AssemblyError('Cannot assemble attribute \'%s\' from context \'%s\'' % (nameAttribute, name))

    def clear(self):
        '''
        Clears the assembly of any attributes and data.
        
        @return: self
            Same instance for chaining purposes.
        '''
        self.attributes.clear()
        return self

class AssemblyAttribute:
    '''
    Contains the data for an attribute assembly.
    '''
    __slots__ = ('status', 'defined', 'required', 'doc')

    def __init__(self):
        '''
        Construct the attribute assembly.
        '''
        self.status = 0
        self.defined = set()
        self.required = set()
        self.doc = None

    def create(self):
        '''
        Creates the attribute based on this assembly.
        '''
        if self.defined and self.required:
            types = self.defined.intersection(self.required)
            if not types:
                raise AssemblyError('Invalid defined %s and required %s assembly types' % 
                                    ([typ.__name__ for typ in self.defined], [typ.__name__ for typ in self.required]))
        elif self.defined: types = self.defined
        elif self.required: types = self.required
        else: raise AssemblyError('Invalid assembly has no types')

        return Attribute(self.status, tuple(types), self.doc)

    # ----------------------------------------------------------------

    def add(self, attribute):
        '''
        Combines this attribute assembly with the provided attribute.
        
        @param attr: Attribute
            The attributes to be combined with.
        '''
        assert isinstance(attribute, Attribute), 'Invalid attribute %s' % attribute

        if attribute.status & DEFINED:
            if not self.defined: self.defined.update(attribute.types)
            else:
                if self.defined.isdisjoint(attribute.types):
                    raise AssemblyError('The defined assembly types %s are not compatible with the defined types %s '
                                        'of attribute %s' % ([typ.__name__ for typ in self.defined],
                                                             [typ.__name__ for typ in attribute.types], attribute))
                self.defined.intersection_update(attribute.types)

        if attribute.status & (REQUIRED | OPTIONAL):
            if not self.required: self.required.update(attribute.types)
            else:
                if self.required.isdisjoint(attribute.types):
                    raise AssemblyError('The required assembly types %s are not compatible with the required types %s '
                                        'of attribute %s' % ([typ.__name__ for typ in self.required],
                                                             [typ.__name__ for typ in attribute.types], attribute))
                    self.required.intersection_update(attribute.types)

        if self.required and self.defined and self.required != self.defined and self.defined.issuperset(self.required):
                raise AssemblyError('The defined attributes types %s are not compatible with the required types %s' % 
                ([typ.__name__ for typ in self.defined], [typ.__name__ for typ in self.required]))

        self.status |= attribute.status

        docs = []
        if self.doc is not None: docs.append(self.doc)
        if attribute.doc is not None: docs.append(attribute.doc)

        if docs: self.doc = '\n'.join(docs)

# --------------------------------------------------------------------

def location(processor):
    '''
    Provides a processor location message used for exceptions.
    
    @param index: integer
        The processor index to have the location message.
    @return: string
        The location message.
    '''
    assert isinstance(processor, Processor), 'Invalid processor %s' % processor

    return '\n  File "%s", line %i, in %s' % (processor.fileName, processor.lineNumber, processor.name)
