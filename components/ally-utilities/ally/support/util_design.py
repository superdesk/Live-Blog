'''
Created on May 21, 2012

@package: utilities
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides implementations for general design patterns that can be easily used.
'''

from collections import Iterable, deque
import logging

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

class Chain:
    '''
    A chain that contains a list of processors that are executed one by one. Each processor will have the duty
    to proceed with the processing if is the case by calling the chain.
    '''

    def __init__(self, calls):
        '''
        Initializes the chain with the processors to be executed.
        
        @param calls: Iterable[callable]
            The iterable of callables to be executed. Attention the order in which the callables are provided
            is critical since one call is responsible for delegating to the next.
            The callable needs to take as parameters the arguments passed to the process method + the chain instance.
        '''
        assert isinstance(calls, Iterable), 'Invalid calls %s' % calls
        self._calls = deque(calls)
        if __debug__:
            for call in self._calls: assert callable(call), 'Invalid callable %s' % call

        self._consumed = False

    def proceed(self):
        '''
        Indicates to the chain that it should proceed with the chain execution after a processor has returned. The proceed
        is available only when the chain is in execution. The execution is continued with the same arguments.
        '''
        self._proceed = True

    def process(self, *args):
        '''
        Called in order to execute the next processors in the chain. This method will stop processing when all
        the processors have been executed.
        
        @param args: arguments
            The arguments to dispatch to the next callable to be executed.
        '''
        proceed = True
        while proceed:
            proceed = self._proceed = False
            if len(self._calls) > 0:
                proc = self._calls.popleft()

                assert log.debug('Processing %r', proc) or True
                proc(*(args + (self,)))
                assert log.debug('Processing finalized %r', proc) or True

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
