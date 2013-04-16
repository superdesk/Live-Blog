'''
Created on Feb 11, 2013

@package: ally base
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Module containing processors.
'''

from .assembly import Assembly, Container
from .context import create, createDefinition
from .execution import Chain, Processing
from .spec import AssemblyError, IProcessor, ContextMetaClass, ProcessorError, \
    Resolvers, IReport, ResolverError
from ally.support.util_sys import locationStack
from collections import Iterable
from inspect import ismethod, isfunction, getfullargspec
from itertools import chain
import abc

# --------------------------------------------------------------------

class Processor(IProcessor):
    '''
    Implementation for @see: IProcessor that takes as the call a function and uses the annotations on the function arguments 
    to extract the contexts.
    '''
    __slots__ = ('contexts', 'call')
    
    def __init__(self, contexts, call):
        '''
        Construct the processor for the provided context having the provided call.
        
        @param contexts: dictionary{string, ContextMetaClass}
            The contexts to be associated with the processor.
        @param call: callable
            The call of the processor.
        '''
        assert isinstance(contexts, dict), 'Invalid contexts %s' % contexts
        assert callable(call), 'Invalid call %s' % call
        if __debug__:
            for key, clazz in contexts.items():
                assert isinstance(key, str), 'Invalid context name %s' % key
                assert isinstance(clazz, ContextMetaClass), 'Invalid context class %s for %s' % (clazz, key)

        self.contexts = contexts
        self.call = call

    def register(self, sources, resolvers, extensions, calls, report):
        '''
        @see: IProcessor.register
        '''
        assert isinstance(resolvers, Resolvers), 'Invalid resolvers %s' % resolvers
        assert isinstance(calls, list), 'Invalid calls %s' % calls
        resolvers.merge(self.contexts)
        calls.append(self.call)
        
    # ----------------------------------------------------------------
    
    def clone(self):
        '''
        Clones the processor.
        '''
        return Processor(dict(self.contexts), self.call)

    def __eq__(self, other):
        if not isinstance(other, self.__class__): return False
        return self.contexts == other.contexts and self.call == other.call

class Contextual(Processor):
    '''
    Implementation for @see: IProcessor that takes as the call a function and uses the annotations on the function arguments 
    to extract the contexts.
    '''
    __slots__ = ('proceed', 'function')

    def __init__(self, function, proceed=False):
        '''
        Constructs a processor based on a function.
        @see: Processor.__init__
        
        @param function: function|method
            The function of the processor with the arguments annotated.
        @param proceed: boolean
            Flag indicating that the processor should auto proceed for the executed chain.
            Attention if this flag is provided then the function should not have a 'chain' argument.
        '''
        assert isinstance(proceed, bool), 'Invalid proceed flag %s' % proceed
        assert isfunction(function) or ismethod(function), 'Invalid function %s' % function
        
        self.proceed = proceed
        self.function = function
        
        fnArgs = getfullargspec(function)
        arguments, annotations = self.processArguments(fnArgs.args, fnArgs.annotations)
        
        assert isinstance(arguments, Iterable), 'Invalid arguments %s' % arguments
        assert isinstance(annotations, dict), 'Invalid annotations %s' % annotations
        contexts = {}
        for name in arguments:
            assert isinstance(name, str), 'Invalid argument name %s' % name
            clazz = annotations.get(name)
            if clazz is None: continue
            if not isinstance(clazz, ContextMetaClass):
                raise ProcessorError('Not a context class %s for argument %s, at:%s' % 
                                     (clazz, name, locationStack(self.function)))
            contexts[name] = clazz
        if not contexts: raise ProcessorError('Cannot have a function with no context, at:%s' % 
                                              locationStack(self.function))
        
        super().__init__(contexts, self.processCall(function))
    
    def register(self, sources, resolvers, extensions, calls, report):
        '''
        @see: IProcessor.register
        '''
        assert isinstance(resolvers, Resolvers), 'Invalid resolvers %s' % resolvers
        assert isinstance(calls, list), 'Invalid calls %s' % calls
        
        try: resolvers.merge(self.contexts)
        except ResolverError: raise AssemblyError('Cannot merge contexts at:%s' % locationStack(self.function))
        calls.append(self.call)
        
    # ----------------------------------------------------------------
    
    def clone(self):
        '''
        @see: Processor.clone
        '''
        return Contextual(self.function, self.proceed)
     
    def processArguments(self, arguments, annotations):
        '''
        Process the context arguments as seen fit.
        
        @param arguments: list[string]|tuple(string)
            The arguments to process.
        @param annotations: dictionary{string, object}
            The annotations to process.
        @return: tuple(list[string], dictionary{string, object})
            A tuple containing the list of processed arguments names and second value the dictionary containing the 
            annotation for arguments.
        '''
        assert isinstance(arguments, (list, tuple)), 'Invalid arguments %s' % arguments
        assert isinstance(annotations, dict), 'Invalid annotations %s' % annotations
        if self.proceed:
            if len(arguments) > 1 and 'self' == arguments[0]: return arguments[1:], annotations
            raise ProcessorError('Required function of form \'def processor(self, contex:Context ...)\' for:%s' % 
                                 locationStack(self.function))

        if len(arguments) > 2 and 'self' == arguments[0]: return arguments[2:], annotations
        raise ProcessorError('Required function of form \'def processor(self, chain, contex:Context ...)\' for:%s' % 
                             locationStack(self.function))
    
    def processCall(self, call):
        '''
        Process the call of the process if is the case.
        
        @param call: callable
            The call to wrap.
        @return: callable
            The wrapped call.
        '''
        if self.proceed:
            def wrapper(chain, **keyargs):
                assert isinstance(chain, Chain), 'Invalid processors chain %s' % chain
                call(**keyargs)
                chain.proceed()
            return wrapper
        return call
    
    # ----------------------------------------------------------------
    
    def __str__(self):
        ctxs = '\n'.join(('%s=%s' % item for item in self.contexts.items()))
        if ismethod(self.function):
            return '%s with:\n%s\n, defined at:%s\n, in instance %s' % \
                (self.__class__.__name__, ctxs, locationStack(self.function), self.function.__self__)
        return '%s with:\n%s\n, defined at:%s' % (self.__class__.__name__, ctxs, locationStack(self.function))

