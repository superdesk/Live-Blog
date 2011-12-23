'''
Created on Dec 6, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Module containing the nodes for the IoC setup procedure.
'''

from _abcoll import Callable
from copy import deepcopy
from inspect import isclass, isfunction, getfullargspec, isgenerator
import abc
import logging
import re

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

SEPARATOR = '.'
# The path separator.

VALIDATION_NAME = re.compile('([a-z_A-Z]{1})([a-z_A-Z0-9\\.\\$]*$)')
# The regex for name validation .

split = lambda path: path.rsplit(SEPARATOR, 1) if SEPARATOR in path else ('', path)
# Splits the path into the root path and name.

asSubPath = lambda path: path if path.startswith(SEPARATOR) else SEPARATOR + path
# Makes the provided path a sub part of a path, basically adds a separator in front of the path if doesn't have one.

asPrePath = lambda path: path if path.endswith(SEPARATOR) else path + SEPARATOR 
# Makes the provided path a pre part of a path, basically adds a separator at the end of the path if doesn't have one.

PREFIX_CONFIG = '_'
# Configuration prefix.

MATCHER_CONFIG = re.compile('[a-z_' + re.escape(SEPARATOR) + 'A-Z0-9]*' + re.escape(PREFIX_CONFIG) + '+[a-zA-Z0-9\\$]*$')
# Provides the matcher that detects a configuration name.

isConfig = lambda name: MATCHER_CONFIG.match(name) is not None
# Checks if the name is a configuration name.

def toConfig(name):
    '''Converts the provided name to configuration name.'''
    assert isinstance(name, str), 'Invalid name %s' % name
    if isConfig(name): return name
    
    splits = name.split(SEPARATOR)
    splits[-1] = PREFIX_CONFIG + splits[-1]
    return SEPARATOR.join(splits)

#TODO: comment
IGNORE = object()

# --------------------------------------------------------------------

class SetupError(Exception):
    '''
    Exception thrown when there is a setup problem.
    '''

# --------------------------------------------------------------------

class IListener(metaclass=abc.ABCMeta):
    '''
    API for node listeners.
    '''
    
    @abc.abstractclassmethod
    def before(self, source):
        '''
        Method invoked before an action is taken by the node.
        
        @param source: Node
            The source node of the event.
        '''
        
    @abc.abstractclassmethod
    def after(self, source, result):
        '''
        Method invoked after an action has been finalized.
        
        @param source: Node
            The source node of the event.
        @param result: object|None
            The result of the after process.
        '''
        
class ICondition(metaclass=abc.ABCMeta):
    '''
    API for node conditions.
    '''
    
    @abc.abstractclassmethod
    def isValid(self):
        '''
        Method invoked to check if the condition is valid for the node.
        '''

# --------------------------------------------------------------------

class Node:
    '''
    The base node structure.
    '''
    
    def __init__(self, name):
        '''
        Construct the node.
        
        @param name: string
            The name of this node.
        '''
        assert isinstance(name, str), 'Invalid name string %s' % name
        assert VALIDATION_NAME.match(name), 'Invalid name formatting %s' % name
        self._name = name

    name = property(lambda self: self._name, doc=
'''
@type name: string
    The name of the node.
''')
    
    def doMatch(self, *criteria):
        '''
        Checks if this node recognizes the criteria.
        
        @param criteria: arguments
            The criteria(s) used to identify the node. If no criteria is provided than the event is considered valid for
            all nodes.
        @return: Node|IGNORE
            The matched node, otherwise IGNORE.
        '''
        if not criteria: return self 
        for crt in criteria:
            if isinstance(crt, str):
                if self._name == crt: return self
                if self._name.endswith(asSubPath(crt)): return self
        return IGNORE

    def __repr__(self):
        '''
        @see: http://docs.python.org/reference/datamodel.html
        '''
        l = [self.__class__.__name__, ':', id(self), '[name=', self._name, ']']
        return ''.join(str(v) for v in l)

