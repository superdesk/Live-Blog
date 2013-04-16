'''
Created on Feb 11, 2013

@package: ally base
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Contains the classes used in the execution of processors.
'''

from .spec import ContextMetaClass
from collections import Iterable, deque
import logging

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------
        
class Processing:
    '''
    Container for processor's, provides chains for their execution.
    !!! Attention, never ever use a processing in multiple threads, only one thread is allowed to execute 
    a processing at one time.
    '''
    __slots__ = ('ctx', '_calls')

    class Ctx:
        '''
        Provides the contexts proxy for an easier access.
        '''
        if __debug__:
            def __setattr__(self, key, clazz):
                assert isinstance(key, str), 'Invalid context name %s' % key
                assert not key.startswith('_'), 'The context name \'%s\' cannot start with an _' % key
                assert isinstance(clazz, ContextMetaClass), 'Invalid context class %s for %s' % (clazz, key)
                object.__setattr__(self, key, clazz)

    def __init__(self, calls, contexts=None):
        '''
        Construct the processing.
        
        @param calls: Iterable(callable)
            The iterable of calls that consists this processing.
        @param contexts: dictionary{string, ContextMetaClass}|None
            The initial contexts to be associated.
        '''
        assert isinstance(calls, Iterable), 'Invalid calls %s' % calls
        
        self._calls = list(calls)
        if __debug__:
            for call in self._calls: assert callable(call), 'Invalid call %s' % call
                
        self.ctx = Processing.Ctx()
        if contexts:
            assert isinstance(contexts, dict), 'Invalid contexts %s' % contexts
            if __debug__:
                for key, clazz in contexts.items():
                    assert isinstance(key, str), 'Invalid context name %s' % key
                    assert isinstance(clazz, ContextMetaClass), 'Invalid context class %s for %s' % (clazz, key)
            self.ctx.__dict__.update(contexts)
        
    contexts = property(lambda self: self.ctx.__dict__.items(), doc='''
    @rtype: Iterable(tuple(string, Context class))
    The iterable containing key: value pairs of the contained meta classes.
    ''')
    calls = property(lambda self: self._calls, doc='''
    @rtype: Iterable(call)
    The iterable containing the calls of this processing.
    ''')
    
    def update(self, **contexts):
        '''
        Used to update the contexts of the processing.

        @param contexts: dictionary{string, ContextMetaClass}
            The contexts to update with.
        @return: this processing
            This processing for chaining purposes.
        '''
        if __debug__:
            for key, clazz in contexts.items():
                assert isinstance(key, str), 'Invalid context name %s' % key
                assert isinstance(clazz, ContextMetaClass), 'Invalid context class %s for %s' % (clazz, key)
        self.ctx.__dict__.update(contexts)
        return self
    
    def fillIn(self, **keyargs):
        '''
        Updates the provided arguments with the rest of the contexts that this processing has. The fill in process is done
        when a context name is not present in the provided arguments, the value added is being as follows:
            - if the context name start with a capital letter then the class is provided as a value
            - if the context names starts with a lower case then an instance is created for the class and used as a value.
        
        @param keyargs: key arguments
            The key arguments to be filled in.
        @return: dictionary{string: object}
            The fill in key arguments.
        '''
        for name, clazz in self.contexts:
            if name not in keyargs:
                if name[:1].lower() == name[:1]: keyargs[name] = clazz()
                else: keyargs[name] = clazz
        return keyargs

