'''
Created on Feb 23, 2012

@author: mihaibalaceanu
'''

from ally.container import ioc
from menu_gui.api.menu import IMenuProviderService
from menu_gui.impl.menu import MenuProviderService
from __plugin__.plugin.registry import services
from menu_gui.api.action import IActionManagerService, Action
from menu_gui.impl.action import ActionManagerService


#@ioc.entity
#def menuService() -> IMenuProviderService:
#    return MenuProviderService()

@ioc.entity
def actionManagerService() -> IActionManagerService:
    return ActionManagerService()
    
@ioc.before(services)
def updateServices():
    #services().append(menuService())
    services().append(actionManagerService())
 
@ioc.entity   
def menuAction():
    return Action('menu')

@ioc.start
def registerActions():
    actionManagerService().add(menuAction())    