'''
Created on Feb 2, 2012

@package: introspection request
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mihai Balaceanu

Registered actions for request plugin
'''

from ..acl import gui
from ..gui_action import defaults
from ..gui_action.service import addAction
from ..gui_core.gui_core import publishedURI
from acl.right_action import RightAction
from admin.introspection.api.component import IComponentService
from admin.introspection.api.plugin import IPluginService
from admin.introspection.api.request import IRequestService
from ally.container import ioc, support
from ally.internationalization import NC_
from gui.action.api.action import Action

# --------------------------------------------------------------------

support.listenToEntities(Action, listeners=addAction)
support.loadAllEntities(Action)

# --------------------------------------------------------------------

@ioc.entity
def menuAction() -> Action:
    return Action('request', NC_('menu', 'Request'), Parent=defaults.menuAction(),
                  NavBar='/api-requests', Script=publishedURI('superdesk/request/scripts/js/menu.js'))

@ioc.entity
def modulesAction() -> Action:
    return Action('request', Parent=defaults.modulesAction())

@ioc.entity
def modulesListAction() -> Action:
    return Action('list', Parent=modulesAction(), Script=publishedURI('superdesk/request/scripts/js/list.js'))

# --------------------------------------------------------------------

@ioc.entity
def rightRequestsInspection() -> RightAction:
    return gui.actionRight(NC_('security', 'Requests inspection'), NC_('security', '''
    Allows for the viewing of all possible requests that can be made on the REST server, also the plugins and components
    that are part of the application are also visible.'''))

# --------------------------------------------------------------------

@gui.setup
def registerAcl():
    r = rightRequestsInspection()
    r.addActions(menuAction(), modulesAction(), modulesListAction())
    r.allGet(IComponentService, IPluginService, IRequestService)
