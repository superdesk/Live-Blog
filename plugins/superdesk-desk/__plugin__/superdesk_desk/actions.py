from ally.container import ioc, support
from ally.internationalization import NC_ as _
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
    script=publishedURI('superdesk-desk/scripts/config.js')
    return Action('desks', Parent=superdesk.menuAction(), Label=_('menu', 'Desks'), NavBar='config/desks', Script=script)

@ioc.entity
def blogConfigView() -> RightAction:
    return gui.actionRight(_('security', 'Blog Config View'), _('security', 'Allows desks configuration.'))

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
