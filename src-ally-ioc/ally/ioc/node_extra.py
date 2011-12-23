'''
Created on Dec 8, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Module containing the nodes for the IoC setup events.
'''

from .node import SetupError, isConfig, PREFIX_CONFIG, IListener, \
    argumentsFor, argumentsPush, ICondition, Node, extractArguments
from _abcoll import Callable
from inspect import isfunction
import logging

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

TARGET_EVENT = 'event'
TARGET_CONDITION = 'condition'
TARGET_REPLACE = 'replace'

# Event Nodes
# --------------------------------------------------------------------

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

class EventOnReference(Woman, IListener):
    '''
    @see: Node
    Provides the event delivering for nodes that respect the event reference.
    '''
    
    def __init__(self, name, event, call, arguments=None, reference=None, multiple=None):
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
        @param multiple: boolean|None
            True indicates that the event is allowed to be handled multiple times, False the event should be handled just
            once and None allows the event handler to provide a default behavior based on the reference
            (True for entities, False for configurations)
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
        if multiple is not None:
            assert isinstance(multiple, bool), 'Invalid multiple flag %s' % multiple
            self._multiple = multiple
        else: self._multiple = isConfig(reference)
            
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
    def doAssemble(self, target):
        '''
        Assembles this event.
        
        @param target: string
            The assembling target.
        '''
        if target != TARGET_EVENT: return omni.CONTINUE
        if not self._reference: raise SetupError('The event has no reference specified')
        paths = self.doAddListener(self, self._reference)
        if len(paths) > 1: raise SetupError('To many paths %s found for reference %r' % (paths, self._reference))
        return self._path
    
    @omni.resolver
    def doEvent(self, *criteria):
        '''
        Handle the node event if the criteria matches.
        
        @param criteria: arguments
            The criteria(s) used to identify the node. If no criteria is provided than the event is considered valid for
            all nodes.
        @return: True
            If the event was handled by this node.
        '''
        if not self._isMatched(criteria) or not self._isChecked(): return omni.CONTINUE
        if self.doIsValue(self._path, omni=omni.F_FIRST):
            if not self._multiple: raise SetupError('The event %s cannot be dispatched twice' % self)
        else: self.doSetValue(self._path, True)
        keyargs = extractArguments(self, self._arguments)
        self._listenersBefore()
        self._listenersAfter(self._call(**keyargs))
        
        assert log.debug('Processed the referenced event %s', self) or True
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
        
    def before(self, source):
        '''
        @see: IListener.before
        '''
        if self._event == EVENT_BEFORE and self._isChecked(): self.doEvent(self._path)
        
    def after(self, source, result):
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
        if self._isMatched(criteria) and self._isChecked():
            if self.doIsValue(self._path, omni=omni.F_FIRST):
                raise SetupError('The event %s cannot be dispatched twice' % self)
            self.doSetValue(self._path, True)
            keyargs = extractArguments(self, self._arguments)
            self._listenersBefore()
            self._listenersAfter(self._call(**keyargs))
            assert log.debug('Processed the start event %s', self) or True
        return self._path

# --------------------------------------------------------------------

