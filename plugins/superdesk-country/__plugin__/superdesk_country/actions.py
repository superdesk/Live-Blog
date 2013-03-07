'''
Created on March 23, 2012

@package: ally actions gui
@copyright: 2011 Sourcefabric o.p.s.
@license:  http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mihai Balaceanu

Actions and acl action setups.
'''

from ..acl import gui
from ..gui_action import defaults
from ..gui_action.service import addAction
from ..gui_core.gui_core import publishedURI
from acl.right_action import RightAction
from ally.container import ioc, support
from ally.internationalization import NC_
from gui.action.api.action import Action
    
# --------------------------------------------------------------------

support.listenToEntities(Action, listeners=addAction)
support.loadAllEntities(Action)

# --------------------------------------------------------------------

@ioc.entity
def menuAction() -> Action:
    return Action('country', Parent=defaults.menuAction(), Label=NC_('menu', 'Countries'),
                  Script=publishedURI('superdesk/country/scripts/js/menu.js'), NavBar='/country/list')

@ioc.entity
def modulesAction() -> Action:
    return Action('country', Parent=defaults.modulesAction())

# TODO: check with Billy about the country rights
# @ioc.entity
# def modulesUpdateAction():
#    return Action('update', Parent=modulesAction(), Script=publishedURI('superdesk/country/scripts/js/update.js'))

@ioc.entity
def modulesListAction() -> Action:
    return Action('list', Parent=modulesAction(), Script=publishedURI('superdesk/country/scripts/js/list.js'))

# @ioc.entity
# def modulesAddAction():
#    return Action('add', Parent=modulesAction(), Script=publishedURI('superdesk/country/scripts/js/add.js'))

# --------------------------------------------------------------------

@ioc.entity
def rightCountryView() -> RightAction:
    return gui.actionRight(NC_('security', 'Countries view'), NC_('security', '''
    Allows for the viewing of countries available in the application.'''))

# @ioc.entity
# def rightCountryModify():
#    return acl.actionRight(NC_('security', 'Countries modify'), NC_('security', '''
#    Allows for the viewing and modifying of countries available in the application.'''))

# --------------------------------------------------------------------

# @gui.setup
# def registerAclCountryView():
#    r = rightCountryView()
#    r.addActions(menuAction(), modulesAction(), modulesListAction())
#    r.allGet(ICountryService)

# @gui.setup
# def registerAclCountryModify():
#    r = rightUserUpdate()
#    r.addActions(menuAction(), modulesAction(), modulesListAction(), modulesUpdateAction())
#    r.allGet(IUserService).allUpdate(IUserService)
