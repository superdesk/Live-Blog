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
    return Action('media-archive', Parent=defaults.menuAction(), Label=NC_('Menu', 'Media Archive'), Href='/media-archive', 
                  ScriptPath=getPublishedGui('media-archive/scripts/js/menu-media-archive.js'))

#@ioc.entity   
#def subMenuAction():
#    return Action('submenu', Parent=menuAction(), ScriptPath=getPublishedGui('media-archive/scripts/js/submenu-media-archive.js'))

@ioc.entity   
def modulesAction():
    return Action('media-archive', Parent=defaults.modulesAction())

@ioc.entity   
def modulesAddAction():
    return Action('add', Parent=modulesAction(), 
                  ScriptPath=getPublishedGui('media-archive/scripts/js/add-media.js'))

@ioc.entity   
def modulesMainAction():
    return Action('main', Parent=modulesAction(), 
                  ScriptPath=getPublishedGui('media-archive/scripts/js/media-archive-main.js'))

@ioc.entity   
def modulesConfigureAction():
    return Action('configure', Parent=modulesAction(), 
                  ScriptPath=getPublishedGui('media-archive/scripts/js/configure-media-archive.js'))

@ioc.start
def registerActions():
    actionManagerService().add(menuAction())
    actionManagerService().add(modulesAction())
    actionManagerService().add(modulesAddAction())
    actionManagerService().add(modulesMainAction())
    actionManagerService().add(modulesConfigureAction())
    
