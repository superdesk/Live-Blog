'''
Created on Jun 11, 2012

@package: utilities
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Module containing a processor dynamic execution chain. There is a handler that composes an execution chain with 
dynamic parameters.
'''

from ally.support.util import Uninstantiable
from ally.support.util_sys import callerLocals
from collections import Iterable, deque
from inspect import isclass, isfunction, getfullargspec
from itertools import chain
import abc
import logging

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

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

class Classes:
    '''
    Container for the processing classes.
    '''

    def __init__(self, **classes):
        '''
        Construct the classes container.
        
        @param classes: key arguments of class
            The key arguments to be used in calling the processors.
        '''
        for name, clazz in classes.items():
            assert isclass(clazz), 'Invalid class %s' % clazz
            setattr(self, name, clazz)

class Processing:
    '''
    Container for processor's, provides chains for their execution.
    !!! Attention, never ever use a processing in multiple threads, only one thread is allowed to execute 
    a processing at one time.
    '''
    __slots__ = ('classes', 'processors')

    def __init__(self, handlers, classes):
        '''
        @param handlers: Iterable(IHandler)
            The list of handlers that will compose this processing.
        @param classes: Classes
            The classes container.
        '''
        assert isinstance(handlers, Iterable), 'Invalid handlers %s' % handlers
        assert isinstance(classes, Classes), 'Invalid classes %s' % classes

        self.classes = classes
        self.processors = []

        for handler in handlers:
            assert isinstance(handler, IHandler), 'Invalid handler %s' % handler
            handler.prepare(self)

    def newChain(self):
        '''
        Constructs a new processors chain.
        
        @return: Chain
            The chain of processors.
        '''
        return Chain(self.processors)

class IHandler(metaclass=abc.ABCMeta):
    '''
    The handler prepares the processing that will be used for creating execution chains.
    '''

    @abc.abstractmethod
    def prepare(self, processing):
        '''
        Prepare the context for processing.
        
        @param processing: Processing
            The processors context to prepare.
        '''

# --------------------------------------------------------------------

def assemble(processing, processor, required=None, extends=None, **arguments):
    '''
    Assembles into the provided processing context the provided processor based on the required classes and
    extend classes.
    
    @param processing: Processing
        The processing to assemble into.
    @param processor: callable
        The processor callable to be assembled.
    @param required: dictionary{string, class|tuple(class)}|None
        The required classes for the arguments that will be passed to the processor. The key is name of the argument
        and the value represents the class or classes required for that argument.
    @param extends: dictionary{string, class|tuple(class)}|None
        The extended classes for the arguments that will be passed to the processor. The key is name of the argument
        and the value represents the class or classes that will extend the argument value.
    @param arguments: key arguments of class
        The arguments classes for the processor, if a class is a Mokup it will be used based on the mokup
        specifications, otherwise the provided class is considered a required class.
    '''
    assert isinstance(processing, Processing), 'Invalid processing %s' % processing
    assert callable(processor), 'Invalid processor %s' % processor

    if required is None: required = {}
    if extends is None: extends = {}
    assert isinstance(required, dict), 'Invalid required %s' % required
    assert isinstance(extends, dict), 'Invalid extend %s' % extends

    required = {name:classes if isinstance(classes, tuple) else (classes,) for name, classes in required.items()}
    extends = {name:classes if isinstance(classes, tuple) else (classes,) for name, classes in extends.items()}

    if arguments: append(required, extends, arguments)

    for name, classes in required.items():
        current = getattr(processing.classes, name, None)
        if current is None:
            log.info('Excluded processor %s because there is no argument \'%s\' provided', processor, name)
            return
        for clazz in classes:
            assert isclass(clazz), 'Invalid required class %s for argument %s' % (clazz, name)
            if not issubclass(current, clazz):
                log.info('Excluded processor %s because the current class %s is not extending %s',
                         processor, current, clazz) or True
                return

    processing.processors.append(processor)

    for name, classes in extends.items():
        if not isinstance(classes, tuple): classes = (classes,)
        current = getattr(processing.classes, name, None)

        for clazz in classes:
            assert isclass(clazz), 'Invalid extend class %s for argument %s' % (clazz, name)

            if current is None: current = clazz
            else: current = extends(current, clazz)

        setattr(processing.classes, name, current)

def ext(clazz):
    '''
    Marks the provided class as an extend class whenever is passed on as an append class.
    
    @param clazz: class
        The class to mark as extend.
    '''
    assert isclass(clazz), 'Invalid class %s' % clazz

    return Mark(clazz, False)

