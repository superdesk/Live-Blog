'''
Created on Feb 23, 2012

@package: ally actions gui 
@copyright: 2011 Sourcefabric o.p.s.
@license:  http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mihai Balaceanu
'''

from ally.container import ioc
from actions_gui.api.action import Action
from __plugin__.actions_gui.service import actionManagerService

# --------------------------------------------------------------------

@ioc.entity   
def modulesAction():
    '''
    Register default action name: modules
    This node should contain actions to be used inside the application 
    as main modules (whole page for edit/add/etc.)
    '''
    return Action('modules')

@ioc.entity   
def menuAction():
    '''
    Register default action name: modules
    This node should contain actions to be used to generate the top navigation menu 
    '''
    return Action('menu')

@ioc.start
def registerActions():
    '''
    Register defined actions on the manager
    '''
    actionManagerService().add(menuAction())
    actionManagerService().add(modulesAction())
