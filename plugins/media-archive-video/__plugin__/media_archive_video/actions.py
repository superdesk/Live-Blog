'''
Created on May 3rd, 2012

@package: Livedesk 
@copyright: 2011 Sourcefabric o.p.s.
@license:  http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mihai Balaceanu

Actions and acl action setups.
'''

from ..acl import gui
from ..gui_action.service import addAction
from ..gui_core.gui_core import publishedURI
from ..media_archive.actions import modulesAction as mediaArchiveAction
from ally.container import ioc, support
from gui.action.api.action import Action
from superdesk.media_archive.api.video_data import IVideoDataService
from superdesk.media_archive.api.video_info import IVideoInfoService
from ally.internationalization import NC_
from acl.right_action import RightAction
    
# --------------------------------------------------------------------

support.listenToEntities(Action, listeners=addAction)
support.loadAllEntities(Action)

# --------------------------------------------------------------------

@ioc.entity   
def modulesAction() -> Action:
    '''
    register image plugin on media archive actions
    '''
    return Action('video', Parent=mediaArchiveAction(), Script=publishedURI('media-archive-video/scripts/js/media-archive/'))
     
# --------------------------------------------------------------------

@ioc.entity
def rightMediaArchiveVideoView() -> RightAction:
    return gui.actionRight(NC_('security', 'IAM Video view'), NC_('security', '''
    Allows read only access to IAM Video items.''')) 

# --------------------------------------------------------------------
    
@gui.setup
def registerAclMediaArchiveVideoView():
    r = rightMediaArchiveVideoView()
    r.addActions(modulesAction())
    r.all(IVideoDataService, IVideoInfoService)
   
