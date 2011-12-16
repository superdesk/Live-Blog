'''
Created on Dec 11, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Module that contains the omni event handling. Basically is just a framework that allows event dispatching based on class
defined methods. As an example we have:

class A:

    @omni.resolver
    def doSomething(self, condition):
        if condition:
            return 'Heloo'
        return omni.CONTINUE

@omni.source('children', 'parent')
class B:

    def __init__(self):
        self.parent = None
        self.children = []
    
    @omni.resolver
    def start(self):
        self.doSomething(True, omniClosest=True)

The class A has an event method 'doSomething' that is decorated with delegate, the class B is decorated as having the 
sources of event delivery in the attributes children and parent (this attributes are read by using the getattr function)
and also an event delegate method 'start'. In the 'start' method an attempt is made to call the 'doSomething' method
on class B which has not implemented it, in this case because the class B has declared some resources for delegation
it will investigate those sources for a 'doSomething' method, so if we do something like:

b = B()
b.children.append(A())
b.start()

>> 'Heloo'

'''

from _abcoll import Iterable, Callable
from functools import partial, update_wrapper
from inspect import isfunction, getfullargspec, isclass
import inspect
import logging
from ally.util import Attribute

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------
# Isolations

ISOLATION_NONE = 0
# Specifies that the resolver should not be isolated when resolving, meaning that the resolver method will be called
# every time that is an event for it. !!!Attention this isolation can lead to infinite loops.

ISOLATION_RESOLVER = 1
# Specifies that same resolver method can not be called twice on the same instance.
# !!!Attention this isolation can lead to unpredictable behavior.

ISOLATION_INSTANCE = 2
# Specifies that if a instance is in the process of resolving it will not accept any other events.

ISOLATIONS = {'none':ISOLATION_NONE, 'resolver':ISOLATION_RESOLVER, 'instance':ISOLATION_INSTANCE}

# --------------------------------------------------------------------
# Flags

F_FIRST = 1
# Flag indicating that the omni event should stop at the first resolver. If this flag is used an there is no resolve for
# the event than a OmniError is raised.

F_FARTHEST = 2
# Flag indicating that the omni event should be dispatched starting with the farthest resolvers.

F_SOURCE = 4
# Flag indicating that the search should be made only on the event source.

F_CHILDREN = 16
# Flag indicating that the search should be made only on the direct children of the event source, the dispatch will not
# be made directly on the event source.

F_LOCAL = 32
# Flag indicating that the search should be made only on the local nodes, basically the breidges will not be used.

# --------------------------------------------------------------------
# Markers

CONTINUE = object()
# An object used as a marker when a delegated function cannot handle the provided data and wants the omni event
# dispatching to continue.

# --------------------------------------------------------------------

_ARGUMENT_OMNI = 'omni'
# The name of the argument used to indicate omni event behavior.

# --------------------------------------------------------------------

def resolver(*args, isolation='instance'):
    '''
    Used for decorating the methods to be declared as resolvers for omni event dispatching. A resolver needs to always
    return a not None value.
    
    @param isolation: string
        The isolation level of the resolver when is being executed, one of:
        
        'none': Specifies that the resolver should not be isolated when resolving, meaning that the resolver method 
                will be called every time that is an event for it. !!!Attention this isolation can lead to infinite
                loops.
                
        'resolver': Specifies that same resolver method can not be called twice on the same instance.
        
        'instance': Specifies that if a instance is in the process of resolving it will not accept any other events.
    '''
    if not args: return partial(resolver, isolation=isolation)
    assert len(args) == 1, 'Expected only one argument that is the decorator function, got %s arguments' % len(args)
    function = args[0]
    assert isolation in ISOLATIONS, 'Invalid isolation %s' % isolation
    assert isfunction(function), 'Expected a function as the argument, got %s' % function
    fnArgs = getfullargspec(function)
    if _ARGUMENT_OMNI in fnArgs.args:
        raise OmniError('Cannot use argument name %r in function %s because is reserved' % (_ARGUMENT_OMNI, function))
    return _bindResolver(Resolver(function, ISOLATIONS[isolation]))

def source(*names):
    '''
    Used for decorating the classes that have sources of delegation. 
    '''
    return partial(_bindSources, sources=names)

