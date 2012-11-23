'''
Created on May 3rd, 2012

@package: Livedesk 
@copyright: 2011 Sourcefabric o.p.s.
@license:  http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mihai Balaceanu
'''

from ally.container import ioc
from gui.action.api.action import Action
from ..gui_action.service import actionManagerService
from ..gui_core.gui_core import getPublishedGui
from ..media_archive.actions import modulesAction as mediaArchiveAction

# --------------------------------------------------------------------

@ioc.entity   
def modulesAction():
    '''
    register image plugin on media archive actions
    '''
    return Action('image', Parent=mediaArchiveAction(), ScriptPath=getPublishedGui('media-archive-image/scripts/js/media-archive/'))

@ioc.start
def registerActions():
    actionManagerService().add(modulesAction())
    
