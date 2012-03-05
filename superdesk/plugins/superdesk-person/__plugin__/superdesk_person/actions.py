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
import __plugin__.superdesk_user.actions as userActions
from __plugin__.core_gui.gui_core import getPublishedGui

# --------------------------------------------------------------------

@ioc.entity   
def userAction():
    scriptPath = getPublishedGui('superdesk/person/scripts/js/user-update.js')
    return Action('person', Parent=userActions.modulesUpdateAction(), ScriptPath=scriptPath)

@ioc.start
def registerActions():
    actionManagerService().add(userAction())