class Resolver(Node):
    '''
    @see: Node.__init__
    Provides support for listeners and conditions.
    '''
    
    def __init__(self, name):
        '''
        @see: Node.__init__
        '''
        Node.__init__(self, name)
        self._listeners = []
        self._conditions = []
    
    def doListener(self, listener, *criteria):
        '''
        Add a listener to this node.
        
        @param listener: IListener
            The listener to add.
        @param criteria: arguments
            The criteria(s) used to identify the node. If no criteria is provided than the event is considered valid for
            all nodes.
        @return: string|IGNORE
            The name of the node that added the listener.
        '''
        if self.doMatch(*criteria) is IGNORE: return IGNORE
        if not self._isChecked(): return IGNORE
        assert isinstance(listener, IListener), 'Invalid listener %s' % listener
        if listener in self._listeners: raise SetupError('The listener %s is already in %s' % (listener, self))
        self._listeners.append(listener)
        assert log.debug('Added listener %s to %s', listener, self) or True
        return self._name
    
    def doCondition(self, condition, *criteria):
        '''
        Add a condition to this node.
        
        @param condition: ICondition
            The condition to add.
        @param criteria: arguments
            The criteria(s) used to identify the node. If no criteria is provided than the event is considered valid for
            all nodes.
        @return: string
            The path of the node who registered the condition.
        '''
        if self.doMatch(*criteria) is IGNORE: return IGNORE
        assert isinstance(condition, ICondition), 'Invalid condition %s' % condition
        if condition in self._conditions: raise SetupError('The condition %s is already in %s' % (condition, self))
        self._conditions.append(condition)
        assert log.debug('Added condition %s to %s', condition, self) or True
        return self._name

    def _isChecked(self):
        '''
        Used to check the assigned conditions.
        
        @return: boolean
            True if the conditions allow the node, False otherwise.
        '''
        for condition in self._conditions:
            assert isinstance(condition, ICondition)
            if not condition.isValid(): return False
        return True
    
    def _dispatchBefore(self):
        '''
        @see: IListener.before
        Dispatches a before event to the events registered listeners.
        '''
        for listener in self._listeners:
            assert isinstance(listener, IListener)
            listener.before(self)
            
    def _dispatchAfter(self, result):
        '''
        @see: IListener.after
        Dispatches a after event to the events registered listeners.
        '''
        for listener in self._listeners:
            assert isinstance(listener, IListener)
            listener.after(self, result)
            
    def _dispatchAll(self, result):
        '''
        Dispatches a before and after event to the events registered listeners.
        '''
        self._dispatchBefore()
        self._dispatchAfter(result)

class Source(Resolver):
    '''
    @see: Resolver
    The base class for source nodes, basically this are the nodes that have a value to process.
    '''
    
    def __init__(self, name, type=None):
        '''
        @see: Resolver.__init__
        
        @param type: class|None
            The type(class) of the value that is being delivered by this source.
        '''
        Resolver.__init__(self, name)
        assert type is None or isclass(type), 'Invalid type %s' % type
        self._type = type
        self._hasValue = False
        self._value = None
    
    def doMatch(self, *criteria):
        '''
        @see: Node.doMatch
        '''
        if super().doMatch(criteria) is IGNORE:
            if self._type:
                for crt in criteria:
                    if isclass(crt) and issubclass(self._type, crt): return self
        return IGNORE

    def doUnused(self, *criteria):
        '''
        Finds the node that recognizes the criteria and is considered unused.
        
        @param criteria: arguments
            The criteria(s) used to identify the node. If no criteria is provided than the event is considered valid for
            all nodes.
        @return: string
            The path of the unused source.
        '''
        if self.doMatch(*criteria) is IGNORE: return IGNORE
        if not self._isChecked() or self._hasValue: return IGNORE
        return self._name
    
    def doValue(self, search, *criteria):
        '''
        Provides the source value.
        
        @param criteria: arguments
            The criteria(s) used to identify the node. If no criteria is provided than the event is considered valid for
            all nodes.
        @return: object
            The processed object.
        '''
        if self.doMatch(*criteria) is IGNORE: return IGNORE
        if self._isChecked():
            if not self._hasValue: self._process(search)
            return self._value
        return IGNORE
    
    def _process(self, search):
        '''
        Processes the source value.
        
        @return: object
            The process value.
        '''
    
    def _validate(self, value):
        '''
        Validates the provided value against the source type.
        
        @param value: object   
            The value to check.
        @return: object
            The same value as the provided value.
        @raise SetupError: In case the value is not valid.
        '''
        if self._type and value is not None and not isinstance(value, self._type):
            raise SetupError('Invalid value provided %s, expected type %s for %s' % (value, self._type, self))
        return value

    def __repr__(self):
        '''
        @see: http://docs.python.org/reference/datamodel.html
        '''
        l = [self.__class__.__name__, ':', id(self), '[path=', self._path, ', type=', self._type, ']']
        return ''.join(str(v) for v in l)

# --------------------------------------------------------------------

