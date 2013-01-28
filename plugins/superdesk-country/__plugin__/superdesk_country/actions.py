'''
Created on March 23, 2012

@package: ally actions gui 
@copyright: 2011 Sourcefabric o.p.s.
@license:  http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mihai Balaceanu
'''

from ..gui_action import defaults
from ..gui_action.service import addAction
from ..gui_core.gui_core import publishedURI
from ..gui_security import acl
from ally.container import ioc
from ally.internationalization import NC_
from distribution.container import app
from gui.action.api.action import Action
from superdesk.country.api.country import ICountryService

# --------------------------------------------------------------------

@ioc.entity   
def menuAction():
    return Action('country', Parent=defaults.menuAction(), Label=NC_('menu', 'Countries'),
                  Script=publishedURI('superdesk/country/scripts/js/menu.js'), NavBar='/country/list')

@ioc.entity   
def modulesAction():
    return Action('country', Parent=defaults.modulesAction())

#TODO: check with Billy about the country rights
#@ioc.entity   
#def modulesUpdateAction():
#    return Action('update', Parent=modulesAction(), Script=publishedURI('superdesk/country/scripts/js/update.js'))

@ioc.entity   
def modulesListAction():
    return Action('list', Parent=modulesAction(), Script=publishedURI('superdesk/country/scripts/js/list.js'))

#@ioc.entity   
#def modulesAddAction():
#    return Action('add', Parent=modulesAction(), Script=publishedURI('superdesk/country/scripts/js/add.js'))

# --------------------------------------------------------------------

@ioc.entity
def rightCountryView():
    return acl.actionRight(NC_('security', 'Countries view'), NC_('security', '''
    Allows for the viewing of countries available in the application.'''))

#@ioc.entity
#def rightCountryModify():
#    return acl.actionRight(NC_('security', 'Countries modify'), NC_('security', '''
#    Allows for the viewing and modifying of countries available in the application.'''))

# --------------------------------------------------------------------

@app.deploy
def registerActions():
    addAction(menuAction())
    addAction(modulesAction())
    #addAction(modulesUpdateAction())
    addAction(modulesListAction())
    #addAction(modulesAddAction())

#@acl.setup
#def registerAclCountryView():
#    rightCountryView().addActions(menuAction(), modulesAction(), modulesListAction())\
#    .allGet(ICountryService)
    
#@acl.setup
#def registerAclCountryModify():
#    rightUserUpdate().addActions(menuAction(), modulesAction(), modulesListAction(), modulesUpdateAction())\
#    .allGet(IUserService).allUpdate(IUserService)
