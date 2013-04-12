'''
Created on Jan 8, 2013

@package: ally base
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the setup calls implementations for the IoC module.
'''

from ..error import SetupError, ConfigError
from ..impl.priority import Priority
from ._assembly import Assembly
from ._entity import Initializer
from functools import partial
from inspect import isclass, isgenerator
from itertools import chain
import logging

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

class WithListeners:
    '''
    Provides support for listeners to be notified of the call process.
    '''

    def __init__(self):
        '''
        Constructs the listener support.
        '''
        self._listenersBefore = []
        self._listenersAfter = []
        
    def validateAcceptListeners(self):
        '''
        Method to be overridden used to validate if listeners can still be added. The method needs to raise a
        SetupError in case of listeners not allowed.
        '''

    def addBefore(self, listener, auto):
        '''
        Adds a before listener.
        
        @param listener: Callable
            A callable that takes no parameters that will be invoked before the call is processed.
        @param auto: boolean
            Flag indicating that the call of the listener should be auto managed by the called.
        '''
        assert callable(listener), 'Invalid listener %s' % listener
        assert isinstance(auto, bool), 'Invalid auto flag %s' % auto
        self.validateAcceptListeners()
        self._listenersBefore.append((listener, auto))

    def addAfter(self, listener, auto):
        '''
        Adds an after listener.
        
        @param listener: Callable
            A callable that takes no parameters that will be invoked after the call is processed.
        @param auto: boolean
            Flag indicating that the call of the listener should be auto managed by the called.
        '''
        assert callable(listener), 'Invalid listener %s' % listener
        assert isinstance(auto, bool), 'Invalid auto flag %s' % auto
        self.validateAcceptListeners()
        self._listenersAfter.append((listener, auto))

class WithCall:
    '''
    Provides support for calls that are wrapped around another call.
    '''

    def __init__(self, call):
        '''
        Construct the with call support.
        
        @param call: Callable
            The call that is used by this Call in order to resolve.
        '''
        self.call = call

    def setCall(self, call):
        '''
        Sets the call for this Call.
        
        @param call: Callable
            The call that is used by this Call in order to resolve.
        '''
        assert callable(call), 'Invalid callable %s' % call
        self._call = call

    call = property(lambda self: self._call, setCall, doc=
'''
@type call: Callable
    The call used for resolve.
''')

class WithType:
    '''
    Provides support for calls that have a type.
    '''

    def __init__(self, types):
        '''
        Construct the type support.
        
        @param types: Iterable[class]|None
            The type(s) of the value.
        '''
        self.types = types
        
    def setType(self, types):
        '''
        Sets the types.
        
        @param types: Iterable[class]|None
            The type(s) of the value.
        '''
        if types is not None: types = tuple(types)
        else: types = ()
        if __debug__:
            for clazz in types: assert isclass(clazz), 'Invalid type class %s' % clazz
        self._types = types

    types = property(lambda self: self._types, setType, doc=
'''
@type types: Iterable[class]|None
    The type(s) of the value.
''')
        
    def isOf(self, clazz):
        '''
        Checks if the provided type is compatible with the provided type.
        
        @param clazz: class
            The class to check.
        @return: boolean
            True if is of class type, False otherwise.
        '''
        assert isclass(clazz), 'Invalid class %s' % clazz
        for typ in self._types:
            if clazz == typ or issubclass(typ, clazz): return True
        return False

    def validate(self, value):
        '''
        Validates the provided value against the source type.
        
        @param value: object   
            The value to check.
        @return: object
            The same value as the provided value.
        @raise SetupError: In case the value is not valid.
        '''
        if self._types and value is not None:
            for clazz in self._types:
                if not isinstance(value, clazz):
                    raise SetupError('Invalid value provided \'%s\', expected to be instance of all types %s' % 
                                     (value, self._types))
        return value

# --------------------------------------------------------------------

