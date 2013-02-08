'''
Created on May 3rd, 2012

@package: Livedesk 
@copyright: 2011 Sourcefabric o.p.s.
@license:  http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mihai Balaceanu
'''

from ..gui_action.service import addAction
from ..gui_core.gui_core import publishedURI
from ..media_archive.actions import modulesTypesAction as mediaArchiveAction
from ally.container import ioc
from distribution.container import app
from gui.action.api.action import Action
from __plugin__.gui_security import acl
from superdesk.media_archive.api.image_data import IImageDataService
from superdesk.media_archive.api.image_info import IImageInfoService
from ally.internationalization import NC_

# --------------------------------------------------------------------

@ioc.entity   
def modulesAction():
    '''
    register image plugin on media archive actions
    '''
    return Action('image', Parent=mediaArchiveAction(), Script=publishedURI('media-archive-image/scripts/js/media-archive/'))

# --------------------------------------------------------------------

@app.deploy
def registerActions():
    addAction(modulesAction())
    
# --------------------------------------------------------------------

@ioc.entity
def rightMediaArchiveImageView():
    return acl.actionRight(NC_('security', 'IAM Image view'), NC_('security', '''
    Allows read only access to IAM Image items.''')) 

# --------------------------------------------------------------------
    
@acl.setup
def registerAclMediaArchiveImageView():
    rightMediaArchiveImageView().addActions(modulesAction()).all(IImageDataService).all(IImageInfoService)
