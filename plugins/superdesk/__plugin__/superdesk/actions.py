from ally.container import ioc, support
from ally.internationalization import NC_
from acl.right_action import RightAction
from gui.action.api.action import Action
from __plugin__.acl import gui
from __plugin__.gui_action import defaults
from __plugin__.gui_action.service import addAction
from superdesk.desk.api.desk import IDeskService

# -------------------------------------------------------------------

support.listenToEntities(Action, listeners=addAction)
support.loadAllEntities(Action)

# -------------------------------------------------------------------

@ioc.entity
def configAction() -> Action:
    return Action('config', Parent=defaults.menuAction(), Label=NC_('menu', 'Configure'))

@ioc.entity
def configView() -> RightAction:
    return gui.actionRight(NC_('security', 'Configure menu view'), NC_('security', 'Allows access to configure menu.'))

@gui.setup
def registerConfigView():
    r = configView()
    r.addActions(menuAction())
    r.allGet(IDeskService) # TODO it must be binded to a service, but there is none