def append(required, extends, classes):
    '''
    Appends on the required and extends dictionary the provided arguments.
    
    @param required: dictionary{string, tuple(class)}
        The required argument classes.
    @param extends: dictionary{string, tuple(class)}
        The extend argument classes.
    @param classes: dictionary{name, class|tuple(class)|Mark|tuple(Mark))
        The arguments classes for the processor, if a class is a Mokup it will be used based on the mokup
        specifications, otherwise the provided class is considered a required class.
    '''
    assert isinstance(required, dict), 'Invalid required %s' % required
    assert isinstance(extends, dict), 'Invalid extends %s' % extends
    assert isinstance(classes, dict), 'Invalid classes %s' % classes

    for name, clazzes in classes.items():
        assert isinstance(name, str), 'Invalid argument name %s' % name
        if not isinstance(clazzes, tuple): clazzes = (clazzes,)
        for clazz in clazzes:
            requiredAdd, extendAdd = None, None
            if isinstance(clazz, Mark):
                assert isinstance(clazz, Mark)
                if clazz.required: requiredAdd = (clazz.clazz,)
                else: extendAdd = (clazz.clazz,)
            else:
                assert isclass(clazz), 'Invalid argument \'%s\' with class %s' % (name, clazz)
                if issubclass(clazz, Mokup):
                    requiredAdd = clazz._ally_mokup_required
                    extendAdd = clazz._ally_mokup_extend
                else: requiredAdd = (clazz,)

            if requiredAdd:
                clazzes = required.get(name)
                if clazzes:
                    assert isinstance(clazzes, tuple), \
                    'Invalid required clazzes %s for argument %s' % (clazzes, name)
                    clazzes = clazzes + requiredAdd
                else: clazzes = requiredAdd
                required[name] = clazzes

            if extendAdd:
                clazzes = extends.get(name)
                assert isinstance(clazzes, tuple), \
                'Invalid extend clazzes %s for argument %s' % (clazzes, name)
                if clazzes: clazzes = clazzes + extendAdd
                else: clazzes = extendAdd
                extends[name] = clazzes

def mokup(*required):
    '''
    Provides a decorator for mokup classes used mainly for type hinting, this decorator will make the class
    uninstantiable and also provide the specifications for assembly.
    
    @param required: arguments[class]
        The required classes of the mokup, the decorated class should directly extend all classes(required+extended).
    '''
    if __debug__:
        for clazz in required: assert isclass(clazz), 'Invalid class %s' % clazz

    def decorator(clazz):
        assert isclass(clazz), 'Invalid decorated class %s' % clazz
        namespace = dict(_ally_mokup_required=required,
                         _ally_mokup_extend=set(clazz.__bases__).difference(required))
        namespace['__module__'] = clazz.__module__
        return type('%s$Mokup' % clazz.__name__, (Mokup,) + clazz.__bases__, namespace)

    return decorator

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

    arguments = {}
    for name in fnArgs.args[2:]:
        clazz = fnArgs.annotations.get(name)
        assert clazz is not None, 'Expected an annotation of class or tuple(class) for argument %s'
        arguments[name] = clazz

    required, extends = {}, {}
    append(required, extends, arguments)

    locals = callerLocals()
    processors = locals.get('processors')
    if processors is None: locals['processors'] = processors = []

    processors.append(Processor(function, required, extends))

    return function

class Handler(IHandler):
    '''
    Implementation for a @see: IHandler that provides the preparing based on functions that have been decorated with 
    @see: processor.
    '''

    def prepare(self, processing):
        '''
        @see: IHandler.prepare
        '''
        assert hasattr(self, 'processors'), 'No processors available'
        assert isinstance(processing, Processing), 'Invalid processing %s' % processing

        for processor in self.processors:
            assert isinstance(processor, Processor), 'Invalid processor %s' % processor
            assemble(processing, processor.processor, processor.required, processor.extends)

# --------------------------------------------------------------------

class Mark:
    '''
    Used for marking classes for appending.
    '''
    __slots__ = ('clazz', 'required')

    def __init__(self, clazz, required):
        '''
        Construct the mark.
        
        @param clazz: class
            The class marked.
        @param required: boolean
            True if the class is a required class or False for an extend class.
        '''
        assert isclass(clazz), 'Invalid class %s' % clazz
        assert isinstance(required, bool), 'Invalid required flag %s' % required

        self.clazz = clazz
        self.required = required

class Mokup(Uninstantiable, metaclass=abc.ABCMeta):
    '''
    The mokup base class.
    '''
    _ally_mokup_required = () # Contains all the required classes
    _ally_mokup_extend = () # Contains all the extending classes

    @classmethod
    def __subclasshook__(cls, C):
        for clazz in chain(cls._ally_mokup_required, cls._ally_mokup_extend):
            if not issubclass(C, clazz): return False
        return True

class Processor:
    '''
    Class that contains the specifications for a processor.
    '''
    __slots__ = ('processor', 'required', 'extends')

    def __init__(self, processor, required, extends):
        '''
        Construct the processor.
        
        @param processor: callable
            The processor callable.
        @param required: dictionary{string, tuple(class)}
            The required argument classes.
        @param extends: dictionary{string, tuple(class)}
            The extend argument classes.
        '''
        assert callable(processor), 'Invalid processor %s' % processor
        assert isinstance(required, dict), 'Invalid required %s' % required
        assert isinstance(extends, dict), 'Invalid extends %s' % extends
        if __debug__:
            for name, classes in required:
                assert isinstance(name, str), 'Invalid required name %s' % name
                assert isinstance(classes, tuple), 'Invalid required classes %s' % classes
                for clazz in classes:
                    assert isclass(clazz), 'Invalid argument %s required class %s' % (name, clazz)
            for name, classes in extends:
                assert isinstance(name, str), 'Invalid extend name %s' % name
                assert isinstance(classes, tuple), 'Invalid extend classes %s' % classes
                for clazz in classes:
                    assert isclass(clazz), 'Invalid argument %s extend class %s' % (name, clazz)

        self.processor = processor
        self.required = required
        self.extends = extends
