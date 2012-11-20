'''
Created on Feb 23, 2012

@package: ally actions gui 
@copyright: 2011 Sourcefabric o.p.s.
@license:  http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mihai Balaceanu
'''

from ally.container import ioc
from gui.action.api.action import Action
from ..gui_action.service import actionManagerService
from ..gui_action import defaults
from ..gui_core.gui_core import getPublishedGui
from ally.internationalization import NC_

# --------------------------------------------------------------------

@ioc.entity   
def menuAction():
    return Action('user', Parent=defaults.menuAction(), Label=NC_('Menu', 'Users'), Href='/users',
                  ScriptPath=getPublishedGui('superdesk/user/scripts/js/menu.js'))

@ioc.entity   
def modulesAction():
    return Action('user', Parent=defaults.modulesAction())

#@ioc.entity   
#def modulesUpdateAction():
#    return Action('update', Parent=modulesAction(), ScriptPath=getPublishedGui('superdesk/user/scripts/js/modules-update.js'))

@ioc.entity   
def modulesListAction():
    return Action('list', Parent=modulesAction(), ScriptPath=getPublishedGui('superdesk/user/scripts/js/list.js'))

#@ioc.entity   
#def modulesAddAction():
#    return Action('add', Parent=modulesAction(), ScriptPath=getPublishedGui('superdesk/user/scripts/js/modules-add.js'))

@ioc.start
def registerActions():
    actionManagerService().add(menuAction())
    actionManagerService().add(modulesAction())
    #actionManagerService().add(modulesUpdateAction())
    actionManagerService().add(modulesListAction())
    #actionManagerService().add(modulesAddAction())
