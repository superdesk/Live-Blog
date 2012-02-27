'''
Created on Feb 2, 2012

@package ally core request
@copyright 2011 Sourcefabric o.p.s.
@license http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Contains the GUI configuration setup for the node presenter plugin.
'''

from ally.container import ioc
from __plugin__.core_gui.gui_core import publishGui
from __plugin__.menu_gui.service import actionManagerService, menuAction
from menu_gui.api.action import Action

# --------------------------------------------------------------------

@ioc.start
def publishJS():
    publishGui('app')
    
@ioc.entity    
def requestAction():
    return Action('request', menuAction())
    
@ioc.start
def actionRegister():
    actionManagerService().add(requestAction())