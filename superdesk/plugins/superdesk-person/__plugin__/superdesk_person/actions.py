'''
Created on Feb 23, 2012

@package: ally actions gui 
@copyright: 2011 Sourcefabric o.p.s.
@license:  http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mihai Balaceanu
'''

from ally.container import ioc
from gui.action.api.action import Action
import __plugin__.superdesk_user.actions as userActions
from ..gui_core.gui_core import getPublishedGui
from ..gui_action.service import actionManagerService

# --------------------------------------------------------------------

@ioc.entity   
def userAction():
    scriptPath = getPublishedGui('superdesk/person/scripts/js/user-update.js')
    return Action('person', Parent=userActions.modulesUpdateAction(), ScriptPath=scriptPath)

@ioc.start
def registerActions():
    actionManagerService().add(userAction())
