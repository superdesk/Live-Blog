'''
Created on Dec 6, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Module containing the nodes for the IoC setup procedure.
'''

from .. import omni
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

VALIDATION_NAME = re.compile('([a-z_A-Z]{1})([a-z_A-Z0-9\\$]*$)')
# The regex for name validation .

split = lambda path: path.rsplit(SEPARATOR, 1) if SEPARATOR in path else ('', path)
# Splits the path into the root path and name.

asSubPath = lambda path: path if path.startswith(SEPARATOR) else SEPARATOR + path
# Makes the provided path a sub part of a path, basically adds a separator in front of the path if doesn't have one.

asPrePath = lambda path: path if path.endswith(SEPARATOR) else path + SEPARATOR 
# Makes the provided path a pre part of a path, basically adds a separator at the end of the path if doesn't have one.

PREFIX_CONFIG = '_'
# Configuration prefix.

#TODO: the isconfig and to config need to be made to handle also paths not only names.
isConfig = lambda name: name.startswith(PREFIX_CONFIG)
# Checks if the name is a configuration name.

toConfig = lambda name: name if isConfig(name) else PREFIX_CONFIG + name
# Converts the provided name to configuration name.

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

@omni.source('children', 'parent')
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
        self._path = name
        self._parent = None
        self._children = {}
     
    def setParent(self, parent):
        '''
        Sets the parent of this node.
        
        @param parent: Node
            The parent to set.
        @return: self
            The same node for chaining purposes.
        '''
        assert isinstance(parent, Node), 'Invalid parent node %s' % parent
        if self._parent: raise SetupError('This node %s is already indexed on %s' % (self, self._parent))
        if self._name in parent._children: raise SetupError('The child node %s is already in %s' % (self, parent))
        self._parent = parent
        parent._children[self._name] = self
        self._updatePath()
        assert log.debug('Set parent %s for %s', parent, self) or True
        return self

    name = property(lambda self: self._name, doc=
'''
@type name: string
    The name of the node.
''')
    path = property(lambda self: self._path, doc=
'''
@type path: string
    The path of the node, this has to uniquely identify this node.
''')
    parent = property(lambda self: self._parent, setParent, doc=
'''
@type parent: Node|None
    The parent node.
''')
    children = property(lambda self: self._children.values(), doc=
'''
@type children: list[Node]
    The children nodes..
''')

    @omni.resolver      
    def doFindNode(self, *criteria):
        '''
        Finds the node that recognizes the criteria.
        
        @param criteria: arguments
            The criteria(s) used to identify the node.
        '''
        if not self._isMatched(criteria): return omni.CONTINUE
        return self
    
    def _updatePath(self):
        '''
        Called when the parenting structure of a node is changed and the path needs to be updated.
        '''
        if self._parent:
            self._path = self._parent._path + SEPARATOR + self._name
        else: self._path = self._name
        for child in self._children.values(): child._updatePath()
    
    def _isMatched(self, criteria):
        '''
        Checks if the provided criteria matches the Node.
        
        @param criteria: tuple(object)|list[object]
            The criteria(s) to check.
        @return: boolean
            True if the criteria is matched, False otherwise.
        '''
        assert isinstance(criteria, (tuple, list)), 'Invalid criteria %s' % criteria
        if not criteria: return True 
        for crt in criteria:
            if isinstance(crt, str): return self._isMatchedPath(crt)
        return False
    
    def _isMatchedPath(self, path):
        '''
        Checks if the provided path matches the Node path.
        
        @param path: string
            The path to check.
        @return: boolean
            True if the path is matched, False otherwise.
        '''
        assert isinstance(path, str), 'Invalid path %s' % path
        if self._path == path: return True
        if self._path.endswith(asSubPath(path)): return True
        return False
    
    def __repr__(self):
        '''
        @see: http://docs.python.org/reference/datamodel.html
        '''
        l = [self.__class__.__name__, ':', id(self), '[path=', self._path, ']']
        return ''.join(str(v) for v in l)

class Woman(Node):
    '''
    @see: Node.__init__
    I didn't know exactly how to call this node because it provides support for listeners and conditions so I think is
    normal to call it a woman than.
    '''
    
    def __init__(self, name):
        '''
        @see: Node.__init__
        '''
        Node.__init__(self, name)
        self._listeners = []
        self._conditions = []
    
    @omni.resolver
    def doAddListener(self, listener, *criteria):
        '''
        Add a listener to this node.
        
        @param listener: IListener
            The listener to add.
        @param criteria: arguments
            The criteria(s) used to identify the node. If no criteria is provided than the event is considered valid for
            all nodes.
        @return: string
            The path of the women who registered the listener.
        '''
        if not self._isMatched(criteria) or not self._isChecked(): return omni.CONTINUE
        self._addListener(listener)
        return self._path
    
    @omni.resolver
    def doAddCondition(self, condition, *criteria):
        '''
        Add a condition to this node.
        
        @param condition: ICondition
            The condition to add.
        @param criteria: arguments
            The criteria(s) used to identify the node. If no criteria is provided than the event is considered valid for
            all nodes.
        @return: string
            The path of the women who registered the condition.
        '''
        if not self._isMatched(criteria) or not self._isChecked(): return omni.CONTINUE
        assert isinstance(condition, ICondition), 'Invalid condition %s' % condition
        if condition in self._conditions: raise SetupError('The condition %s is already in %s' % (condition, self))
        self._conditions.append(condition)
        assert log.debug('Added condition %s to %s', condition, self) or True
        return self._path

    def _addListener(self, listener):
        '''
        Add a listener to this node.
        
        @param listener: IListener
            The listener to add.
        '''
        assert isinstance(listener, IListener), 'Invalid listener %s' % listener
        if listener in self._listeners: raise SetupError('The listener %s is already in %s' % (listener, self))
        self._listeners.append(listener)
        assert log.debug('Added listener %s to %s', listener, self) or True

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
    
    def _listenersBefore(self):
        '''
        @see: IListener.before
        Dispatches a before event to the events registered listeners.
        '''
        for listener in self._listeners:
            assert isinstance(listener, IListener)
            listener.before(self)
            
    def _listenersAfter(self, result):
        '''
        @see: IListener.after
        Dispatches a after event to the events registered listeners.
        '''
        for listener in self._listeners:
            assert isinstance(listener, IListener)
            listener.after(self, result)
            
    def _listenersAll(self, result):
        '''
        Dispatches a before and after event to the events registered listeners.
        '''
        self._listenersBefore()
        self._listenersAfter(result)