def eventReferencedFrom(function, event, name=None, reference=None, multiple=None):
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
    @param multiple: boolean|None
        True indicates that the event is allowed to be handled multiple times, False the event should be handled just
        once and None allows the event handler to provide a default behavior based on the reference
        (True for entities, False for configurations)
    @return: EventOnReference
        The converted EventOnReference.
    '''
    assert name is None or isinstance(name, str), 'Invalid name %s' % name

    assert isfunction(function), 'Invalid function %s' % function
    name = name or function.__name__

    arguments, defaults, annotations = argumentsFor(function)
    
    if 'return' in annotations:
        raise SetupError('No return annotation expected for event function %r' % function.__name__)

    ev = EventOnReference(name, event, function, arguments, reference, multiple)
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

# Condition Nodes
# --------------------------------------------------------------------

toConditionName = lambda target, clazz: target + '$' + clazz.__name__
# Provides a condition name for the provided target and class condition.

# --------------------------------------------------------------------

class OnlyIf(Node, ICondition):
    '''
    Node that acts like an only if condition.
    '''
        
    def __init__(self, target, options):
        '''
        @see: Node.__init__
        
        @param target: string
            The target of the only if condition.
        @param options: dictionary{string, object}
            The conditional options to be considered.
        '''
        assert isinstance(target, str), 'Invalid target %s' % target
        assert isinstance(options, dict), 'Invalid options %s' % options
        Node.__init__(self, toConditionName(target, self.__class__))
        self._target = target
        self._options = options
        
    @omni.resolver      
    def doFindUnused(self, *criteria):
        '''
        Finds the node that recognizes the criteria and is considered unused.
        
        @param criteria: arguments
            The criteria(s) used to identify the node. If no criteria is provided than the event is considered valid for
            all nodes.
        @return: string
            The path of the unused condition.
        '''
        if not self._isMatched(criteria): return omni.CONTINUE
        if self.doIsValue(self._path, omni=omni.F_FIRST): return omni.CONTINUE
        return self._path
    
    @omni.resolver
    def doAssemble(self, target):
        '''
        Assembles this condition.
        
        @param target: string
            The assembling target.
        '''
        if target != TARGET_CONDITION: return omni.CONTINUE
        try: self.doAddCondition(self, self._target, omni=omni.F_FIRST)
        except omni.NoResultError: raise SetupError('Cannot locate any node for target %s' % self._target)
        return self._path
    
    def addOptions(self, options):
        '''
        Adds new options or override existing ones based on the provided options map.
        
        @param options: dictionary{string, object}
            The options dictionary.
        '''
        assert isinstance(options, dict), 'Invalid options %s' % options
        self._options.update(options)
    
    def isValid(self):
        '''
        Method invoked to check if the condition is valid for the node.
        
        @return: boolean
            True if the condition checks for the node, False otherwise.
        '''
        if not self.doIsValue(self._path, omni=omni.F_FIRST): self.doSetValue(self._path, True)
        for name, value in self._options.items():
            try: v = self.doGetValue(name, omni=omni.F_FIRST)
            except omni.NoResultError: raise SetupError('Cannot find any value for %r to solve the condition' % name)
            if value != v: return False
        return True

# Replacing Nodes
# --------------------------------------------------------------------

class Replacer(Node):
    '''
    Node that provides the replacing of another node.
    '''
        
    def __init__(self, name, replacer):
        '''
        @see: Node.__init__
        
        @param replacer: Node
            The replacer node, the name of this node will be used to find the replaced target.
            The replaced node needs to be compatible with this node meaning that:
                isinstance(replaced, replacer.__class__) == True
        '''
        Node.__init__(self, name)
        assert isinstance(replacer, Node), 'Invalid replacer %s' % replacer
        self._replacer = replacer

    @omni.resolver
    def doAssemble(self, target):
        '''
        Assembles this replacer.
        
        @param target: string
            The assembling target.
        '''
        if target != TARGET_REPLACE: return omni.CONTINUE
        nodes = self.doFindNode(self._replacer.name)
        nodes = [node for node in nodes if isinstance(node, self._replacer.__class__)]
        if not nodes:
            raise SetupError('Could not find any target node for replacer %s' % self._replacer)
        if len(nodes) > 1:
            raise SetupError('To many target nodes %s found for replacer %s' % (nodes, self._replacer))
        else: nodes[0].replace(self._replacer)
        return self._path

class ReplacerConfigurations(Node):
    '''
    Node that provides the replacing of configurations, more or less sets configuration values.
    '''
        
    def __init__(self, configurations):
        '''
        @see: Node.__init__
        
        @param configurations: dictionary{string, object}
            The configurations dictionary.
        '''
        Node.__init__(self, 'module$configurations')
        assert isinstance(configurations, dict), 'Invalid configurations %s' % configurations
        if __debug__:
            for name in configurations: assert isinstance(name, str), 'Invalid configuration name %s' % name
        self._configurations = configurations

    @omni.resolver
    def doAssemble(self, target):
        '''
        Assembles this replacer.
        
        @param target: string
            The assembling target.
        '''
        if target != TARGET_REPLACE: return omni.CONTINUE
        for name, value in self._configurations.items():
            try: self.doSetConfiguration(name, value, omni=omni.F_FIRST)
            except omni.NoResultError: raise SetupError('Cannot set configuration %r with value %s' % (name, value))
        return self._path