# --------------------------------------------------------------------

class IBranch(metaclass=abc.ABCMeta):
    '''
    Specification for a branch handler.
    '''
    __slots__ = ()
    
    @abc.abstractmethod
    def process(self, processor, sources, resolvers, extensions, report):
        '''
        Process the branch for the current contexts and attributes.
        
        @param sources: Resolvers
            The sources attributes resolvers that need to be solved by processors.
        @param resolvers: Resolvers
            The attributes resolvers solved so far by processors.
        @param extensions: Resolvers
            The resolvers that are not part of the main stream attributes resolvers but they are rather extension for the created
            contexts.
        @param report: IReport
            The report to be used in the registration process.
        @return: IProcessing
            The branch processing.
        ''' 

class Brancher(Contextual):
    '''
    Implementation for @see: IProcessor that provides branching of other processors containers.
    '''
    __slots__ = ('branches', 'processings')
    
    def __init__(self, function, *branches, proceed=False):
        '''
        Construct the branching processor.
        @see: Contextual.__init__
        
        @param branches: arguments[IBranch]
            The branches to use in branching.
        '''
        assert branches, 'At least one branch is required'
        if __debug__:
            for branch in branches: assert isinstance(branch, IBranch), 'Invalid branch %s' % branch
        self.branches = branches
        super().__init__(function, proceed)
    
    def register(self, sources, resolvers, extensions, calls, report):
        '''
        @see: IProcessor.register
        '''
        assert isinstance(calls, list), 'Invalid calls %s' % calls
        
        self.processings = []
        for branch in self.branches:
            assert isinstance(branch, IBranch), 'Invalid branch %s' % branch
            try: processing = branch.process(self, sources, resolvers, extensions, report)
            except ResolverError: raise AssemblyError('Cannot create processing at:%s' % locationStack(self.function))
            assert isinstance(processing, Processing), 'Invalid processing %s' % processing
            self.processings.append(processing)
        calls.append(self.call)
        
    # ----------------------------------------------------------------
    
    def clone(self):
        '''
        @see: Processor.clone
        '''
        return Brancher(self.function, *self.branches, proceed=self.proceed)
        
    def processArguments(self, arguments, annotations):
        '''
        @see: Contextual.processArguments
        '''
        arguments, annotations = super().processArguments(arguments, annotations)
        
        n = len(self.branches)
        if len(arguments) > n: return arguments[n:], annotations
        raise ProcessorError('Required function of form \'def processor(self, [chain], '
                             'processing, ..., contex:Context ...)\' for:%s' % locationStack(self.function))
    
    def processCall(self, call):
        '''
        @see: Contextual.processCall
        '''
        def wrapper(*args, **keyargs):
            call(*chain(args, self.processings), **keyargs)
        return super().processCall(wrapper)

# --------------------------------------------------------------------

