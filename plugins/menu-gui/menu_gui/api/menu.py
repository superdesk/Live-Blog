'''
Created on Feb 23, 2012

@author: mihaibalaceanu
'''

from ally.api.config import service, call
from ally.api.type import Iter
from menu_gui.api import modelGui
from ally.api.configure import update

@modelGui
class Menu:
    '''
    The menu entity
    '''
    Id = int
    Name = str
    Display = str
    Parent = int
    
update(Menu.Parent, Menu.Id)
    
@service
class IMenuProviderService:
    '''
    Provides GUI menu entries
    '''
    
    @call
    def getAll(self) -> Iter(Menu):
        '''
        Provides the menu
        '''


