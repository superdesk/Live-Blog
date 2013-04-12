'''
Created on Feb 23, 2012

@package: ally actions gui 
@copyright: 2011 Sourcefabric o.p.s.
@license:  http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mihai Balaceanu

Provides the services setup.
'''

from ally.container import support
from gui.action.api.action import IActionManagerService

# --------------------------------------------------------------------

def addAction(action):
    '''
    Add a new action.
    '''
    support.entityFor(IActionManagerService).add(action)
