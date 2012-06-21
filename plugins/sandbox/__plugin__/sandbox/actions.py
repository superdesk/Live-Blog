'''
Created on Jun 18, 2012

@package: Livedesk 
@copyright: 2011 Sourcefabric o.p.s.
@license:  http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mihai Balaceanu
'''

from ally.container import ioc
from ally.internationalization import NC_
from gui.action.api.action import Action
from ..gui_action.service import actionManagerService
from ..gui_action import defaults
from ..gui_core.gui_core import getPublishedGui

# --------------------------------------------------------------------

@ioc.entity   
def menuAction():
    return Action('sandbox', Parent=defaults.menuAction(), Label=NC_('Menu', 'Sandbox'),
                  ScriptPath=getPublishedGui('superdesk/sandbox/scripts/js/menu-sandbox.js'))
@ioc.entity   
def modulesAction():
    return Action('sandbox', Parent=defaults.modulesAction(), ScriptPath=getPublishedGui('superdesk/sandbox/scripts/js/sandbox.js'))

@ioc.start
def registerActions():
    actionManagerService().add(menuAction())
    actionManagerService().add(modulesAction())
