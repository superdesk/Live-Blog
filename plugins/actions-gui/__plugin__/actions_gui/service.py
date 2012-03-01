'''
Created on Feb 23, 2012

@package: ally actions gui 
@copyright: 2011 Sourcefabric o.p.s.
@license:  http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mihai Balaceanu


'''

from ally.container import ioc
from __plugin__.plugin.registry import services
from actions_gui.api.action import IActionManagerService
from actions_gui.impl.action import ActionManagerService

# --------------------------------------------------------------------

@ioc.entity
def actionManagerService() -> IActionManagerService:
    return ActionManagerService()
    
@ioc.before(services)
def updateServices():
    services().append(actionManagerService())
