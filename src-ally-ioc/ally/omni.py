'''
Created on Dec 11, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Module that contains the omni event handling. Basically is just a framework that allows event dispatching based on class
defined methods. As an example we have:

class A:

    def doSomething(self, event, condition):
        if condition:
            print('Heloo')
        return omni.CONTINUE

class B:

    def __init__(self):
        self.parent = None
        self.children = []
    
    def start(self):
        omni.dispatch('Something', True).stopAtFirst(True).to(self.children, self.parent)
'''

import logging
from collections import deque
from _abcoll import Callable

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------
# Markers

CONTINUE = object()
# An object used as a marker when a delegated function cannot handle the provided data and wants the omni event
# dispatching to continue.

# --------------------------------------------------------------------

_PREFIX_RESOLVER = 'do'
# The resolver functions are considered only if they have the provided prefix.

# --------------------------------------------------------------------

class Omni:
    '''
    Provides the omni event container.
    '''
    
    __slots__ = ['_name', '_nameResolver', '_handlers', '_exclude', '_args']
    
    def __init__(self, name):
        '''
        Construct the event with the provided name.
        
        @param name: string
            The event name. This is the resolver method name without the handler prefix.
        '''
        assert isinstance(name, str), 'Invalid name %s' % name
        self._name = name
        self._nameResolver = _PREFIX_RESOLVER + name
        self._handlers = deque()
        self._exclude = set()
        self._args = None
        
    name = property(lambda self: self._name, doc=
'''
@type name: string
    The event name.
''')
    
    def add(self, *handlers):
        '''
        Adds to the handlers list the provided handlers for handling the event. 
        
        @param handlers: arguments
            The handler objects to be used in the event dispatch.
        @return: self
            For chaining purposes.
        '''
        if __debug__:
            for handler in handlers: assert handler is not None, 'Cannot add a None handler'
        self._handlers.extend(handlers)
        return self
        
    def exclude(self, *handlers):
        '''
        Exclude the handlers from handling the event. 
        
        @param handlers: arguments
            The handler objects to be excluded from the event dispatch.
        @return: self
            For chaining purposes.
        '''
        if __debug__:
            for handler in handlers: assert handler is not None, 'Cannot exclude a None handler'
        self._exclude.update(id(handler) for handler in handlers)
        return self
    
    def args(self, *args, **keyargs):
        '''
        Sets the arguments to be passed to the handlers when handling the event.
        
        @param args: arguments
            The arguments to be delivered to the handlers.
        @param keyargs: key arguments
            The key arguments to be delivered to the handlers.
        @return: self
            For chaining purposes.
        '''
        self._args = args, keyargs
        return self
    
    def schedule(self, omniOrCall):
        '''
        Schedule a omni event or call.
        
        @param omniOrCall: Omni|Callable
            The omni event or callable object to be scheduled.
        '''
        if isinstance(omniOrCall, Omni):
            pass
    
# --------------------------------------------------------------------

def doOmni(omni):
    '''
    Dispatches the omni event.
    '''
    assert isinstance(omni, Omni), 'Invalid omni event %s' % omni
    handlers, exclude, args, name = omni._handlers, omni._exclude, omni._args, omni._nameResolver
    handlerFunction = _handlerFunction
    while handlers:
        handler = handlers.popleft()
        if id(handler) in exclude: continue
        functions = handlerFunction(handler.__class__)
        
        function = functions.get(_PREFIX_RESOLVER)
        if function is not None:
            if args: function(handler, omni, *args[0], **args[1])
            else: function(handler, omni)
            
        function = functions.get(name)
        if function is not None:
            if args: function(handler, omni, *args[0], **args[1])
            else: function(handler, omni)

# --------------------------------------------------------------------
        
_CACHE_FUNCTIONS = {}

def _handlerFunction(clazz):
    '''
    !!!FOR INTERNAL USE ONLY.
    Provides the functions map for the provided handler class.
    '''
    methods = _CACHE_FUNCTIONS.get(clazz)
    if methods is None:
        methods = {name:getattr(clazz, name) for name in dir(clazz) 
                   if name.startswith(_PREFIX_RESOLVER) and isinstance(getattr(clazz, name), Callable)}
        _CACHE_FUNCTIONS[clazz] = methods
    return methods

