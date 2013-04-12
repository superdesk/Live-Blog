'''
Created on Feb 23, 2012

@package: ally actions gui 
@copyright: 2011 Sourcefabric o.p.s.
@license:  http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mihai Balaceanu
'''

from .service import addAction
from ally.container import ioc, app
from gui.action.api.action import Action

# --------------------------------------------------------------------

@ioc.entity   
def menuAction():
    '''
    Register default action name: menu
    This node should contain actions to be used to generate the top navigation menu 
    '''
    return Action('menu')

@ioc.entity   
def modulesAction():
    '''
    Register default action name: modules
    This node should contain actions to be used inside the application 
    as main modules (whole page for edit/add/etc.)
    '''
    return Action('modules')

# --------------------------------------------------------------------

@ioc.entity
def modulesDashboardAction():
    '''
    Register default action name: modules.dashboard
    This node should contain actions to be used inside the dashboard of the application 
    as main modules (whole page for edit/add/etc.)
    '''
    return Action('dashboard', Parent=modulesAction())

@app.deploy
def registerActions():
    '''
    Register defined actions on the manager
    '''
    addAction(menuAction())
    addAction(modulesAction())
    addAction(modulesDashboardAction())
