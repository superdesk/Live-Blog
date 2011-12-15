'''
Created on Dec 8, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Module containing the nodes for the IoC conditional setup.
'''

from .. import omni
from .node import Node, SetupError, ICondition
import logging

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

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
    def doAssemble(self):
        '''
        Assembles this condition.
        '''
        try: self.doAddCondition(self, self._target, omni=omni.F_FIRST)
        except omni.NoResultError: raise SetupError('Cannot locate any node for target %s' % self._target)
        return omni.CONTINUE # Continue the assemble for others
    
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