class CallEvent(WithCall, WithListeners):
    '''
    Provides the event call.
    @see: Callable, WithCall, WithListeners
    '''

    def __init__(self, assembly, name, call):
        '''
        Construct the event call.
        
        @param assembly: Assembly
            The assembly to which this call belongs.
        @param name: string
            The event name.
            
        @see: WithCall.__init__
        @see: WithListeners.__init__
        '''
        assert isinstance(assembly, Assembly), 'Invalid assembly %s' % assembly
        assert isinstance(name, str), 'Invalid name %s' % name
        WithCall.__init__(self, call)
        WithListeners.__init__(self)

        self.assembly = assembly
        self.name = name
        self._processed = False

    def validateAcceptListeners(self):
        '''
        @see: WithListeners.validateAcceptListeners
        '''
        if self._processed: raise SetupError('Already processed cannot add anymore listeners to \'%s\'' % self.name)
 
    def __call__(self):
        '''
        Provides the call for the source.
        '''
        if self._processed: return
        self._processed = True
        self.assembly.called.add(self.name)

        for listener, _auto in self._listenersBefore: listener()
        ret = self.call()
        if ret is not None: raise SetupError('The event call \'%s\' cannot return any value' % self.name)
        for listener, _auto in self._listenersAfter: listener()
        
class CallEventOnCount(CallEvent):
    '''
    Event call that triggers only after being called count times.
    @see: CallEvent
    '''

    def __init__(self, assembly, name, call, count):
        '''
        Construct the call on count event.
        @see: CallEvent.__init__
        
        @param count: integer
            The number of calls that the event needs to be called in order to actually trigger.
        '''
        assert isinstance(count, int) and count > 0, 'Invalid count %s' % count
        super().__init__(assembly, name, call)
        
        self._count = count

    def __call__(self):
        '''
        Provides the call for the source.
        '''
        if self._count > 0: self._count -= 1
        if self._count <= 0: super().__call__()

class CallEntity(WithCall, WithType, WithListeners):
    '''
    Call that resolves an entity setup.
    @see: Callable, WithCall, WithType, WithListeners
    '''

    def __init__(self, assembly, name, call, types=None):
        '''
        Construct the entity call.
        
        @param assembly: Assembly
            The assembly to which this call belongs.
        @param name: string
            The entity name.
        
        @see: WithCall.__init__
        @see: WithType.__init__
        @see: WithListeners.__init__
        '''
        assert isinstance(assembly, Assembly), 'Invalid assembly %s' % assembly
        assert isinstance(name, str), 'Invalid name %s' % name
        WithCall.__init__(self, call)
        WithType.__init__(self, types)
        WithListeners.__init__(self)

        self.marks = []

        self.assembly = assembly
        self.name = name
        self._hasValue = False
        self._processing = False
        self._interceptors = []
        
    def validateAcceptListeners(self):
        '''
        @see: WithListeners.validateAcceptListeners
        '''
        if self._hasValue:
            raise SetupError('Already used cannot add anymore listeners to \'%s\'' % self.name)

    def addInterceptor(self, interceptor):
        '''
        Adds a value interceptor. A value interceptor is a Callable object that takes as the first argument the entity
        value and as the second value the follow up Callable of the value and returns the value for the entity and the
        new follow up.
        
        @param interceptor: Callable(object, Callable)
            The interceptor.
        '''
        assert callable(interceptor), 'Invalid interceptor %s' % interceptor
        self._interceptors.append(interceptor)

    def __call__(self):
        '''
        Provides the call for the entity.
        '''
        if not self._hasValue:
            if self._processing:
                raise SetupError('Cyclic dependency detected for \'%s\', try using yield' % self.name)
            self._processing = True
            self.assembly.called.add(self.name)

            ret = self.call()

            if isgenerator(ret): value, followUp = next(ret), partial(next, ret, None)
            else: value, followUp = ret, None

            if value is not None:
                valueId, callsOfValue = id(value), self.assembly.callsOfValue
                calls = callsOfValue.get(valueId)
                if calls is None: callsOfValue[valueId] = calls = [self]
                else: calls.append(self)
            else: valueId = None

            assert log.debug('Processed entity \'%s\' with value %s', self.name, value) or True
            v = self.validate(value)
            for inter in self._interceptors:
                try: v, followUp = inter(v, followUp)
                except: raise SetupError('Problems for interceptor %s' % inter)

            self._hasValue = True
            self._value = v

            for listener, _auto in self._listenersBefore: listener()

            if followUp: followUp()

            if valueId:
                calls.pop()
                if len(calls) == 0:
                    Initializer.initialize(value)
                    del callsOfValue[valueId]

            for listener, _auto in self._listenersAfter: listener()

            assert log.debug('Finalized %r with value %s', self.name, value) or True
        return self._value

