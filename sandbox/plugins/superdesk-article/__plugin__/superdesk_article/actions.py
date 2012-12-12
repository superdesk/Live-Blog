'''
Created on May 3rd, 2012

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
    return Action('article-demo', Parent=defaults.menuAction(), Label=NC_('Menu', 'Articles') )

@ioc.entity   
def subMenuAction():
    return Action('submenu', Parent=menuAction(), ScriptPath=getPublishedGui('superdesk/article/scripts/js/submenu.js'))

@ioc.entity   
def modulesAction():
    return Action('article-demo', Parent=defaults.modulesAction())

@ioc.entity   
def modulesEditAction():
    return Action('edit', Parent=modulesAction(), 
                  ScriptPath=getPublishedGui('superdesk/article/scripts/js/edit.js'))

@ioc.start
def registerActions():
    actionManagerService().add(menuAction())
    actionManagerService().add(subMenuAction())
    actionManagerService().add(modulesAction())
    actionManagerService().add(modulesEditAction())
