'''
Created on Jun 19, 2011

@package: ally core
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the nodes used in constructing the resources node tree.
'''

from ally.api.operator.type import TypeModelProperty
from ally.api.type import Input, typeFor
from ally.core.spec.resources import ConverterPath, Match, Node, Invoker
from collections import deque
import logging

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

ORDER_ROOT = 0
ORDER_PATH = 1
ORDER_INTEGER = 2
ORDER_STRING = 3

# --------------------------------------------------------------------

class MatchRoot(Match):
    '''
    Match class for root node.
    
    @see: Match
    '''

    def __init__(self, node):
        '''
        @see: Match.__init__
        '''
        super().__init__(node)

    def asArgument(self, invoker, args):
        '''
        @see: Match.asArgument
        '''
        # Nothing to do here

    def isValid(self):
        '''
        @see: Match.isValid
        '''
        return True

    def update(self, obj, objType):
        '''
        @see: Match.update
        '''
        return False

    def toPath(self, converterPath, isFirst, isLast):
        '''
        @see: Match.toPath
        '''
        return None

    def clone(self):
        '''
        @see: Match.clone
        '''
        return self

    def __str__(self): return 'ROOT'

class MatchString(Match):
    '''
    Match class for string.
    
    @see: Match
    '''

    def __init__(self, node, value):
        '''
        @see: Match.__init__
        
        @param value: string
            The string value of the match.
        '''
        super().__init__(node)
        assert isinstance(value, str), 'Invalid string match value %s' % value
        self.value = value

    def asArgument(self, invoker, args):
        '''
        @see: Match.asArgument
        '''
        # Nothing to do here

    def isValid(self):
        '''
        @see: Match.isValid
        '''
        return True

    def update(self, obj, objType):
        '''
        @see: Match.update
        '''
        return False

    def toPath(self, converterPath, isFirst, isLast):
        '''
        @see: Match.toPath
        '''
        assert isinstance(converterPath, ConverterPath)
        return converterPath.normalize(self.value)

    def clone(self):
        '''
        @see: Match.clone
        '''
        return self

    def __str__(self): return self.value

class MatchProperty(Match):
    '''
    Match class for string for a property.
    
    @see: Match
    '''

    def __init__(self, node, value=None):
        '''
        @see: Match.__init__
        
        @param value: string|None
            The match string value, none if the match will expect updates.
        '''
        assert isinstance(node, NodeProperty), 'Invalid node %s' % node
        super().__init__(node)
        self.value = value

    def asArgument(self, invoker, args):
        '''
        @see: Match.value
        '''
        assert isinstance(invoker, Invoker), 'Invalid invoker %s' % invoker
        assert isinstance(args, dict), 'Invalid arguments dictionary %s' % args
        assert self.value != None, 'This match %s has no value' % self
        for inp in invoker.inputs:
            if inp in self.node.inputs and inp.name not in args:
                args[inp.name] = self.value
                return

    def update(self, obj, objType):
        '''
        @see: Match.update
        '''
        if objType in self.node.typesProperties:
            self.value = obj
            return True

        for typ in self.node.typesProperties:
            assert isinstance(typ, TypeModelProperty)
            if objType == typ.container or objType == typ.parent:
                assert typ.parent.isValid(obj), 'Invalid object \'%s\' for model %s' % (obj, typ.parent)
                self.value = getattr(obj, typ.property)
                return True

        return False

    def isValid(self):
        '''
        @see: Match.isValid
        '''
        return self.value is not None

    def toPath(self, converterPath, isFirst, isLast):
        '''
        @see: Match.toPath
        '''
        assert isinstance(converterPath, ConverterPath)
        assert self.value is not None, \
        'Cannot represent the path element for %s because there is no value' % self.type
        return converterPath.asString(self.value, self.node.type)

    def clone(self):
        '''
        @see: Match.clone
        '''
        return MatchProperty(self.node, self.value)

    def __str__(self): return '*' if self.value is None else str(self.value)

# --------------------------------------------------------------------

class NodeRoot(Node):
    '''
    Provides a node for the root.
    
    @see: Node
    '''

    def __init__(self):
        '''
        @see: Match.__init__
        
        @param get: Invoker
            The get invoker for the root node.
        '''
        super().__init__(None, True, ORDER_ROOT)
        self._match = MatchRoot(self)

    def tryMatch(self, converterPath, paths):
        '''
        @see: Node.tryMatch
        '''
        return self._match

    def newMatch(self):
        '''
        @see: Node.newMatch
        '''
        return self._match
    
    def correspondentIn(self, nodes):
        '''
        @see: Node.correspondentIn
        '''
        for node in nodes:
            if isinstance(node, self.__class__): return True
        return False

    def __str__(self):
        return '<Node Root>'