class Routing(IBranch):
    '''
    Branch for routed processors containers. By routing is understood that the processors will be executed separately
    from the main chain and they need to solve the main contexts. 
    '''
    __slots__ = ('assembly', 'merged')
    
    def __init__(self, assembly, merged=True):
        '''
        Construct the routing branch.
        
        @param assembly: Assembly
            The processors assembly that provides routing.
        @param merged: boolean
            Flag indicating that the routing should be merged with the main context, thus allowing the routing processor
            to use the same objects.
            Attention if this is true then no processing context will be available.
        '''
        assert isinstance(assembly, Assembly), 'Invalid assembly %s' % assembly
        assert isinstance(merged, bool), 'Invalid merged flag %s' % merged
        self.assembly = assembly
        self.merged = merged
        
    def process(self, processor, sources, resolvers, extensions, report):
        '''
        @see: IBrach.process
        '''
        assert isinstance(processor, Processor), 'Invalid processor %s' % processor
        assert isinstance(sources, Resolvers), 'Invalid sources %s' % sources
        assert isinstance(resolvers, Resolvers), 'Invalid resolvers %s' % resolvers
        assert isinstance(report, IReport), 'Invalid report %s' % report
        
        report = report.open('Routing \'%s\'' % self.assembly.name)
        try:
            calls, rresolvs, rextens = [], Resolvers(), Resolvers()
            for rproc in self.assembly.processors:
                assert isinstance(rproc, IProcessor), 'Invalid processor %s' % rproc
                rproc.register(sources, rresolvs, rextens, calls, report)
        except (ResolverError, AssemblyError): raise AssemblyError('Cannot process Routing for %s' % self.assembly.name)
        
        try:
            rresolvs.solve(processor.contexts)
            resolvers.merge(rresolvs.copy(sources.iterateNames()))
            rresolvs.solve(sources)
            rresolvs.validate()
            rresolvs.solve(rextens)
            
            if self.merged:
                assert isinstance(extensions, Resolvers), 'Invalid extensions %s' % extensions
                extensions.merge(rresolvs)
                return Processing(calls)
            
            report.add(rresolvs)
            return Processing(calls, create(rresolvs))
        except ResolverError:
            raise AssemblyError('Resolvers problems on Routing for %s\n, with processors %s\n'
                                ', and extensions %s' % (self.assembly.name, rresolvs, rextens))
 
class Using(IBranch):
    '''
    Branch for using processors containers. By using is understood that the processors will be executed separately
    from the main chain and they need to solve the provided contexts. 
    '''
    __slots__ = ('assembly', 'contexts', 'useSources')

    def __init__(self, assembly, **contexts):
        '''
        Construct the using branch.
        
        @param assembly: Assembly
            The processors assembly to use.
        @param contexts: key arguments{string, ContextMetaClass}
            The contexts to be solved by the used container.
        '''
        assert isinstance(assembly, Assembly), 'Invalid assembly %s' % assembly
        if __debug__:
            for name, clazz in contexts.items():
                assert isinstance(name, str), 'Invalid context name %s' % name
                assert isinstance(clazz, ContextMetaClass), 'Invalid context class %s' % clazz
        self.assembly = assembly
        self.contexts = contexts
        self.useSources = set()
    
    def process(self, processor, sources, resolvers, extensions, report):
        '''
        @see: IBrach.process
        '''
        assert isinstance(processor, Processor), 'Invalid processor %s' % processor
        assert isinstance(sources, Resolvers), 'Invalid sources %s' % sources
        assert isinstance(resolvers, Resolvers), 'Invalid resolvers %s' % resolvers
        assert isinstance(report, IReport), 'Invalid report %s' % report
        
        resolvers.merge(processor.contexts)
        report = report.open('Using \'%s\'' % self.assembly.name)
        
        try:
            if self.useSources:
                usrcs = sources.copy(self.useSources)
                if self.contexts: usrcs.merge(self.contexts)
                usrcs.lock()
            else:
                usrcs = Resolvers(True, self.contexts)
            
            calls, uresolvs, uextens = [], Resolvers(), Resolvers()
            for uproc in self.assembly.processors:
                assert isinstance(uproc, IProcessor), 'Invalid processor %s' % uproc
                uproc.register(usrcs, uresolvs, uextens, calls, report)
        except (ResolverError, AssemblyError): raise AssemblyError('Cannot process Using for %s' % self.assembly.name)
        
        try:
            uresolvs.solve(usrcs)
            uresolvs.validate()
            uresolvs.solve(uextens)
            report.add(uresolvs)
            return Processing(calls, create(uresolvs))
        except ResolverError:
            raise AssemblyError('Resolvers problems on Using for %s\n, with sources %s\n, with processors %s\n'
                                ', and extensions %s' % (self.assembly.name, usrcs, uresolvs, uextens))
            
    # ----------------------------------------------------------------
    
    def sources(self, *names):
        '''
        Declare the source names that are used as contexts.
        
        @param names: arguments[string]
            The contexts names to be used from the sources.
        @return: self
            This instance for chaining purposes.
        '''
        if __debug__:
            for name in names: assert isinstance(name, str), 'Invalid context name %s' % name
        self.useSources.update(names)
        return self

