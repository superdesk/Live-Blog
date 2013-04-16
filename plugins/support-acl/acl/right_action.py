'''
Created on Jan 20, 2013

@package: GUI security
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the ACL GUI right.
'''

from .right_sevice import RightService
from gui.action.api.action import Action

# --------------------------------------------------------------------

class RightAction(RightService):
    '''
    The model that describes a right that is binded with actions.
    @see: RightService
    '''
    
    def __init__(self, name, description):
        '''
        @see: RightService.__init__
        '''
        super().__init__(name, description)
        self._actions = []
        
    def actions(self):
        '''
        Provides an iterator over the actions of the right.
        '''
        return iter(self._actions)
        
    def addActions(self, *actions):
        '''
        Add a new action to the right action.
        
        @param action: Action
            The action to be added.
        @return: self
            The self object for chaining purposes.
        '''
        for action in actions:
            assert isinstance(action, Action), 'Invalid action %s' % action
            self._actions.append(action)
        return self