def bridge(*args):
    '''
    Used for decorating the methods to be declared as bridges for omni event dispatching. 
    
    -Unlike the resolver the bridge is always resolved regardless of the event.
    -Bridges are only interrogated if the event call is flagged with BRIDGE.
    -All bridges that are found while resolving are invoked.
    -The bridge is resolved last even if the FARTHEST flag is provided for the event call.
    -The bridge needs to provide an object or list of objects to use as sources, None|CONTINUE if it decides no 
     sources are available.
    '''
    if not args: return bridge
    assert len(args) == 1, 'Expected only one argument that is the decorator function, got %s arguments' % len(args)
    function = args[0]
    assert isfunction(function), 'Expected a function as the argument, got %s' % function
    fnArgs = getfullargspec(function)
    if fnArgs.args == ('self'):
        raise OmniError('The bridge function %r is not allowed any arguments' % function)
    return _bindResolver(Bridge(function))
    
# --------------------------------------------------------------------

class OmniError(Exception):
    '''
    Exception thrown when there is a omni event problem.
    '''

class NoResultError(Exception):
    '''
    Exception thrown when there is no result available whenever using the F_FIRST flag.
    '''
    
_CALLER_STACK = []
# The calls stack for event dispatching.

_RESOLVE_STACK = []
# The resolve stack for event dispatching.

class Call(Callable):
    '''
    Wraps an omni event call to an omni resolver.
    '''
    
    __slots__ = ['source', 'name']
    
    def __init__(self, source, name):
        '''
        Constructs the event.
        
        @param source: object
            The source instance of the event.
        @param name: string
            The event name.
        '''
        assert source is not None, 'An source instance is required'
        assert isinstance(name, str), 'Invalid resolver event name %s' % name
        self._source = source
        self._name = name
        
    def __call__(self, *args, **keyargs):
        '''
        @see: Callable.__call__
        '''
        return _dispatchEvent(self._source, self._name, args, keyargs)
    
    def __repr__(self):
        '''
        @see: http://docs.python.org/reference/datamodel.html
        '''
        l = [self.__class__.__name__, '[name=', self._name, ', source=', self._source, ']']
        return ''.join(str(v) for v in l)

class Resolve:
    '''
    Class used to keep data related to a event resolve.
    '''
    
    __slots__ = ['source', 'name', 'args', 'keyargs', 'flgFirst', 'flgFarthest', 'flgLocal', 'flgSource', 'flgChildren',
                 'exclude', 'isFound', 'isResolved', 'isLocal']
    
    def __init__(self, source, name, args, keyargs, flags=0):
        '''
        Construct a new resolve.
        
        @param source: object
            The source instance of the event.
        @param name: string
            The event name.
        @param args, keyargs: arguments
            The arguments to use as event data.
        @param flags: integer
            The flags of the resolve.
        @ivar exclude: list[object]
            A list with the instances to be excluded.
        @ivar isFound: boolean
            True if the event has been found on at least a source.
        @ivar isResolved: boolean
            Keeps the status for the event resolve, this is useful when an event call is not dispatched with the 
            FIRST flag.
        @ivar isLocal: boolean
            True if the event is in a local context, False if the resolve is over a bridge.
        '''
        assert source is not None, 'An source instance is required'
        assert isinstance(name, str), 'Invalid resolver event name %s' % name
        self.source = source
        self.name = name
        self.args = args
        self.keyargs = keyargs
        
        self.flgFirst = bool(flags & F_FIRST)
        self.flgFarthest = bool(flags & F_FARTHEST)
        self.flgSource = bool(flags & F_SOURCE)
        self.flgChildren = bool(flags & F_CHILDREN)
        self.flgLocal = bool(flags & F_LOCAL) or self.flgChildren or self.flgSource
        
        self.exclude = []
        
        self.isFound = False
        self.isResolved = False
        self.isLocal = True
        
    def __repr__(self):
        '''
        @see: http://docs.python.org/reference/datamodel.html
        '''
        l = [self.__class__.__name__, '[name=', self.name, ', source=', self.source, ']']
        return ''.join(str(v) for v in l)

