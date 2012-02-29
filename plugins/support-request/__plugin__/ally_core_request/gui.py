'''
Created on Feb 2, 2012

@package ally core request
@copyright 2011 Sourcefabric o.p.s.
@license http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Contains the GUI configuration setup for the node presenter plugin.
'''

from ally.container import ioc
from __plugin__.core_gui.gui_core import publishGui, gui_folder_format
from __plugin__.actions_gui.defaults import actionManagerService, menuAction
from actions_gui.api.action import Action
from __plugin__.plugin.registry import cdmGUI
from ally.internationalization import translator

# --------------------------------------------------------------------

_ = translator(__name__)

# --------------------------------------------------------------------

@ioc.start
def publishJS():
    publishGui('app')
    
@ioc.entity    
def requestAction():
    a = Action('request', _('Request'), Parent=menuAction())
    a.ScriptPath = cdmGUI().getURI(gui_folder_format() % 'app/scripts/js/request.js')
    return a
    
@ioc.start
def actionRegister():
    actionManagerService().add(requestAction())
    actionManagerService().add(Action('demo', _('Demo'), Parent=menuAction()))
    