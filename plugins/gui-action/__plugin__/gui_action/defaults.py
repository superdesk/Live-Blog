'''
Created on Feb 23, 2012

@package: ally actions gui 
@copyright: 2011 Sourcefabric o.p.s.
@license:  http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mihai Balaceanu
'''

from .service import actionManagerService
from ally.container import ioc
from gui.action.api.action import Action

# --------------------------------------------------------------------

@ioc.entity   
def menuAction():
    return Action('menu')

@ioc.start
def registerActions():
    actionManagerService().add(menuAction())
