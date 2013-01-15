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
    return Action('livedesk', Parent=defaults.menuAction(), Label=NC_('Menu', 'Live Blogs') ) # ,
                  #ScriptPath=getPublishedGui('livedesk/scripts/js/menu-live-blogs.js'))

#def menuTestAction():
#    return Action('livedesk-test', Parent=defaults.menuAction(), Label=NC_('Menu', 'Test'),
#                  ScriptPath=getPublishedGui('livedesk/scripts/js/test.js'))

@ioc.entity   
def subMenuAction():
    return Action('submenu', Parent=menuAction(), ScriptPath=getPublishedGui('livedesk/scripts/js/submenu-live-blogs.js'))

@ioc.entity   
def modulesAction():
    return Action('livedesk', Parent=defaults.modulesAction())

@ioc.entity   
def dashboardAction():
    return Action('livedesk', Parent=defaults.modulesDashboardAction(), ScriptPath=getPublishedGui('livedesk/scripts/js/dashboard.js'))

@ioc.entity   
def modulesAddAction():
    return Action('add', Parent=modulesAction(), 
                  ScriptPath=getPublishedGui('livedesk/scripts/js/add-live-blogs.js'))
@ioc.entity   
def modulesEditAction():
    return Action('edit', Parent=modulesAction(), 
                  ScriptPath=getPublishedGui('livedesk/scripts/js/edit-live-blogs.js'))

@ioc.entity   
def modulesConfigureAction():
    return Action('configure', Parent=modulesAction(), 
                  ScriptPath=getPublishedGui('livedesk/scripts/js/configure-blog.js'))
@ioc.entity   
def modulesManageCollaboratorsAction():
    return Action('manage-collaborators', Parent=modulesAction(), 
                  ScriptPath=getPublishedGui('livedesk/scripts/js/manage-collaborators.js'))
@ioc.entity   
def modulesArchiveAction():
    return Action('archive', Parent=modulesAction(), 
                  ScriptPath=getPublishedGui('livedesk/scripts/js/archive.js'))

@ioc.start
def registerActions():
    actionManagerService().add(menuAction())
    actionManagerService().add(subMenuAction())
    actionManagerService().add(modulesAction())
    actionManagerService().add(dashboardAction())
    actionManagerService().add(modulesAddAction())
    actionManagerService().add(modulesEditAction())
    actionManagerService().add(modulesConfigureAction())
    actionManagerService().add(modulesManageCollaboratorsAction())
    actionManagerService().add(modulesArchiveAction())
    
