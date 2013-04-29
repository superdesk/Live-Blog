from ally.container import ioc, support
from ally.internationalization import NC_ as _
from ally.api.config import service, model
from ally.support.api.entity import Entity, IEntityGetService
from acl.right_action import RightAction
from gui.action.api.action import Action
from __plugin__.acl import gui
from __plugin__.gui_core.gui_core import publishedURI
from __plugin__.gui_action import defaults
from __plugin__.gui_action.service import addAction
import __plugin__.superdesk.actions as superdesk
from superdesk.desk.api.desk import IDeskService

support.listenToEntities(Action, listeners=addAction)
support.loadAllEntities(Action)

@ioc.entity
def desksMenuAction() -> Action:
    return Action('desks', Parent=defaults.menuAction(), Label=_('menu', 'Desks'))

@ioc.entity
def desksListMenuAction() -> Action:
    script = publishedURI('superdesk-desk/scripts/actions/desks.js')
    return Action('desks:list', Parent=desksMenuAction(), Script=script)

@ioc.entity
def configMenuAction() -> Action:
    script = publishedURI('superdesk-desk/scripts/actions/config.js')
    return Action('config:desks', Parent=superdesk.menuAction(), Label=_('menu', 'Desks'), NavBar='config/desks', Script=script)

@ioc.entity
def deskView() -> RightAction:
    return gui.actionRight(_('security', 'Desk View'), _('security', 'Allows desks view.'))

@ioc.entity
def deskConfigView() -> RightAction:
    return gui.actionRight(_('security', 'Desk Config View'), _('security', 'Allows desks configuration.'))

@gui.setup
def registerConfigView():
    r = deskConfigView()
    r.addActions(configMenuAction())
    r.allGet(IDeskService)

@gui.setup
def registerDeskView():
    r = deskView()
    r.addActions(desksMenuAction(), desksListMenuAction())
    r.allGet(IDeskService)
