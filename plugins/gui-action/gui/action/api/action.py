'''
Created on Feb 27, 2012

@package ally 
@copyright 2011 Sourcefabric o.p.s.
@license http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mihai Balaceanu

Action manager interface and action model 
'''

from gui.api import modelGui
from ally.api.config import service, call
from ally.api.operator import INSERT
from ally.api.type import Iter
import re

# --------------------------------------------------------------------

@modelGui
class Action:
    '''
    The object used to create and group actions 
    '''
    Path = str
    Label = str
    ScriptPath = str
    
    def __init__(self, Path=None, Label=None, Parent=None):
        self.Path = ''
        if Path:
            self.Path = re.compile('[^\w\-\.]', re.ASCII).sub('', Path)
        if Parent:
            assert isinstance(Parent, Action), 'Invalid Parent object: %s' % Parent
            self.Path = Parent.Path + '.' + self.Path
        if Label:
            self.Label = Label
    
# --------------------------------------------------------------------

@service
class IActionManagerService:
    '''
    Provides a container and manager for actions
    '''
    
    @call(method=INSERT)
    def add(self, action:Action) -> Action.Path:
        '''
        Register an action here
        '''
        
    @call
    def getAll(self, path:str=None) -> Iter(Action):
        '''
        Get all actions registered
        '''