class Function(Source):
    '''
    Provides a source node that invokes a function in order to get the value.
    '''
    
    def __init__(self, name, call, type=None, arguments=None):
        '''
        @see: Source.__init__
        
        @param call: Callable
            The function call to invoke for the value.
        @param arguments: list[string]|None
            The list of argument names to invoke the call with, None for no arguments.
        '''
        Source.__init__(self, name, type)
        if isConfig(name):
            raise SetupError('The function name %r cannot start with %r' % (name, PREFIX_CONFIG))
        assert isinstance(call, Callable), 'Invalid callable object %s' % call
        self._call = call
        if arguments:
            assert isinstance(arguments, list), 'Invalid arguments %s' % arguments
            if __debug__:
                for argn in arguments: assert isinstance(argn, str), 'Invalid argument name %s' % argn
            self._arguments = arguments
        else: self._arguments = []
    
    
    def _process(self, search):
        '''
        Processes the function value.
        @see: Source._process
        '''
        keyargs = extractArguments(search, self._arguments)
        ret = self._call(**keyargs)
        if isgenerator(ret): value, generator = self._validate(next(ret)), ret
        else: value, generator = self._validate(ret), None
        
        self.doSetValue(self._path, value)
        assert log.debug('Processed and set value %s of node %s', value, self) or True
        omni.release()
        self._listenersBefore()
        
        if generator:
            try: next(generator)
            except StopIteration: pass
        
        self._listenersAfter(value)
        assert log.debug('Initialized and set value %s of node %s', value, self) or True
        return value

class Argument(Source):
    '''
    Provides a source node that acts like a function argument. It keeps a value or a type for the argument and when a
    function requires the argument it will try to provide the value based on this properties.
    '''
    
    @omni.resolver
    def doAddListener(self, listener, *criteria):
        '''
        @see: Women.doAddListener
        '''
        if self._isMatched(criteria) and self._isChecked():
            if self._hasValue:
                self._addListener(listener)
                return self._path
            elif self._type not in criteria:
                # If the argument has no value it means that he cannot deliver the listener event so we just add the type
                # of the argument in the criteria and let other woman that has the source register the listener.
                omni.change(listener, self._type, *criteria)
        return omni.CONTINUE
    
    def __init__(self, name, type=None, hasValue=False, value=None):
        '''
        @see: Source.__init__
        The argument needs to have provided either a type or a value.
        
        @param hasValue: boolean
            A flag indicating that the argument has a value, since None can also be a valid value for the argument.
        @param value: object
            The argument value, event None is valid value.
        '''
        assert isinstance(hasValue, bool), 'Invalid has value flag %s' % hasValue
        if hasValue:
            if not type: type = value.__class__
            else: assert isinstance(value, type), 'Invalid value %s for type %s' % (value, type)
        assert type is not None, 'The argument needs either a type or a value specified'
        Source.__init__(self, name, type)
        self._hasValue = hasValue
        self._value = value
        
    def _process(self):
        '''
        Processes the argument value.
        @see: Source.processValue
        '''
        if self._hasValue:
            self.doSetValue(self._path, self._value)
            assert log.debug('Set fixed value %s of node %s', self._value, self) or True
            omni.release()
            self._listenersAll(self._value)
            return self._value
        else:
            values = self.doProcessValue(self._type)
            if not values:
                raise SetupError('Could not find any data source for type %s for %s' % (self._type, self))
            if len(values) > 1:
                raise SetupError('To many values %s found for %s' % (values, self))
            else:
                value = self._validate(values[0])
                self.doSetValue(self._path, value)
                assert log.debug('Processed value %s by type of node %s', value, self) or True
                return value
            
class Configuration(Source):
    '''
    Provides a source node that acts like a configuration.
    '''
    
    def __init__(self, name, type=None, hasValue=False, value=None, description=None):
        Source.__init__(self, name, type)
        assert isinstance(hasValue, bool), 'Invalid has value flag %s' % hasValue
        if hasValue and type: assert isinstance(value, type), 'Invalid value %s for type %s' % (value, type)
        assert not description or isinstance(description, str), 'Invalid description %s' % description
        self._hasValue = hasValue
        self._value = value
        self._description = description
        
    description = property(lambda self: self._description, doc=
'''
@type description: string
    The description of the configuration.
''')
    
    @omni.resolver
    def doAddListener(self, listener, *criteria):
        '''
        @see: Women.doAddListener
        '''
        if self._isMatched(criteria) and self._isChecked() and self._hasValue:
            # If the configuration has no value it means it cannot provide the before and after for the listeners.
            self._addListener(listener)
            return self._path
        return omni.CONTINUE

    @omni.resolver
    def doSetConfiguration(self, path, value):
        '''
        Sets the configuration with the specified path.
        
        @param path: string
            The path to set the configuration to.
        @param value: object
            The configuration value to set.
        @return: True
            If the path was successfully set on this node.
        '''
        assert isinstance(path, str), 'Invalid configuration path %s' % path
        if self._isMatchedPath(toConfig(path)) and self._isChecked():
            self._value = self._validate(value)
            self._hasValue = True
            return True
        return omni.CONTINUE

    def _process(self):
        '''
        Processes the configuration value.
        @see: Source.processValue
        '''
        if self._hasValue:
            self.doSetValue(self._path, self._value)
            assert log.debug('Set configuration value %s of node %s', self._value, self) or True
            omni.release()
            self._listenersAll(self._value)
            return self._value
        else:
            value = self.doGetValue(self._name, omni=omni.F_FIRST)
            self.doSetValue(self._path, self._validate(value))
            assert log.debug('Set configuration value %s from source %r for node %s', value, self._name, self) or True
            return value

