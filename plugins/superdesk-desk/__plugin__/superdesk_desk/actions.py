from ally.container import ioc, support
from ally.internationalization import NC_ as _
from acl.right_action import RightAction
from gui.action.api.action import Action
from ..acl import gui
from ..gui_core.gui_core import publishedURI
from ..gui_action import defaults
from ..gui_action.service import addAction
from ..superdesk import actions as superdeskActions
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
    return Action('config:desks', Parent=superdeskActions.menuConfigAction(), Label=_('menu', 'Desks'),\
                  NavBar='config/desks', Script=publishedURI('superdesk-desk/scripts/actions/config.js'))

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
