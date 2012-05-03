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
    return Action('livedesk', Parent=defaults.menuAction(), Label=NC_('Menu', 'Live Blogs'),
                  ScriptPath=getPublishedGui('livedesk/scripts/js/menu-live-blogs.js'), Href='/livedesk/live-blogs')

@ioc.entity   
def modulesAction():
    return Action('livedesk', Parent=defaults.modulesAction())

@ioc.entity   
def modulesUpdateAction():
    return Action('add', Parent=modulesAction(), 
                  ScriptPath=getPublishedGui('livedesk/scripts/js/add-live-blogs.js'))

@ioc.start
def registerActions():
    actionManagerService().add(menuAction())
    actionManagerService().add(modulesAction())
    actionManagerService().add(modulesUpdateAction())
