'''
Created on Feb 11, 2013

@package: ally base
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Contains the handlers support.
'''

from .assembly import Container
from .processor import Contextual, Brancher
import abc

# --------------------------------------------------------------------

class Handler(Container):
    '''
    Handler base that provides a container for a processor.
    '''

    def __init__(self, processor):
        '''
        Construct the handler.
        
        @param processor: IProcessor
            The processor for the container.
        '''
        super().__init__(processor)

class HandlerProcessor(Handler):
    '''
    A handler that contains a processor derived on the contextual 'process' function.
    '''

    def __init__(self):
        '''
        Construct the handler with the processor automatically created from the 'process' function.
        '''
        super().__init__(Contextual(self.process, proceed=False))

    @abc.abstractclassmethod
    def process(self, chain, **keyargs):
        '''
        The contextual process function used by the handler.
        
        @param chain: Chain
            The processing chain.
        '''

class HandlerProcessorProceed(Handler):
    '''
    A handler that contains a processor derived on the contextual 'process' function and automatically proceeds the chain.
    '''

    def __init__(self):
        '''
        Construct the handler with the processor automatically created from the 'process' function.
        '''
        super().__init__(Contextual(self.process, proceed=True))

    @abc.abstractclassmethod
    def process(self, **keyargs):
        '''
        The contextual process function used by the handler, this process will not require a chain and will always
        proceed with the execution.
        '''
        
# --------------------------------------------------------------------

class HandlerBranching(Handler):
    '''
    A handler that contains a processor derived on the contextual 'process' function that also provides branching for other
    processors containers based on the setup provided at construction.
    '''

    def __init__(self, *branches):
        '''
        Construct the handler with the processor automatically created from the 'process' function and the including or 
        branching based on the provided processors containers.
        
        @param branches: arguments[IBranch]
            The branches used in branching, attention the order provided for setups will be reflected in the provided 
            processing order.
        '''
        super().__init__(Brancher(self.process, *branches, proceed=False))

    @abc.abstractclassmethod
    def process(self, chain, *processings, **keyargs):
        '''
        The contextual process function used by the handler.
        
        @param chain: Chain
            The processing chain.
        @param processings: arguments[Processing]
            The processings to use for branching, in the order the initial branches setups have been provided.
        '''
        
class HandlerBranchingProceed(Handler):
    '''
    A handler that contains a processor derived on the contextual 'process' function that also provides branching
    and automatically proceeds the chain.
    '''
    
    def __init__(self, *branches):
        '''
        Construct the handler with the processor automatically created from the 'process' function and the including or 
        branching based on the provided processors containers.
        
        @param branches: arguments[IBranch]
            The branches used in branching, attention the order provided for setups will be reflected in the provided 
            processing order.
        '''
        super().__init__(Brancher(self.process, *branches, proceed=True))


    @abc.abstractclassmethod
    def process(self, *processings, **keyargs):
        '''
        The contextual process function used by the handler, this process will not require a chain and will always
        proceed with the execution.
        
        @param processings: arguments[Processing]
            The processings to use for branching, in the order the initial branches setups have been provided.
        '''