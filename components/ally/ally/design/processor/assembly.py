'''
Created on Feb 11, 2013

@package: ally base
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Contains the assembly support.
'''

from .context import create
from .execution import Processing
from .spec import IProcessor, AssemblyError, Resolvers
from abc import ABCMeta
from ally.design.processor.report import ReportUnused
from collections import Iterable
import logging

# --------------------------------------------------------------------

log = logging.getLogger(__name__)
ABCMeta = ABCMeta  # Just to avoid the warning

# --------------------------------------------------------------------

class Container(metaclass=ABCMeta):
    '''
    Specification for classes that are processor containers.
    '''
    
    def __init__(self, *processors):
        '''
        Constructs the container using the provided processors.
        '''
        self.processors = list(processors)
        for processor in self.processors: assert isinstance(processor, IProcessor), 'Invalid processor %s' % processor
        
class Assembly(Container):
    '''
    The assembly provides a container for the processors.
    '''
    
    def __init__(self, name):
        '''
        Constructs the assembly.
        
        @param name: string
            The name of the assembly mainly used for reporting purposes.
        '''
        assert isinstance(name, str), 'Invalid name %s' % name
        super().__init__()
        self.name = name

    def add(self, *processors, before=None, after=None):
        '''
        Add to the assembly the provided processors.
        
        @param processors: arguments[IProcessor|Container|list[IProcessor|Container]|tuple(IProcessor|Container)]
            The processor(s) to be added to the assembly.
        @param before: IProcessor|Container
            The processor(s) will be ordered before this processor, you can only specify before or after.
        @param after: IProcessor|Container
            The processor(s) will be ordered after this processor, you can only specify after or before.
        '''
        index = self._indexFrom(before, after)
        for processor in self._processorsFrom(processors):
            self.processors.insert(index, processor)
            index += 1

    def move(self, processor, before=None, after=None):
        '''
        Moves in to the assembly the provided processor.
        
        @param processor: IProcessor|Container
            The processor to be moved in to the assembly.
        @param before: IProcessor|Container
            The processor(s) will be moved before this processor, you can only specify before or after.
        @param after: IProcessor|Container
            The processor(s) will be moved after this processor, you can only specify after or before.
        '''
        assert before is not None or after is not None, 'You need to provide an after or a before processor in order to move'
        processor = self._processorFrom(processor)
        try: self.processors.remove(processor)
        except ValueError: raise AssemblyError('Unknown processor %s in assembly' % processor)
        index = self._indexFrom(before, after)
        self.processors.insert(index, processor)

    def replace(self, replaced, replacer):
        '''
        Replaces in to the assembly the provided processors.
        
        @param replaced: IProcessor|Container
            The processor to be replaced in to the assembly.
        @param replacer: IProcessor|Container
            The processor that will replace.
        '''
        try: index = self.processors.index(self._processorFrom(replaced))
        except ValueError: raise AssemblyError('Invalid replaced processor %s' % replaced)
        self.processors[index] = self._processorFrom(replacer)
        
    def remove(self, *processors):
        '''
        Removes from the assembly the provided processor.
        
        @param processor: arguments[IProcessor|Container]
            The processor to be removed from the assembly.
        '''
        assert processors, 'At least one processor is required to be removed'
        for processor in processors:
            try: index = self.processors.index(self._processorFrom(processor))
            except ValueError: raise AssemblyError('Invalid processor %s to be removed' % processor)
            del self.processors[index]

    def create(self, **contexts):
        '''
        Create a processing based on all the processors in the assembly.
        
        @param contexts: key arguments of ContextMetaClass
            Key arguments that have as a value the context classes that the processing chain will be used with.
        @return: Processing|tuple of two
            processing: Processing
            A processing created based on the current structure of the assembly.
            report: string
            A text containing the report for the processing creation
        '''
        report = ReportUnused()
        calls, sources, resolvers, extensions = [], Resolvers(True, contexts), Resolvers(), Resolvers()
        for processor in self.processors:
            assert isinstance(processor, IProcessor), 'Invalid processor %s' % processor
            processor.register(sources, resolvers, extensions, calls, report)
            
        resolvers.solve(sources)
        resolvers.validate()
        resolvers.solve(extensions)
        processing = Processing(calls, create(resolvers))
        reportAss = report.open('Assembly \'%s\'' % self.name)
        reportAss.add(resolvers)
        
        lines = report.report()
        if lines: log.info('\n%s\n' % '\n'.join(lines))
        else: log.info('Nothing to report for \'%s\', everything fits nicely', self.name)
        return processing

    # ----------------------------------------------------------------

    def _processorFrom(self, processor):
        '''
        Provides an the processor from the provided processor or container.
        
        @param processor: IProcessor|Container
            The processor or handler to get the processor for.
        '''
        if isinstance(processor, IProcessor): return processor
        elif isinstance(processor, Container):
            assert isinstance(processor, Container)
            assert len(processor.processors) == 1, 'Container %s, is required to have only one processor' % processor
            processor = processor.processors[0]
            assert isinstance(processor, IProcessor), 'Invalid processor %s' % processor
            return processor

        raise AssemblyError('Invalid processor or container %s' % processor)

    def _processorsFrom(self, processors):
        '''
        Provides an iterable of the processors obtained from the provided processors or processors containers.
        
        @param processors: Iterable[Processor|Container| list[Processor|Container]|tuple(Processor|Container)]
            The processors or processors containers to be made in an iterable of processors.
        '''
        assert isinstance(processors, Iterable), 'Invalid processors %s' % processors

        for processor in processors:
            if isinstance(processor, (list, tuple)):
                for processor in self._processorsFrom(processor): yield processor

            elif isinstance(processor, Container):
                assert isinstance(processor, Container)
                for processor in  processor.processors: yield processor
            elif isinstance(processor, IProcessor): yield processor
            else: raise AssemblyError('Invalid processor or container %s' % processor)

    def _indexFrom(self, before=None, after=None):
        '''
        Provides the index where to insert based on the provided before and after processors.
        
        @param before: Processor|Container
            The processor(s) will be moved before this processor, you can only specify before or after.
        @param after: Processor|Container
            The processor(s) will be moved after this processor, you can only specify after or before.
        @return: integer
            The index where to insert.
        '''
        index = len(self.processors)
        if before is not None:
            before = self._processorFrom(before)
            assert after is None, 'Cannot have before and after at the same time'

            try: index = self.processors.index(before)
            except ValueError: raise AssemblyError('Unknown before processor %s in assembly' % before)

        elif after is not None:
            after = self._processorFrom(after)

            try: index = self.processors.index(after) + 1
            except ValueError: raise AssemblyError('Unknown after processor %s in assembly' % after)
        return index
    
    def __str__(self):
        return '%s \'%s\' with %s processors' % (self.__class__.__name__, self.name, len(self.processors))
