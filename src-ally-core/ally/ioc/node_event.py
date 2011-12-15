'''
Created on Dec 8, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Module containing the nodes for the IoC setup events.
'''

from .. import omni
from .node import SetupError, isConfig, PREFIX_CONFIG, IListener, \
    argumentsFor, argumentsPush, Initializer, Woman
from _abcoll import Callable
from inspect import isfunction
import logging

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

EVENT_BEFORE = 'before'
# Event used to signal that a before (context assemble, entity use) action.
EVENT_AFTER = 'after'
# Event used to signal that an after (context assemble, entity setup) action.
EVENTS = (EVENT_BEFORE, EVENT_AFTER)

# --------------------------------------------------------------------

def doFindEvent(self, *criteria):
    '''
    Finds the event node that recognizes the criteria.
    
    @param criteria: arguments
        The criteria(s) used to identify the node.
    @return: string
        The path of the event.
    '''
    if not self._isMatched(criteria) or not self._isChecked(): return omni.CONTINUE
    return self._path

def _processEvent(self):
    '''
    Handles the function event.
    '''
    if self.doIsValue(self._path, omni=omni.F_FIRST):
        raise SetupError('The event %s cannot be dispatched twice' % self)
    keyargs = {}
    for name in self._arguments:
        try: keyargs[name] = self.doGetValue(name, omni=omni.F_FIRST)
        except omni.NoResultError: raise SetupError('Could not find argument value %r for %s' % (name, self))
    self._listenersBefore()
    ret = self._call(**keyargs)
    if ret is not None: Initializer.initialize(ret)
    self._listenersAfter()
    self.doSetValue(self._path, True)
    log.debug('Processed the event %s', self)
        
class EventOnReference(Woman, IListener):
    '''
    @see: Node
    Provides the event delivering for nodes that respect the event reference.
    '''
    
    def __init__(self, name, event, call, arguments=None, reference=None):
        '''
        @see: Woman.__init__
        
        @param event: string
            The event name.
        @param call: Callable
            The function call to invoke for the event.
        @param arguments: list[string]|None
            The list of argument names to invoke the call with, None for no arguments.
        @param reference: string|None
            The reference of the event node.
        '''
        Woman.__init__(self, name)
        assert event in EVENTS, 'Invalid event %s' % event
        if isConfig(self._name):
            raise SetupError('The event name %r cannot start with %r' % (self._name, PREFIX_CONFIG))
        assert isinstance(call, Callable), 'Invalid callable object %s' % call
        self._call = call
        if arguments:
            assert isinstance(arguments, list), 'Invalid arguments %s' % arguments
            if __debug__:
                for argn in arguments: assert isinstance(argn, str), 'Invalid argument name %s' % argn
            self._arguments = arguments
        else: self._arguments = []
        assert not reference or isinstance(reference, str), 'Invalid reference %s' % reference
        self._event = event
        self._reference = reference
        
    arguments = property(lambda self: self._arguments, doc=
'''
@type arguments: list[string]
    The arguments of the function of the event.
''')
    
    doFindEvent = omni.resolver(doFindEvent)
    
    @omni.resolver      
    def doFindUnused(self, *criteria):
        '''
        Finds the node that recognizes the criteria and is considered unused.
        
        @param criteria: arguments
            The criteria(s) used to identify the node. If no criteria is provided than the event is considered valid for
            all nodes.
        @return: string
            The path of the unused event.
        '''
        if not self._isMatched(criteria) or not self._isChecked(): return omni.CONTINUE
        if self.doIsValue(self._path, omni=omni.F_FIRST): return omni.CONTINUE
        return self._path
    
    @omni.resolver
    def doAssemble(self):
        '''
        Assembles this event.
        '''
        if not self._reference: raise SetupError('The event has no reference specified')
        paths = self.doAddListener(self, self._reference)
        if len(paths) > 1: raise SetupError('To many paths %s found for reference %r' % (paths, self._reference))
        return omni.CONTINUE # We just let others also assemble, especially the bridged ones.
    
    @omni.resolver
    def doEvent(self, *criteria):
        #TODO: comment
        if not self._isMatched(criteria) or not self._isChecked(): return omni.CONTINUE
        _processEvent(self)
        return True
        
    def forReference(self, reference):
        '''
        Set the reference for the event.
        
        @param reference: string
            The reference of the event node.
        '''
        assert isinstance(reference, str), 'Invalid reference %s' % reference
        self._reference = reference
        return self
        
    def before(self):
        '''
        @see: IListener.before
        '''
        if self._event == EVENT_BEFORE and self._isChecked(): self.doEvent(self._path)
        
    def after(self):
        '''
        @see: IListener.after
        '''
        if self._event == EVENT_AFTER and self._isChecked(): self.doEvent(self._path)

