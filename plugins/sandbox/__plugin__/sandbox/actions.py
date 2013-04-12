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
from ..gui_action.service import addAction
from ..gui_action import defaults
from ..gui_core.gui_core import publishedURI

# --------------------------------------------------------------------

@ioc.entity   
def menuAction():
    return Action('sandbox', Parent=defaults.menuAction(), Label=NC_('Menu', 'Sandbox'),
                  Script=publishedURI('superdesk/sandbox/scripts/js/menu-sandbox.js'))
@ioc.entity   
def subMenuAction():
    return Action('submenu', Parent=menuAction(), 
                  Script=publishedURI('superdesk/sandbox/scripts/js/submenu-sandbox.js'))

@ioc.entity   
def modulesAction():
    return Action('sandbox', Parent=defaults.modulesAction(), Script=publishedURI('superdesk/sandbox/scripts/js/sandbox.js'))

@ioc.start
def registerActions():
    addAction(menuAction())
    addAction(subMenuAction())
    addAction(modulesAction())
