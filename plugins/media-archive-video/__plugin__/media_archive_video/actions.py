'''
Created on May 3rd, 2012

@package: Livedesk 
@copyright: 2011 Sourcefabric o.p.s.
@license:  http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mihai Balaceanu
'''

from ..gui_action.service import addAction
from ..gui_core.gui_core import publishedURI
from ..media_archive.actions import modulesAction as mediaArchiveAction
from ally.container import ioc
from distribution.container import app
from gui.action.api.action import Action
from superdesk.media_archive.api.video_data import IVideoDataService
from superdesk.media_archive.api.video_info import IVideoInfoService
from ally.internationalization import NC_
from __plugin__.gui_security import acl

# --------------------------------------------------------------------

@ioc.entity   
def modulesAction():
    '''
    register image plugin on media archive actions
    '''
    return Action('video', Parent=mediaArchiveAction(), Script=publishedURI('media-archive-video/scripts/js/media-archive/'))

@app.deploy
def registerActions():
    addAction(modulesAction())
     
# --------------------------------------------------------------------

@ioc.entity
def rightMediaArchiveVideoView():
    return acl.actionRight(NC_('security', 'IAM Video view'), NC_('security', '''
    Allows read only access to IAM Video items.''')) 

# --------------------------------------------------------------------
    
@acl.setup
def registerAclMediaArchiveVideoView():
    rightMediaArchiveVideoView().addActions(modulesAction()).all(IVideoDataService).all(IVideoInfoService)
   
