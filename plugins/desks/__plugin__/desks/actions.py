'''
Created on May 3rd, 2012

@package: Superdesk 
@copyright: 2011 Sourcefabric o.p.s.
@license:  http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mihai Balaceanu

'''

from ..acl import gui
from ..gui_action import defaults
from ..gui_action.service import addAction
from ..gui_core.gui_core import publishedURI
from acl.right_action import RightAction
from ally.container import ioc, support
from ally.internationalization import NC_
from gui.action.api.action import Action
from superdesk.desks.api.desks import IDesksService
    
# --------------------------------------------------------------------

support.listenToEntities(Action, listeners=addAction)
support.loadAllEntities(Action)

# --------------------------------------------------------------------

@ioc.entity   
def menuAction() -> Action:
    return Action('desks', Parent=defaults.menuAction(), Label=NC_('menu', 'Desks'), NavBar='/desks',
                  Script=publishedURI('superdesk/desks/scripts/js/menu.js'))

@ioc.entity   
def modulesAction() -> Action:
    return Action('desks', Parent=defaults.modulesAction())

@ioc.entity   
def modulesMainAction() -> Action:
    return Action('main', Parent=modulesAction(), Script=publishedURI('superdesk/desks/scripts/js/main.js'))

# --------------------------------------------------------------------

@ioc.entity
def rightDesksView() -> RightAction:
    return gui.actionRight(NC_('security', 'Desks'), NC_('security', ''''''))

# --------------------------------------------------------------------
    
@gui.setup
def registerAclMediaArchiveView():
    r = rightDesksView()
    r.addActions(menuAction(), modulesAction(), modulesMainAction())
    r.allGet(IDesksService)
