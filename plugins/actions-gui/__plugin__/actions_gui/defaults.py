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
def menuAction():
    return Action('menu')

@ioc.start
def registerActions():
    actionManagerService().add(menuAction())