# --------------------------------------------------------------------

def argumentsFor(function):
    '''
    Extracts the function arguments from the provided function.
    
    @param function: function 
        The function to extract the arguments for.
    @return: tuple(list[string], dictionary{string, object}, dictionary{string, object})
        Basically this will return the function args, defaults, annotations.
    '''
    assert isfunction(function), 'Invalid function %s' % function
    fnArgs = getfullargspec(function)
    if fnArgs.varargs is not None or fnArgs.varkw is not None:
        raise SetupError('The setup function %r cannot have variable arguments or key arguments' % \
                         function.__name__)
    defaults = {}
    if fnArgs.defaults:
        for k, argn in enumerate(fnArgs.args):
            i = len(fnArgs.defaults) - (len(fnArgs.args) - k)
            if i >= 0: defaults[argn] = fnArgs.defaults[i]
    return list(fnArgs.args), defaults, fnArgs.annotations

def argumentsPush(node, arguments, defaults, annotations):
    '''
    Pushes argument and configurations nodes into the provided node based on the provided arguments.
    
    @param node: Node
        The node in which to push the arguments/configurations.
    @param argumens: list[string]
        The name of the arguments to be pushed.
    @param defaults: dictionary{string, object}
        The default values for the arguments.
    @param annotations: dictionary{string, object}
        The annotations for the arguments.
    '''
    assert isinstance(node, Node), 'Invalid node %s' % node
    assert isinstance(arguments, list), 'Invalid arguments %s' % defaults
    assert isinstance(defaults, dict), 'Invalid defaults %s' % defaults
    assert isinstance(annotations, dict), 'Invalid annotations %s' % annotations
    
    for argn in arguments:
        hasValue, value, type = argn in defaults, deepcopy(defaults.get(argn)), None
        if value is not None: type = value.__class__

        if isConfig(argn):
            description = None
            if argn in annotations:
                description = annotations[argn]
                if not isinstance(description, str):
                    raise SetupError('The annotation for argument %r in %r needs to be a string' % (argn, node))
            Configuration(argn, type, hasValue, value, description).setParent(node)
        else:
            if argn in annotations:
                type = annotations[argn]
                if not isclass(type):
                    raise SetupError('The annotation for argument %r in %r needs to be a class' % (argn, node))
            if hasValue or type is not None: Argument(argn, type, hasValue, value).setParent(node)
 
def functionFrom(function, name=None):
    '''
    Constructs a IoC Function based on the provided function.
    
    @param function: function 
        The function to convert to Function.
    @param name: string|None
        The name to use for the function, if not specified it will use the function name.
    @return: Function
        The converted function.
    '''
    assert name is None or isinstance(name, str), 'Invalid name %s' % name

    assert isfunction(function), 'Invalid function %s' % function
    name = name or function.__name__

    arguments, defaults, annotations = argumentsFor(function)
    
    type = None
    if 'return' in annotations:
        type = annotations['return']
        if not isclass(type):
            raise SetupError('The return annotation for function %r needs to be a class, got %s' % (name, type))

    fn = Function(name, function, type, arguments)
    argumentsPush(fn, arguments, defaults, annotations)
    
    return fn

# --------------------------------------------------------------------

def extractArguments(search, arguments):
    '''
    Extract the arguments.
    
    @param search: ISearch
        The search used for finding the values.
    @param arguments: list[string]|tuple(string)
        The arguments to be extracted.
    @return: dictionary{string, value}
        The extracted arguments.
    '''
    assert isinstance(source, Node), 'Invalid source node %s' % source
    assert isinstance(arguments, (list, tuple)), 'Invalid arguments %s' % arguments
    keyargs = {}
    argumentSearch = Search(search)
    for name in arguments:
        assert isinstance(name, str), 'Invalid name %s' % name
        keyargs[name] = argumentSearch.findFirst('doValue', argumentSearch, name)
        argumentSearch.reset()
        try:  keyargs[name] = source.doGetValue(name, omni=omni.F_FIRST)
        except omni.NoResultError: raise SetupError('Could not find argument value %r for %s' % (name, source))
    return keyargs
