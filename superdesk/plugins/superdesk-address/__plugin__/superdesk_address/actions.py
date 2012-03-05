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
from __plugin__.actions_gui import defaults
import __plugin__.superdesk_person.actions as personActions
from ally.internationalization import translator
from __plugin__.core_gui.gui_core import getPublishedGui

# --------------------------------------------------------------------

_ = translator(__name__)

# --------------------------------------------------------------------

@ioc.entity   
def menuAction():
    scriptPath = getPublishedGui('superdesk/address/scripts/js/menu.js')
    return Action('address', Parent=defaults.menuAction(), Label=_('Adresses'), ScriptPath=scriptPath)

@ioc.entity   
def modulesAction():
    scriptPath = getPublishedGui('superdesk/address/scripts/js/modules.js')
    return Action('address', Parent=defaults.modulesAction(), ScriptPath=scriptPath)

@ioc.entity
def personAction():
    scriptPath = getPublishedGui('superdesk/address/scripts/js/person-user.js')
    return Action('address', Parent=personActions.userAction(), ScriptPath=scriptPath)

@ioc.start
def registerActions():
    actionManagerService().add(menuAction())
    actionManagerService().add(modulesAction())
    actionManagerService().add(personAction())