class Resolver:
    '''
    Descriptor class that provides resolving for omni event dispatching through the use of resolving functions.
    '''
    
    def __init__(self, function, isolation):
        '''
        Constructs the delegate for the provided function.
        
        @param function: function
            The delegate function.
        @param isolation: integer
            @see: resolver
        '''
        assert isfunction(function), 'Invalid function %s' % function
        assert isinstance(isolation, int), 'Invalid isolation %s' % isolation
        self._function = function
        self._isolation = isolation
        self._handler = None
        update_wrapper(self, function)
    
    def setHandler(self, handler):
        '''
        Set the handler for this resolver.
        
        @param handler: Handler
            The handler for the resolver.
        '''
        assert isinstance(handler, Handler), 'Invalid handler %s' % handler
        assert not self._handler, 'There is already a handler for this %s resolver' % self
        self._handler = handler
        handler.addResolver(self)
        
    def getHandler(self):
        '''
        Provides the handler of this resolver.
        
        @return: Handler
            The handler.
        '''
        assert self._handler, 'There is no handler assigned to this resolver, maybe you forgot to decorate the '\
        'containing class with the @handler decorator'
        return self._handler

    name = property(lambda self: self._function.__name__, doc=
'''
@type name: string
    The resolver name.
''')
    isolation = property(lambda self: self._isolation, doc=
'''
@type isolation: integer
    The resolver isolation.
''')
    handler = property(getHandler, setHandler, doc=
'''
@type handler: Handler
    The handler of the resolver.
''')
    
    def resolve(self, instance, args, keyargs):
        '''
        Invokes the delegate function with the provided arguments and key arguments.
        
        @param instance: object
            The instance of the function method.
        @param args, keyargs: arguments
            The arguments to invoke the function with.
        @return: object
            The resolved value.
        '''
        assert instance is not None, 'An instance is required'
        try: return self._function(instance, *args, **keyargs)
        except TypeError:
            raise TypeError('Problems invoking function %s with arguments %s' % (self._function, (args, keyargs)))
    
    def __get__(self, instance, owner):
        '''
        @see: http://docs.python.org/reference/datamodel.html
        '''
        if instance is not None: return _createEventCall(instance, self._function.__name__)
        return self
    
    def __repr__(self):
        '''
        @see: http://docs.python.org/reference/datamodel.html
        '''
        l = [self.__class__.__name__, ':', self._function.__name__, '-', self._handler]
        return ''.join(str(v) for v in l)

class Bridge(Resolver):
    '''
    @see: Resolver
    Provides a bridge.
        -Unlike the resolver the bridge is always resolved regardless of the event.
        -All bridges that are found while resolving are invoked.
        -The bridge is resolved last even if the FARTHEST flag is provided for the event call.
        -The bridge needs to provide an object or list of objects to use as sources, None if it decides no sources are
         available.
    '''
    
    def __init__(self, function):
        '''
        @see: Resolver.__init__
        '''
        Resolver.__init__(self, function, True)

class Handler:
    '''
    Provides the handling for resolvers.
    '''
        
    def __init__(self):
        '''
        Construct the handler.
        '''
        self._sources = []
        self._resolvers = {}
        
    def addSource(self, source):
        '''
        Adds a new source of handlers to this handler.
        
        @param source: string
            The source attribute name for the handlers.
        '''
        assert isinstance(source, str), 'Invalid source attribute name %s' % source
        if source not in self._sources: self._sources.append(source)

    def addResolver(self, resolver):
        '''
        Adds a new resolver to this handler.
        
        @param resolver: Resolver
            The resolver to be added.
        '''
        assert isinstance(resolver, Resolver), 'Invalid resolver %s' % resolver
        assert resolver.name not in self._resolvers, \
        'The resolver name %s is already in this %s handler' % (resolver.name, self)
        self._resolvers[resolver.name] = resolver
       
    def __repr__(self):
        '''
        @see: http://docs.python.org/reference/datamodel.html
        '''
        l = [self.__class__.__name__, '[']
        l.append(', '.join(self._sources))
        l.append(']')
        return ''.join(str(v) for v in l)

# --------------------------------------------------------------------

def origin(default=None):
    '''
    Provides the origin instance for the current ongoing event.
    
    @param default: object
        The default object to use if there is no event origin.
    @return: object
        The instance source of the current ongoing event.
    @raise ValueError: if there is no ongoing event and no default has been provided.
    '''
    if _RESOLVE_STACK: return _RESOLVE_STACK[-1].source
    if default is not None: return default
    raise ValueError('There is no ongoing event')

def event():
    '''
    Provides the ongoing event name.
    
    @return: string
        The current ongoing event name.
    @raise ValueError: if there is no ongoing event.
    '''
    if _RESOLVE_STACK: return _RESOLVE_STACK[-1].name
    raise ValueError('There is no ongoing event')

def resolved():
    '''
    Provides the resolved status of the ongoing event.
    
    @return: boolean
        True if the ongoing event is resolved, False otherwise.
    @raise ValueError: if there is no ongoing event.
    '''
    if _RESOLVE_STACK: return _RESOLVE_STACK[-1].isResolved
    raise ValueError('There is no ongoing event')

