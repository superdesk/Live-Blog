'''
Created on Feb 2, 2012

@package ally core request
@copyright 2011 Sourcefabric o.p.s.
@license http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Contains the GUI configuration setup for the node presenter plugin.
'''

from ..gui_action.defaults import actionManagerService, menuAction
from ..gui_core.gui_core import publishGui, gui_folder_format
from ..plugin.registry import cdmGUI
from ally.container import ioc
from ally.internationalization import N_
from gui.action.api.action import Action

# --------------------------------------------------------------------

@ioc.start
def publishJS():
    publishGui('app')
    
@ioc.entity    
def requestAction():
    a = Action('request', N_('Request'), Parent=menuAction())
    a.ScriptPath = cdmGUI().getURI(gui_folder_format() % 'app/scripts/js/request.js')
    return a
    
@ioc.start
def actionRegister():
    actionManagerService().add(requestAction())
    actionManagerService().add(Action('demo', N_('Demo'), Parent=menuAction()))
    