class Included(IBranch):
    '''
    Branch for included processors containers. By included is understood that the processors will be executed using the
    main context objects, so basically is like having included also the processors in the main chain but still have control
    over when and how they are executed.
    '''
    __slots__ = ('assembly', 'contextsUsing')
    
    def __init__(self, assembly):
        '''
        Construct the included branch.
        
        @param assembly: Container
            The processors assembly to be included.
        '''
        assert isinstance(assembly, Assembly), 'Invalid assembly %s' % assembly
        self.assembly = assembly
        self.contextsUsing = {}
    
    def process(self, processor, sources, resolvers, extensions, report):
        '''
        @see: IBrach.process
        '''
        assert isinstance(processor, Processor), 'Invalid processor %s' % processor
        assert isinstance(resolvers, Resolvers), 'Invalid resolvers %s' % resolvers
        assert isinstance(extensions, Resolvers), 'Invalid extensions %s' % extensions
        assert isinstance(report, IReport), 'Invalid report %s' % report
        
        report = report.open('Included \'%s\'' % self.assembly.name)
        
        try:
            calls, iresolvs, iextens = [], Resolvers(), Resolvers()
            for iproc in self.assembly.processors:
                assert isinstance(iproc, IProcessor), 'Invalid processor %s' % iproc
                iproc.register(sources, iresolvs, iextens, calls, report)
            
            if self.contextsUsing:
                uattrs = iresolvs.extract(self.contextsUsing)
                assert isinstance(uattrs, Resolvers)
                uattrs.solve(self.contextsUsing)
                uattrs.validate()
                uattrs.solve(iextens.extract(self.contextsUsing))
                report.add(uattrs)
                contexts = create(uattrs)
            else: contexts = None
            
            iresolvs.solve(processor.contexts)
            resolvers.merge(iresolvs)
            extensions.solve(iextens)
            return Processing(calls, contexts=contexts)
        
        except (ResolverError, AssemblyError): raise AssemblyError('Cannot process Included for %s' % self.assembly.name)
    
    # ----------------------------------------------------------------
    
    def using(self, **contexts):
        '''
        Declare the contexts that will not be included but will be used. This means that this context will be on processing
        contexts and have instances created for.
        
        @param contexts: key arguments{string, ContextMetaClass}
            The contexts to be used rather then included.
        @return: self
            This instance for chaining purposes.
        '''
        if __debug__:
            for name, clazz in contexts.items():
                assert isinstance(name, str), 'Invalid context name %s' % name
                assert isinstance(clazz, ContextMetaClass), 'Invalid context class %s' % clazz
        self.contextsUsing.update(**contexts)
        return self

# --------------------------------------------------------------------

def restructure(processor, *mapping):
    '''
    Handler that restructures the context names for the provided handler or processor.
    
    @param processor: Container|Processor
        Restructures the provided processor.
    @param mapping: arguments[tuple(string, string)]
        The mapping to restructure by. The mapping(s) are provided as tuples having on the first position the name of the 
        restructured processor context and as a second value to name of the context to use.
    @return: Handler
        The handler that has the restructured processor.
    '''
    if isinstance(processor, Container):
        assert isinstance(processor, Container)
        assert len(processor.processors) == 1, 'Container %s, is required to have only one processor' % processor
        processor = processor.processors[0]
    assert isinstance(processor, Processor), 'Invalid processor %s' % processor
    assert mapping, 'At least one mapping is required'
    
    clone = processor.clone()
    assert isinstance(clone, Processor), 'Invalid clone %s' % clone
    
    mappings = {}
    for nameFrom, nameTo in mapping:
        assert nameFrom in clone.contexts, 'Invalid name %s for contexts %s' % (nameFrom, clone.contexts)
        names = mappings.get(nameTo)
        if names is None: mappings[nameTo] = names = set()
        names.add(nameFrom)
    
    restructured = dict(clone.contexts)
    for nameTo, names in mappings.items():
        for nameFrom in names: restructured.pop(nameFrom, None) 
        # Just making sure that the restructured doens't contain the class anymore
        if len(names) > 1:
            resolvers = None
            for nameFrom in names:
                if resolvers is None: resolvers = Resolvers(contexts={nameTo: clone.contexts[nameFrom]})
                else: resolvers.solve({nameTo: clone.contexts[nameFrom]})
            restructured[nameTo] = createDefinition(resolvers)[nameTo]
        else:
            nameFrom = next(iter(names))
            restructured[nameTo] = clone.contexts[nameFrom]

    originalCall = clone.call
    def restructurer(*args, **keyargs):
        for nameTo, names in mappings.items():
            try: value = keyargs.pop(nameTo)
            except KeyError: continue
            for nameFrom in names: keyargs[nameFrom] = value
            
        originalCall(*args, **keyargs)
        
    clone.contexts = restructured
    clone.call = restructurer
    
    from .handler import Handler
    return Handler(clone)