def local():
    '''
    Provides the local status of the ongoing event.
    
    @return: boolean
        True if the ongoing event is resolved, False otherwise.
    @raise ValueError: if there is no ongoing event.
    '''
    if _RESOLVE_STACK: return _RESOLVE_STACK[-1].isLocal
    raise ValueError('There is no ongoing event')

def change(*args, **keyargs):
    '''
    Used for changing the current event data. Basically you will change the arguments and key arguments that the event
    has been invoked with.
    
    @param args, keyargs: arguments
        The arguments to use as event data.
    @raise ValueError: if there is no ongoing event.
    '''
    if _RESOLVE_STACK:
        resolve = _RESOLVE_STACK[-1]
        assert isinstance(resolve, Resolve)
        resolve.args = args
        resolve.keyargs = keyargs
    else: raise ValueError('There is no ongoing event')

# --------------------------------------------------------------------

ATTR_HANDLER = Attribute(__name__, 'handler', Handler)
# The attribute for the handler.

def _handlerOf(instance):
    '''
    Provides the handler that is directly associated with an instance.
    
    @param instance: object|class
        The object instance or class to get the handler from.
    @return: Handler|None
        The handler found or None.
    '''
    assert instance is not None, 'An instance is required'
    if isclass(instance): clazz = instance
    else: clazz = instance.__class__
    return ATTR_HANDLER.get(clazz, None)

def _bindResolver(resolver):
    '''
    Binds the resolver to the locals.
    
    @param resolver: Resolver
        The resolver to be binded to locals.
    @return: Resolver
        The provided resolver.
    '''
    assert isinstance(resolver, Resolver), 'Invalid resolver %s' % resolver
    callerLocals = inspect.stack()[2][0].f_locals # Provides the locals from the calling class
    if ATTR_HANDLER.hasDict(callerLocals): handler = ATTR_HANDLER.getDict(callerLocals)
    else: handler = ATTR_HANDLER.setDict(callerLocals, Handler())
    resolver.handler = handler
    return resolver

def _bindSources(clazz, sources):
    '''
    Binds the sources to the provided class.
    
    @param clazz: class
        The class to bind the sources to.
    @param sources: list[string]|tuple[string]
        The list of source names to add to the instance handler.
    @return: class
        The provided instance.
    '''
    assert isclass(clazz), 'Invalid class %s' % clazz
    assert isinstance(sources, (list, tuple)), 'Invalid sources %s' % sources
    assert sources, 'Invalid sources %s, they do not contain any name' % sources
    handler = _handlerOf(clazz)
    if not handler: handler = ATTR_HANDLER.set(clazz, Handler())
    for src in sources: handler.addSource(src)
    setattr(clazz, '__getattr__', _createEventCall)
    return clazz

def _createEventCall(source, name):
    '''
    Creates a new event call for the provided instance and name.
    
     @param source: object
        The source instance to create event for.
    @param name: string
        The name of the event resolver.
    '''
    assert source is not None, 'An source instance is required'
    assert isinstance(name, str), 'Invalid name %s' % name
    return Call(source, name)

def _generateCalls(instances, name, resolve):
    #TODO: add a better handling to overiden resolvers.
    '''
    Generator method that provides the calls for the name and the provided instance.
    
    @param instances: list[object]
        The instances to provide the resolvers for.
    @param name: string
        The name of the event resolver.
    @param resolve: Resolve
        The resolve to generate the calls for.
    @yeilds: Resolver, object
        The instance and the resolver
    '''
    assert isinstance(instances, list), 'Invalid source instances list %s' % instances
    assert isinstance(name, str), 'Invalid name %s' % name
    assert isinstance(resolve, Resolve), 'Invalid resolve %s' % resolve
    
    excludeSource = resolve.flgChildren and not resolve.flgSource
    addChildren = True
    
    processed = []
    while instances:
        obj = instances.pop(0)
        processed.append(obj)
        clazzes = [obj.__class__]
        foundHandler = False
        sources = []
        bridges = []
        while clazzes:
            clazz = clazzes.pop(0)
            if clazz == object: continue
            handler = _handlerOf(clazz)
            if handler:
                assert isinstance(handler, Handler)
                for bridgeName, bridge in handler._resolvers.items():
                    if isinstance(bridge, Bridge):
                        if bridgeName not in bridges: bridges.append(bridgeName)
                sources.extend(src for src in handler._sources if src not in sources)
                foundHandler = True
            clazzes.extend(clazz.__bases__)
        assert foundHandler, 'Invalid instance %s has no handlers on it' % obj
        
        if obj not in resolve.exclude:
            while bridges:
                bridge = getattr(obj.__class__, bridges.pop(0), None)
                if isinstance(bridge, Bridge): yield bridge, obj
            
            resolver = getattr(obj.__class__, name, None)
            if isinstance(resolver, Resolver):
                resolve.isFound = True
                if not excludeSource: yield resolver, obj
                else:
                    assert log.debug('Not used %s for %r because it was the source, and the source was excluded',
                                     obj, name) or True
        else:
            assert log.debug('Not used %s for %r because it was in the excluded list' , obj, name) or True
        excludeSource = False
        if resolve.flgSource and not resolve.flgChildren: break
        if addChildren:
            for src in sources:
                assert hasattr(obj, src), \
                'There is no attribute %r for instance %s to get the omni event sources' % (src, obj)
                value = getattr(obj, src)
                if isinstance(value, Iterable):
                    for v in value:
                        if v not in processed: instances.append(v)
                elif value is not None and value not in processed: instances.append(value)
        if resolve.flgChildren: addChildren = False

