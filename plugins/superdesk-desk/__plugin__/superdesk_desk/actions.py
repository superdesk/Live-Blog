from ally.container import ioc, support
from ally.internationalization import NC_ as _
from ally.api.config import service, model
from ally.support.api.entity import Entity, IEntityGetService
from acl.right_action import RightAction
from gui.action.api.action import Action
from __plugin__.acl import gui
from __plugin__.gui_core.gui_core import publishedURI
from ..gui_action import defaults
from ..gui_action.service import addAction
from ..superdesk import actions as superdeskActions
import __plugin__.superdesk.actions as superdesk
from superdesk.desk.api.desk import IDeskService

support.listenToEntities(Action, listeners=addAction)
support.loadAllEntities(Action)

@ioc.entity
def configMenuAction() -> Action:
    script=publishedURI('superdesk-desk/scripts/config.js')
    return Action('desks', Parent=superdeskActions.configAction(), Label=_('menu', 'Desks'), NavBar='/config/desks', Script=script)

@ioc.entity
def deskConfigView() -> RightAction:
    return gui.actionRight(_('security', 'Desk Config View'), _('security', 'Allows desks configuration.'))

@ioc.entity   
def modulesAction() -> Action:
    return Action('desks', Parent=defaults.modulesAction())

@ioc.entity   
def modulesMainAction() -> Action:
    return Action('main', Parent=modulesAction(), Script=publishedURI('superdesk/desks/scripts/js/main.js'))

@ioc.entity   
def modulesTasksAction() -> Action:
    return Action('tasks', Parent=modulesAction())

@ioc.entity   
def modulesAddTaskAction() -> Action:
    return Action('add', Parent=modulesTasksAction(), Script=publishedURI('superdesk/desks/scripts/js/task/add.js'))

@ioc.entity   
def modulesEditTaskAction() -> Action:
    return Action('edit', Parent=modulesTasksAction(), Script=publishedURI('superdesk/desks/scripts/js/task/edit.js'))

@ioc.entity   
def modulesSingleDeskAction() -> Action:
    return Action('single', Parent=modulesAction(), Script=publishedURI('superdesk/desks/scripts/js/desk/single.js'))

# --------------------------------------------------------------------

@ioc.entity
def rightDesksView() -> RightAction:
    return gui.actionRight(NC_('security', 'Desks'), NC_('security', ''''''))

# --------------------------------------------------------------------
    
@gui.setup
def registerConfigView():
    r = deskConfigView()
    r.addActions(configMenuAction())
    r.allGet(IDeskService)
