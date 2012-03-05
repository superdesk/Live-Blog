'''
Created on Feb 23, 2012

@package: ally actions gui 
@copyright: 2011 Sourcefabric o.p.s.
@license:  http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mihai Balaceanu


'''

from ally.container import ioc
from gui.action.api.action import IActionManagerService
from gui.action.impl.action import ActionManagerService
from __plugin__.plugin.registry import registerService

# --------------------------------------------------------------------

@ioc.entity
def actionManagerService() -> IActionManagerService:
    b = ActionManagerService()
    return b

@ioc.start
def register():
    registerService(actionManagerService())
