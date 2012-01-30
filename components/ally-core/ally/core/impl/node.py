'''
Created on Jun 19, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the nodes used in constructing the resources node tree.
'''

from ally.api.operator import Model
from ally.api.type import TypeProperty, TypeModel, Input
from ally.core.spec.resources import ConverterPath, Match, Node, Invoker
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
        
        @param matchValue: string
            The string value of the match.
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

class MatchString(Match):
    '''
    Match class for string.
    
    @see: Match
    '''
    
    def __init__(self, node, matchValue):
        '''
        @see: Match.__init__
        
        @param matchValue: string
            The string value of the match.
        '''
        super().__init__(node)
        assert isinstance(matchValue, str), 'Invalid string match value %s' % matchValue
        self.matchValue = matchValue
    
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
        return converterPath.normalize(self.matchValue)
    
    def clone(self):
        '''
        @see: Match.clone
        '''
        return self

class MatchProperty(Match):
    '''
    Match class for string for a property.
    
    @see: Match
    '''
    
    def __init__(self, node, typeProperty, matchValue=None):
        '''
        @see: Match.__init__
        
        @param typeProperty: TypeProperty
            The type property represented by the matcher.
        @param matchValue: string|None
            The match string value, none if the match will expect updates.
        '''
        super().__init__(node)
        assert isinstance(typeProperty, TypeProperty), 'Invalid type property %s' % typeProperty
        self.matchValue = matchValue
        self.typeProperty = typeProperty
    
    def asArgument(self, invoker, args):
        '''
        @see: Match.value
        '''
        assert isinstance(invoker, Invoker), 'Invalid invoker %s' % invoker
        assert isinstance(args, dict), 'Invalid arguments dictionary %s' % args
        assert self.matchValue != None, 'This match %s has not value' % self
        for inp in invoker.inputs:
            assert isinstance(inp, Input)
            if inp.type == self.typeProperty:
                args[inp.name] = self.matchValue
                return
    
    def update(self, obj, objType):
        '''
        @see: Match.update
        '''
        if objType == self.typeProperty.model:
            self.matchValue = self.typeProperty.property.get(obj)
            return True
        elif isinstance(objType, TypeModel):
            assert isinstance(objType, TypeModel)
            if objType.model == self.typeProperty.model:
                self.matchValue = self.typeProperty.property.get(obj)
                return True
        elif isinstance(objType, TypeProperty):
            if objType == self.typeProperty:
                self.matchValue = obj
                return True
        return False
    
    def isValid(self):
        '''
        @see: Match.isValid
        '''
        return self.matchValue is not None
    
    def toPath(self, converterPath, isFirst, isLast):
        '''
        @see: Match.toPath
        '''
        assert isinstance(converterPath, ConverterPath)
        assert self.matchValue is not None, \
        'Cannot represent the path element for %s because there is no value' % self.typeProperty
        return converterPath.asString(self.matchValue, self.typeProperty)
    
    def clone(self):
        '''
        @see: Match.clone
        '''
        return MatchProperty(self.node, self.typeProperty, self.matchValue)

# --------------------------------------------------------------------

class NodeRoot(Node):
    '''
    Provides a node for the root.
    
    @see: Node
    '''
    
    def __init__(self, get):
        '''
        @see: Match.__init__
        
        @param get: Invoker
            The get invoker for the root node.
        '''
        super().__init__(None, True, ORDER_ROOT)
        assert isinstance(get, Invoker), 'Invalid get invoker %s' % get
        assert len(get.inputs) == 0, 'No inputs are allowed for the get on the root node'
        self.get = get
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

    def __eq__(self, other):
        return isinstance(other, self.__class__)
    
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
        assert isinstance(paths, list), 'Invalid paths %s' % paths
        assert len(paths) > 0, 'No path element in paths %s' % paths
        if converterPath.normalize(self._match.matchValue) == paths[0]:
            del paths[0]
            return self._match
        return None

    def newMatch(self):
        '''
        @see: Node.newMatch
        '''
        return self._match

    def __eq__(self, other):
        if isinstance(other, NodePath):
            return self.name == other.name
        return False
    
    def __str__(self):
        return '<%s[%s]>' % (self.__class__.__name__, self.name)

class NodeModel(NodePath):
    '''
    Provides a node that matches model elements.
    
    @see: Node
    '''
    
    def __init__(self, parent, model):
        '''
        @see: Node.__init__
        
        @param model: Model
            The model to make the matching based on.
        @ivar _match: MatchString
            The match corresponding to this node.
        '''
        assert isinstance(model, Model), 'Invalid model %s' % model
        self.model = model
        super().__init__(parent, True, model.name)

class NodeProperty(Node):
    '''
    Provides a node based on a type property.
    
    @see: Node
    '''
    
    def __init__(self, parent, typeProperty):
        '''
        @see: Node.__init__
        
        @param type: TypeProperty
            The type property represented by the node.
        '''
        assert isinstance(typeProperty, TypeProperty), 'Invalid type property %s' % typeProperty
        assert typeProperty.isOf(int) or typeProperty.isOf(str), \
        'Invalid property type class %s needs to be an integer or string' % typeProperty
        self.typeProperty = typeProperty
        super().__init__(parent, False, ORDER_INTEGER if typeProperty.isOf(int) else ORDER_STRING)

    def tryMatch(self, converterPath, paths):
        '''
        @see: Node.tryMatch
        '''
        assert isinstance(paths, list), 'Invalid paths %s' % paths
        assert len(paths) > 0, 'No path element in paths %s' % paths
        assert isinstance(converterPath, ConverterPath), 'Invalid converter path %s' % converterPath
        try:
            value = converterPath.asValue(paths[0], self.typeProperty)
            del paths[0]
            return MatchProperty(self, self.typeProperty, value)
        except ValueError:
            return False

    def newMatch(self):
        '''
        @see: Node.newMatch
        '''
        return MatchProperty(self, self.typeProperty)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.typeProperty == other.typeProperty
        return False

    def __str__(self):
        return '<%s[%s]>' % (self.__class__.__name__, self.typeProperty)
