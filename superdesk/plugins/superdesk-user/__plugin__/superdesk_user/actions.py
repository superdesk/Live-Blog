'''
Created on Feb 23, 2012

@package: ally actions gui 
@copyright: 2011 Sourcefabric o.p.s.
@license:  http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mihai Balaceanu
'''

from ally.container import ioc
from actions_gui.api.action import Action
from __plugin__.actions_gui.service import actionManagerService
from __plugin__.actions_gui import defaults
from __plugin__.core_gui.gui_core import getPublishedGui
from ally.internationalization import translator

# --------------------------------------------------------------------

_ = translator(__name__)
# --------------------------------------------------------------------

@ioc.entity   
def menuAction():
    return Action('user', Parent=defaults.menuAction(), Label=_('Users'), ScriptPath=getPublishedGui('superdesk/user/scripts/js/menu.js'))

@ioc.entity   
def modulesAction():
    return Action('user', Parent=defaults.modulesAction())

@ioc.entity   
def modulesUpdateAction():
    return Action('update', Parent=modulesAction(), ScriptPath=getPublishedGui('superdesk/user/scripts/js/modules-update.js'))

@ioc.entity   
def modulesListAction():
    return Action('list', Parent=modulesAction(), ScriptPath=getPublishedGui('superdesk/user/scripts/js/modules-list.js'))

@ioc.start
def registerActions():
    actionManagerService().add(menuAction())
    actionManagerService().add(modulesAction())
    actionManagerService().add(modulesUpdateAction())
    actionManagerService().add(modulesListAction())
