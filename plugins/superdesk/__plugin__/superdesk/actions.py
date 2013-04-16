from ally.container import ioc, support
from ally.internationalization import NC_
from ally.api.config import service, model
from ally.support.api.entity import Entity, IEntityGetService
from acl.right_action import RightAction
from gui.action.api.action import Action
from __plugin__.acl import gui
from __plugin__.gui_action import defaults
from __plugin__.gui_action.service import addAction
from superdesk.desks.api.desks import IDesksService

support.listenToEntities(Action, listeners=addAction)
support.loadAllEntities(Action)

@ioc.entity
def menuAction() -> Action:
    return Action('config', Parent=defaults.menuAction(), Label=NC_('menu', 'Configure'), NavBar='/config')

@ioc.entity
def configView() -> RightAction:
    return gui.actionRight(NC_('security', 'Config View'), NC_('security', 'Allows read only access to users for livedesk.'))

@gui.setup
def registerConfigView():
    r = configView()
    r.addActions(menuAction())
    r.allGet(IDesksService) # TODO it must be binded to a service, but there is none
