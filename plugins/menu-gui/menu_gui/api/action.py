'''
Created on Feb 27, 2012

@author: mihaibalaceanu
'''

from ally.api.config import service, call
from ally.api.configure import update
from menu_gui.api import modelGui
from ally.api.type import Iter
from ally.api.operator import INSERT

# --------------------------------------------------------------------

@modelGui
class Action:
    '''
    The object used to create and group actions 
    '''
    Id = int
    Name = str
    Parent = int
    
    def __init__(self, Name=None, Parent=None):
        if Name: self.Name = Name
        if Parent: 
            assert isinstance(Parent, Action), 'Invalid Parent object: %s' % Parent
            self.Parent = Parent.Id
    
update(Action.Parent, Action.Id)

@service
class IActionManagerService:
    '''
    Provides a container and manager for actions
    '''
    
    @call(method=INSERT)
    def add(self, action:Action) -> Action.Id:
        '''
        Register an action here
        '''
        
    @call
    def getById(self, id:Action.Id) -> Action:
        '''
        ''' 
        
    @call
    def getAll(self) -> Iter(Action):
        '''
        
        '''
    
    @call(webName='ByParent')
    def getByParent(self, parentId:Action.Id) -> Iter(Action):
        '''
        
        '''