class Chain:
    '''
    A chain that contains a list of processors (callables) that are executed one by one. Each processor will have
    the duty to proceed with the processing if is the case by calling the chain.
    '''
    __slots__ = ('arg', '_calls', '_callBacks', '_callBacksErrors', '_consumed', '_proceed')

    class Arg:
        '''
        Provides the arguments proxy for an easier access.
        '''
        if __debug__:
            def __setattr__(self, key, value):
                assert isinstance(key, str), 'Invalid argument name %s' % key
                assert not key.startswith('_'), 'The argument name \'%s\' cannot start with an _' % key
                object.__setattr__(self, key, value)

    def __init__(self, processing):
        '''
        Initializes the chain with the processing to be executed.
        
        @param processing: Processing|Iterable[callable]
            The processing to be handled by the chain. Attention the order in which the processors are provided
            is critical since one processor is responsible for delegating to the next.
        '''
        if isinstance(processing, Processing):
            assert isinstance(processing, Processing)
            processing = processing.calls
        assert isinstance(processing, Iterable), 'Invalid processing %s' % processing
        self._calls = deque(processing)
        if __debug__:
            for call in self._calls: assert callable(call), 'Invalid processor call %s' % call
        self.arg = Chain.Arg()
        self._callBacks = deque()
        self._callBacksErrors = deque()
        self._consumed = False

    def proceed(self):
        '''
        Indicates to the chain that it should proceed with the chain execution after a processor has returned. 
        The proceed is available only when the chain is in execution. The execution is continued with the same
        arguments.
        
        @return: this chain
            This chain for chaining purposes.
        '''
        assert not self._consumed, 'Chain is consumed cannot proceed'
        self._proceed = True
        return self

    def process(self, **keyargs):
        '''
        Called in order to execute the next processors in the chain. This method registers the chain proceed
        execution but in order to actually execute you need to call the *do* or *doAll* method.
        
        @param keyargs: key arguments
            The key arguments that are passed on to the next processors.
        @return: this chain
            This chain for chaining purposes.
        '''
        assert not self._consumed, 'Chain is consumed cannot process'
        self.arg.__dict__.clear()
        for key, value in keyargs.items(): setattr(self.arg, key, value)
        self._proceed = True
        return self
    
    def update(self, **keyargs):
        '''
        Used to update the key arguments of the processing and also mark the chain for proceeding. A *process* method
        needs to be executed first.

        @param keyargs: key arguments
            The key arguments that need to be updated and passed on to the next processors.
        @return: this chain
            This chain for chaining purposes.
        '''
        assert not self._consumed, 'Chain is consumed cannot update'
        for key, value in keyargs.items(): setattr(self.arg, key, value)
        self._proceed = True
        return self
        
    def branch(self, processing):
        '''
        Branches the chain to a different processing and automatically marks the chain for proceeding.
        If the key arguments are not updated they must be compatible from the previous processing.
        
        @param processing: Processing|Iterable[callable]
            The processing to be handled by the chain. Attention the order in which the processors are provided
            is critical since one processor is responsible for delegating to the next.
        @return: this chain
            This chain for chaining purposes.
        '''
        if isinstance(processing, Processing):
            assert isinstance(processing, Processing)
            processing = processing.calls
        assert isinstance(processing, Iterable), 'Invalid processing %s' % processing
        self._calls.clear()
        self._calls.extend(processing)
        self._proceed = True
        return self
    
    def callBack(self, callBack):
        '''
        Add a call back to the chain that will be called after the chain is completed.
        Also marks the chain as proceeding.
        
        @param callBack: callable(*keyargs)
            The call back.
        @return: this chain
            This chain for chaining purposes.
        '''
        assert not self._consumed, 'Chain is consumed cannot add call back'
        self._callBacks.append(callBack)
        self._proceed = True
        return self
        
    def callBackError(self, callBack):
        '''
        Add a call back to the chain that will be called if an error occurs. In the received key arguments there will
        be also the error that occurred and the trace back of the error. If there is at least one error call back in 
        the chain the exception that will occur in the chain will not be propagated. Also marks the chain as proceeding.
        
        @param callBack: callable(*keyargs)
            The call back.
        @return: this chain
            This chain for chaining purposes.
        '''
        assert not self._consumed, 'Chain is consumed cannot add call back error'
        self._callBacksErrors.append(callBack)
        self._proceed = True
        return self
        
    def do(self):
        '''
        Called in order to do the next chain element. A *process* method needs to be executed first.
        
        @return: boolean
            True if the chain has performed the execution of the next element, False if there is no more to be executed.
        '''
        assert not self._consumed, 'Chain is consumed cannot do anymore'
        assert self._calls, 'Nothing to execute'
        assert self._proceed, 'Cannot proceed if no process is called'
        
        call = self._calls.popleft()
        assert log.debug('Processing %s', call) or True
        self._proceed = False
        try: call(self, **self.arg.__dict__)
        except:
            if self._callBacksErrors:
                self._proceed = False
                while self._callBacksErrors: self._callBacksErrors.pop()()
            else: raise
                
        assert log.debug('Processing finalized \'%s\'', call) or True
        if self._proceed:
            assert log.debug('Proceed signal received, continue execution') or True
            if self._calls: return True
            assert log.debug('Processing finalized by consuming') or True
            self._consumed = True
        else:
            self._calls.clear()
        while self._callBacks: self._callBacks.pop()()
        return False
        
    def doAll(self):
        '''
        Do all the chain elements. A *process* method needs to be executed first.

        @return: this chain
            This chain for chaining purposes.
        '''
        while True:
            if not self.do(): break
        return self

    def isConsumed(self):
        '''
        Checks if the chain is consumed.
        
        @return: boolean
            True if all processors from the chain have been executed, False if a processor from the chain has stopped
            the execution of the other processors.
        '''
        return self._consumed
