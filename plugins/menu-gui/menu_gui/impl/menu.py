'''
Created on Feb 23, 2012

@author: mihaibalaceanu
'''

from ..api.menu import IMenuProviderService
from ally.container.ioc import injected
from menu_gui.api.menu import Menu

@injected
class MenuProviderService(IMenuProviderService):
    '''
    '''
    def __init__(self):
        self.menus = [
            { 'name': 'requests', 'display': 'API Requests' },
            { 'name': 'mockup', 'display': 'Mockup sample' }
        ]
        pass
    
    def getAll(self):
        menuList = []
        for i, menu in enumerate(self.menus):
            m = Menu()
            m.Id = i+1
            m.Name = menu['name']
            m.Display = menu['display']
            menuList.append(m)
        return menuList 
    