def _dispatchCall(call, args, keyargs):
    '''
    Dispatches the call.
    
    @param call: tuple(Resolver, object)
        The tuple containing the resolver and resolver instance to dispatch with.
    @param args, keyargs: arguments
        The arguments to use as call argument.
    @return: object
        The call return value.
    '''
    resolver, instance = call
    assert isinstance(resolver, Resolver)
    
    if resolver.isolation == ISOLATION_INSTANCE:
        for c in _CALLER_STACK:
            if c[1] == instance:
                assert log.debug('Not invoked %s with %r because is instance isolated and the instance is already '
                                 'handling another event %r', instance, resolver.name, c[0].name) or True
                return CONTINUE
    elif resolver.isolation == ISOLATION_RESOLVER:
        if call in _CALLER_STACK:
            assert log.debug('Not invoked %s with %r because is resolver isolated and the instance is already handling '
                             'the same event', instance, resolver.name) or True
            return CONTINUE
        
    _CALLER_STACK.append(call)
    try:
        assert log.debug('Invoked %s on %r with argument %s and key arguments %s', instance, resolver.name, args,
                         keyargs) or True
        return resolver.resolve(instance, args, keyargs)
    finally: _CALLER_STACK.pop()

def _dispatchEvent(source, name, args, keyargs):
    '''
    Dispatches the event call.
    
    @param source: object
        The source instance of the event.
    @param name: string
        The event name.
    @param args, keyargs: arguments
        The arguments to use as event data.
    @return: list[object]|object
        The dispatch return values.
    '''
    assert isinstance(name, str), 'Invalid resolver name %s' % name
    assert source is not None, 'An source instance is required'
    
    flags = keyargs.pop(_ARGUMENT_OMNI, 0)
    resolve = Resolve(source, name, args, keyargs, flags)
    _RESOLVE_STACK.append(resolve)
    
    try:
        assert log.debug('Dispatching event %s with %s', name, resolve) or True
        
        returns, sources = [], [source]
        while sources:
            calls = _generateCalls(sources, name, resolve)
            if resolve.flgFarthest:
                calls = list(calls)
                calls.reverse()
            sources = []
            
            bridgeCalls = []
            for call in calls:
                if isinstance(call[0], Bridge):
                    bridgeCalls.append(call)
                    continue
                assert log.debug('Invoking %s', call) or True
                ret = _dispatchCall(call, resolve.args, resolve.keyargs)
                if ret is not CONTINUE:
                    if ret is None: raise OmniError('None is not a valid return value for %r in %s' % call)
                    resolve.isResolved = True
                    if resolve.flgFirst: return ret
                    else: returns.append(ret)
            
            if not resolve.flgLocal:
                resolve.isLocal = False
                for bridge in bridgeCalls:
                    ret = _dispatchCall(bridge, [], {})
                    if ret is not CONTINUE and ret is not None:
                        if isinstance(ret, Iterable):
                            for src in ret:
                                if src not in sources: sources.append(src)
                        else: sources.append(ret)
            else:
                assert log.debug('Not invoking bridges for %s because is a local call', resolve.name) or True
        
        assert log.debug('Finalized event %s with %r', name, resolve) or True
        if not resolve.isFound:
            raise OmniError('Could not find any resolvers for %r called from %s' % (name, source))
        if resolve.flgFirst and not resolve.isResolved:
            assert log.debug('No result obtained for %r(args=%s, keyargs=%s) called from %s', name, args, keyargs,
                             source) or True
            raise NoResultError
    finally: _RESOLVE_STACK.pop()
    return returns