class Source(Woman):
    '''
    @see: Node
    The base class for source nodes, basically this are the nodes that have a value to process.
    '''
    
    def __init__(self, name, type=None):
        '''
        @see: Node.__init__
        
        @param type: class|None
            The type(class) of the value that is being delivered by this source.
        '''
        Woman.__init__(self, name)
        assert type is None or isclass(type), 'Invalid type %s' % type
        self._type = type

    @omni.resolver(isolation='resolver')
    def doFindSource(self, *criteria):
        '''
        Finds the node that recognizes the criteria and has a data source to deliver.
        
        @param criteria: arguments
            The criteria(s) used to identify the node. If no criteria is provided than the event is considered valid for
            all nodes.
        @return: string
            The path of the source.
        '''
        if not self._isMatched(criteria): return omni.CONTINUE
        return self._path if self._isChecked() else omni.CONTINUE
    
    @omni.resolver      
    def doFindUnused(self, *criteria):
        '''
        Finds the node that recognizes the criteria and is considered unused.
        
        @param criteria: arguments
            The criteria(s) used to identify the node. If no criteria is provided than the event is considered valid for
            all nodes.
        @return: string
            The path of the unused source.
        '''
        if not self._isMatched(criteria) or not self._isChecked(): return omni.CONTINUE
        if self._isUsed(): return omni.CONTINUE
        return self._path

    @omni.resolver
    def doProcessValue(self, *criteria):
        '''
        Provides the source value.
        
        @param criteria: arguments
            The criteria(s) used to identify the node. If no criteria is provided than the event is considered valid for
            all nodes.
        @return: object
            The processed object.
        '''
        if self._isMatched(criteria) and self._isChecked():
            if self.doIsValue(self._path, omni=omni.F_FIRST): return self.doGetValue(self._path, omni=omni.F_FIRST)
            return self._process()
        else: return omni.CONTINUE
    
    def _process(self, data):
        '''
        Processes the source value.
        
        @param data: IData
            The data repository to use for storing the processed value.
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
    
    def _isMatched(self, criteria):
        '''
        @see: Node._isMatched
        '''
        if super()._isMatched(criteria): return True
        if self._type:
            for crt in criteria:
                if isclass(crt) and issubclass(self._type, crt): return True
        return False
    
    def _isUsed(self):
        '''
        Checks if this source is used.
        '''
        return self.doIsValue(self._path, omni=omni.F_FIRST)
    
    def __repr__(self):
        '''
        @see: http://docs.python.org/reference/datamodel.html
        '''
        l = [self.__class__.__name__, ':', id(self), '[path=', self._path, ', type=', self._type, ']']
        return ''.join(str(v) for v in l)

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
        
    def _process(self):
        '''
        Processes the function value.
        @see: Source.processValue
        '''
        keyargs = extractArguments(self, self._arguments)
        ret = self._call(**keyargs)
        if isgenerator(ret): value, generator = self._validate(next(ret)), ret
        else: value, generator = self._validate(ret), None
        
        self.doSetValue(self._path, value)
        self._listenersBefore()
        assert log.debug('Processed and set value %s of node %s', value, self) or True
        
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
            self._listenersAll(self._value)
            assert log.debug('Set fixed value %s of node %s', self._value, self) or True
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
        if self._isMatchedPath(path) and self._isChecked():
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
            self._listenersAll(self._value)
            assert log.debug('Set configuration value %s of node %s', self._value, self) or True
            return self._value
        else:
            value = self.doGetValue(self._name, omni=omni.F_FIRST)
            self.doSetValue(self._path, value)
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

def extractArguments(source, arguments):
    '''
    Extract the arguments.
    
    @param source: Node
        The source node to process the arguments for.
    @param arguments: list[string]|tuple(string)
        The arguments to be extracted.
    @return: dictionary{string, value}
        The extracted arguments.
    '''
    assert isinstance(source, Node), 'Invalid source node %s' % source
    assert isinstance(arguments, (list, tuple)), 'Invalid arguments %s' % arguments
    keyargs = {}
    for name in arguments:
        assert isinstance(name, str), 'Invalid name %s' % name
        try: keyargs[name] = source.doGetValue(name, omni=omni.F_FIRST)
        except omni.NoResultError: raise SetupError('Could not find argument value %r for %s' % (name, source))
    return keyargs