# --------------------------------------------------------------------

class NodePath(Node):
    '''
    Provides a node that matches a simple string path element.
    
    @see: Node
    '''

    def __init__(self, parent, isGroup, name):
        '''
        @see: Node.__init__
        
        @param name: string
            The plain name to be used for the path node.
        @ivar _match: MatchString
            The match corresponding to this node.
        '''
        assert isinstance(name, str) and name != '', 'Invalid node name %s' % name
        self.name = name
        self._match = MatchString(self, name)
        super().__init__(parent, isGroup, ORDER_PATH)

    def tryMatch(self, converterPath, paths):
        '''
        @see: Node.tryMatch
        '''
        assert isinstance(converterPath, ConverterPath), 'Invalid converter path %s' % converterPath
        assert isinstance(paths, deque), 'Invalid paths %s' % paths
        assert len(paths) > 0, 'No path element in paths %s' % paths
        if converterPath.normalize(self._match.value) == paths[0]:
            del paths[0]
            return self._match
        return None

    def newMatch(self):
        '''
        @see: Node.newMatch
        '''
        return self._match
    
    def correspondentIn(self, nodes):
        '''
        @see: Node.correspondentIn
        '''
        for node in nodes:
            if isinstance(node, NodePath) and self.name == node.name: return True
        return False

    def __str__(self):
        return '<%s[%s]>' % (self.__class__.__name__, self.name)

class NodeProperty(Node):
    '''
    Provides a node based on a type property.
    
    @see: Node
    '''

    def __init__(self, parent, inp):
        '''
        @see: Node.__init__
        
        @param inp: Input
            The first input of the property node.
        '''
        assert isinstance(inp, Input), 'Invalid input %s' % inp
        assert isinstance(inp.type, TypeModelProperty), 'Invalid input type %s' % inp.type
        assert inp.type.isOf(int) or inp.type.isOf(str), 'Invalid input type %s' % inp.type

        self.inputs = set((inp,))
        self.typesProperties = set((inp.type,))

        self.type = typeFor(int if inp.type.isOf(int) else str)

        super().__init__(parent, False, self._orderFor(inp.type))

    def tryMatch(self, converterPath, paths):
        '''
        @see: Node.tryMatch
        '''
        assert isinstance(paths, deque), 'Invalid paths %s' % paths
        assert len(paths) > 0, 'No path element in paths %s' % paths
        assert isinstance(converterPath, ConverterPath), 'Invalid converter path %s' % converterPath
        try:
            value = converterPath.asValue(paths[0], self.type)
            del paths[0]
            return MatchProperty(self, value)
        except ValueError:
            return False

    def newMatch(self):
        '''
        @see: Node.newMatch
        '''
        return MatchProperty(self)
    
    def correspondentIn(self, nodes):
        '''
        @see: Node.correspondentIn
        '''
        for node in nodes:
            if isinstance(node, self.__class__) and self.type == node.type: return True
        return False

    def isFor(self, inp):
        '''
        Checks if the node property is for the provided input.
        
        @param inp: Input
            The input to check if valid for this node.
        '''
        assert isinstance(inp, Input), 'Invalid input %s' % inp
        if not isinstance(inp.type, TypeModelProperty): return False
        if not (inp.type.isOf(int) or inp.type.isOf(str)): return False
        return self._orderFor(inp.type) == self.order

    def addInput(self, inp):
        '''
        Adds a new input to the node property.
        
        @param inp: Input
            The input to be acknowledged by the node.
        '''
        assert isinstance(inp, Input), 'Invalid input %s' % inp
        assert isinstance(inp.type, TypeModelProperty), 'Invalid input type property %s' % inp.type
        assert self.isFor(inp), 'Invalid input %s, is not for this node' % inp
        self.inputs.add(inp)
        self.typesProperties.add(inp.type)
        
    def __str__(self):
        return '<%s[%s]>' % (self.__class__.__name__, [str(inp) for inp in self.inputs])

    # ----------------------------------------------------------------

    def _orderFor(self, type):
        '''
        Provides the order for the type.
        '''
        return ORDER_INTEGER if type.isOf(int) else ORDER_STRING
