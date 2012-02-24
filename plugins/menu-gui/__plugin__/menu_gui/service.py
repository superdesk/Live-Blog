'''
Created on Feb 23, 2012

@author: mihaibalaceanu
'''

from ally.container import ioc
from menu_gui.api.menu import IMenuProviderService
from menu_gui.impl.menu import MenuProviderService
from __plugin__.plugin.registry import services

#support.createEntitySetup('gui_menu.api.**.I*Service', 'gui_menu.impl.*.*Service')

@ioc.entity
def menuService() -> IMenuProviderService:
    return MenuProviderService()

@ioc.before(services)
def updateServices():
    services().append(menuService())