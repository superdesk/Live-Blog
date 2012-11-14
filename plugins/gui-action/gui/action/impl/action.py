'''
Created on Feb 27, 2012

@package ally 
@copyright 2011 Sourcefabric o.p.s.
@license http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mihai Balaceanu

Action Manager Implementation
'''

import re
from ally.container.ioc import injected
from ally.container.support import setup
from gui.action.api.action import IActionManagerService, Action

# --------------------------------------------------------------------

@injected
@setup(IActionManagerService)
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
        return action.Path
        
    def getAll(self, path):
        '''
        @see: IActionManagerService.getAll
        '''
        actions = self._actions.values()
        if path:
            # match exact path, passed between " (double quotes)
            if re.match('".+"', path): 
                actions = [action for action in actions if action.Path == path.strip('"')]
            # match a word placeholder *
            elif path.find('*') != -1:
                p = '^'+re.sub(r'\\\*', '(\d|\w|-|_)+', re.escape(path))+'$'
                actions = [action for action in actions if re.match(p, action.Path)]
            # normal match, paths starting with path string
            else: 
                actions = [action for action in actions if action.Path.startswith(path.rstrip('.'))]
                
        return sorted(actions, key=lambda action: action.Path)
