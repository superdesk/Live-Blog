from ally.container import ioc, support
from ally.internationalization import NC_
from ally.api.config import service, model
from ally.support.api.entity import Entity, IEntityGetService
from acl.right_action import RightAction
from gui.action.api.action import Action
from __plugin__.acl import gui
from __plugin__.gui_core.gui_core import publishedURI
from __plugin__.gui_action.service import addAction
import __plugin__.superdesk.actions as superdesk
from superdesk.desks.api.desks import IDesksService

support.listenToEntities(Action, listeners=addAction)
support.loadAllEntities(Action)

@ioc.entity
def menuAction() -> Action:
    return Action('desks', Parent=superdesk.menuAction(), Label=NC_('menu', 'Desks'), NavBar='/config/desks', Script=publishedURI('superdesk-desk/scripts/configmenu.js'))

@ioc.entity
def blogConfigView() -> RightAction:
    return gui.actionRight(NC_('security', 'Blog Config View'), NC_('security', 'Allows desks configurationt.'))

@model
class Menu(Entity):
    pass

@service((Entity, Menu))
class IMenuService(IEntityGetService):
    pass


@gui.setup
def registerConfigView():
    r = blogConfigView()
    r.addActions(menuAction())
    r.allGet(IDesksService)