class CallConfig(WithType, WithListeners):
    '''
    Call that delivers a value.
    @see: Callable, WithType, WithListeners
    '''

    def __init__(self, assembly, name, types=None):
        '''
        Construct the configuration call.
        
        @param assembly: Assembly
            The assembly to which this call belongs.
        @param name: string
            The configuration name.
        @param value: object
            The value to deliver.
            
        @see: WithType.__init__
        @see: WithListeners.__init__
        '''
        WithType.__init__(self, types)
        WithListeners.__init__(self)

        self.assembly = assembly
        self.name = name
        self.external = False
        self._hasValue = False
        self._processed = False
        
    def validateAcceptListeners(self):
        '''
        @see: WithListeners.validateAcceptListeners
        '''
        if self._processed: raise SetupError('Already processed cannot add anymore listeners to \'%s\'' % self.name)

    def setValue(self, value):
        '''
        Sets the value to deliver.
        
        @param value: object
            The value to deliver.
        '''
        if isinstance(value, Exception):
            self._value = value
        else:
            self._value = self.validate(value)
            self._hasValue = True

    hasValue = property(lambda self: self._hasValue, doc=
'''
@type hasValue: boolean
    True if the configuration has a value.
''')
    value = property(lambda self: self._value, setValue, doc=
'''
@type value: object
    The value to deliver.
''')

    def __call__(self):
        '''
        Provides the call for the entity.
        '''
        if not self._processed:
            self._processed = True
            self.assembly.called.add(self.name)
            for listener, auto in chain(self._listenersBefore, self._listenersAfter):
                if auto:
                    if not self.external: listener() 
                    # We only call the listeners if the configuration was not provided externally
                else: listener()
        if isinstance(self._value, Exception): raise self._value
        if not self._hasValue: raise ConfigError('No value for configuration %s' % self.name)
        return self._value

class CallStart(CallEvent):
    '''
    Provides the start call event.
    @see: Callable
    '''
    
    def __init__(self, assembly, name, call, priority):
        '''
        Construct the start call.
        @see: CallEvent.__init__
        
        @param priority: Priority
            The priority of the start call.
        '''
        assert isinstance(priority, Priority), 'Invalid priority %s' % priority
        super().__init__(assembly, name, call)
        
        self.priority = priority

class CallEventControlled(WithCall, WithListeners):
    '''
    Provides the controlled event call. This calls can be managed externally depending on the event names.
    @see: Callable, WithCall, WithListeners
    '''

    def __init__(self, assembly, name, priority, call, triggers):
        '''
        Construct the controlled event call.
        
        @param assembly: Assembly
            The assembly to which this call belongs.
        @param name: string
            The controlled event name.
        @param priority: Priority
            The event priority.
        @param triggers: set{ITrigger}
            The triggers to be associated with the event call.
            
        @see: WithCall.__init__
        @see: WithListeners.__init__
        '''
        assert isinstance(assembly, Assembly), 'Invalid assembly %s' % assembly
        assert isinstance(name, str), 'Invalid name %s' % name
        assert isinstance(priority, Priority), 'Invalid priority %s' % priority
        assert isinstance(triggers, set), 'Invalid triggers %s' % triggers
        if __debug__:
            from ..event import ITrigger
            for trigger in triggers: assert isinstance(trigger, ITrigger), 'Invalid trigger %s' % trigger
        WithCall.__init__(self, call)
        WithListeners.__init__(self)

        self.assembly = assembly
        self.priority = priority
        self.name = name
        self.triggers = triggers
        self._processed = False
        
    def addBefore(self, listener, auto):
        '''
        @see: WithListeners.addBefore
        '''
        raise SetupError('Cannot add before event to the \'%s\' controlled event, only after events are allowed' % self.name)

    def validateAcceptListeners(self):
        '''
        @see: WithListeners.validateAcceptListeners
        '''
        if self._processed: raise SetupError('Already processed cannot add anymore listeners to \'%s\'' % self.name)
 
    def __call__(self):
        '''
        Provides the call for the source.
        '''
        if self._processed:
            return self._value
        self._processed = True
        self.assembly.called.add(self.name)

        try: self._value = self.call()
        except:
            log.exception('A problem occurred for controlled event: %s' % self.name)
            self._value = False
        if self._value is None: self._value = True
        if not isinstance(self._value, bool):
            raise SetupError('The controlled event call \'%s\' needs to return a boolean value, got \'%s\'' % 
                             (self.name, self._value))
        if self._value:
            for listener, _auto in self._listenersAfter: listener()
        return self._value
