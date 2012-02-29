'''
Created on Feb 27, 2012

@package ally 
@copyright 2011 Sourcefabric o.p.s.
@license http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mihai Balaceanu

Action Manager Implementation
'''

from actions_gui.api.action import IActionManagerService, Action
from ally.container.ioc import injected
from ally.internationalization import translator

# --------------------------------------------------------------------

_ = translator(__name__)

# --------------------------------------------------------------------

@injected
class ActionManagerService(IActionManagerService):
    '''
    @see: IActionManagerService
    '''

    def __init__(self):
        '''  '''
        self._actions = {}
    
    def add(self, action):
        '''
        @see: IActionManagerService.add
        '''
        assert isinstance(action, Action), 'Invalid parameter action: %s' % action
        self._actions[action.Path] = action
        
    def getAll(self, path):
        '''
        @see: IActionManagerService.getAll
        '''
        actions = self._actions.values()
        if path: actions = [action for action in actions if action.Path.startswith(path.rstrip('.')+'.')]
        return actions
