'''
Created on May 3rd, 2012

@package: Livedesk 
@copyright: 2011 Sourcefabric o.p.s.
@license:  http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mihai Balaceanu
'''

from ..gui_action import defaults
from ..gui_action.service import addAction
from ..gui_core.gui_core import publishedURI
from ally.container import ioc
from ally.internationalization import NC_
from distribution.container import app
from gui.action.api.action import Action

# --------------------------------------------------------------------

@ioc.entity   
def menuAction():
    return Action('media-archive', Parent=defaults.menuAction(), Label=NC_('menu', 'Media Archive'), NavBar='/media-archive',
                  Script=publishedURI('media-archive/scripts/js/menu.js'))

# @ioc.entity   
# def subMenuAction():
#    return Action('submenu', Parent=menuAction(), ScriptPath=getPublishedGui('media-archive/scripts/js/submenu-media-archive.js'))

@ioc.entity   
def modulesAction():
    return Action('media-archive', Parent=defaults.modulesAction())

@ioc.entity   
def modulesAddAction():
    return Action('add', Parent=modulesAction(),
                  Script=publishedURI('media-archive/scripts/js/add-media.js'))

@ioc.entity   
def modulesMainAction():
    return Action('main', Parent=modulesAction(),
                  Script=publishedURI('media-archive/scripts/js/list.js'))

@ioc.entity   
def modulesConfigureAction():
    return Action('configure', Parent=modulesAction(),
                  Script=publishedURI('media-archive/scripts/js/configure-media-archive.js'))

@app.deploy
def registerActions():
    addAction(menuAction())
    addAction(modulesAction())
    addAction(modulesAddAction())
    addAction(modulesMainAction())
    addAction(modulesConfigureAction())
    
