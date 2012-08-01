'''
Created on Feb 27, 2012

@package ally 
@copyright 2011 Sourcefabric o.p.s.
@license http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mihai Balaceanu

Action manager interface and action model 
'''

from gui.api import modelGui
from ally.api.config import service, call, INSERT
from ally.api.type import Iter
import re

# --------------------------------------------------------------------

@modelGui(id='Path')
class Action:
    '''
    The object used to create and group actions 
    '''
    Path = str
    # path to register in 
    Label = str
    # display label
    ScriptPath = str
    # ui script path
    Href = str
    # href to use for ui controls
    ChildrenCount = int

    def __init__(self, Path=None, Label=None, Parent=None, ScriptPath=None, Href=None):
        self.Path = ''
        self.ChildrenCount = 0
        if Path:
            self.Path = re.compile('[^\w\-\.]', re.ASCII).sub('', Path)
        if Parent:
            assert isinstance(Parent, Action), 'Invalid Parent object: %s' % Parent
            self.Path = Parent.Path + '.' + self.Path
            Parent.incrementKids(self)
        if Label:
            self.Label = Label
        if ScriptPath:
            self.ScriptPath = ScriptPath
        if Href:
            self.Href = Href;

    def incrementKids(self, action):
        if not isinstance(action, Action): return
        self.ChildrenCount += 1

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