class EventOnStart(Woman):
    '''
    @see: Node
    Provides the event delivering for starting the structure.
    '''
    
    def __init__(self, name, call, arguments=None):
        '''
        @see: Woman.__init__
        
        @param call: Callable
            The function call to invoke for the event.
        @param arguments: list[string]|None
            The list of argument names to invoke the call with, None for no arguments.
        '''
        Woman.__init__(self, name)
        if isConfig(name):
            raise SetupError('The event name %r cannot start with %r' % (name, PREFIX_CONFIG))
        assert isinstance(call, Callable), 'Invalid callable object %s' % call
        self._call = call
        if arguments:
            assert isinstance(arguments, list), 'Invalid arguments %s' % arguments
            if __debug__:
                for argn in arguments: assert isinstance(argn, str), 'Invalid argument name %s' % argn
            self._arguments = arguments
        else: self._arguments = []
    
    doFindEvent = omni.resolver(doFindEvent)
    
    @omni.resolver
    def doStart(self, *criteria):
        '''
        Start this event.
        
        @param criteria: arguments
            The criteria(s) used to identify the node. If no criteria is provided than the event is considered valid for
            all nodes.
        '''
        if self._isMatched(criteria) and self._isChecked(): _processEvent(self)
        return omni.CONTINUE # We just let others also assemble, especially the bridged ones.

# --------------------------------------------------------------------

def eventReferencedFrom(function, event, name=None, reference=None):
    '''
    Constructs a IoC referenced event based on the provided function.
    
    @param function: function 
        The function to convert to Function.
    @param event: string
        The event to be associated with the function.
    @param name: string|None
        The name to use for the function, if not specified it will use the function name.
    @param reference: string|None
        The reference to use for the event function.
    @return: EventOnReference
        The converted EventOnReference.
    '''
    assert name is None or isinstance(name, str), 'Invalid name %s' % name

    assert isfunction(function), 'Invalid function %s' % function
    name = name or function.__name__

    arguments, defaults, annotations = argumentsFor(function)
    
    if 'return' in annotations:
        raise SetupError('No return annotation expected for event function %r' % function.__name__)

    ev = EventOnReference(name, event, function, arguments, reference)
    argumentsPush(ev, arguments, defaults, annotations)
    
    return ev

def eventStartFrom(function, name=None):
    '''
    Constructs a IoC start event based on the provided function.
    
    @param function: function 
        The function to convert to Function.
    @param name: string|None
        The name to use for the function, if not specified it will use the function name.
    @return: EventOnStart
        The converted EventOnStart.
    '''
    assert name is None or isinstance(name, str), 'Invalid name %s' % name

    assert isfunction(function), 'Invalid function %s' % function
    name = name or function.__name__

    arguments, defaults, annotations = argumentsFor(function)
    
    if 'return' in annotations:
        raise SetupError('No return annotation expected for event function %r' % function.__name__)

    ev = EventOnStart(name, function, arguments)
    argumentsPush(ev, arguments, defaults, annotations)
    
    return ev
