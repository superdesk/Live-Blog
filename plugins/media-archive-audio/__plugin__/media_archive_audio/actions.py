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

# --------------------------------------------------------------------

@ioc.entity   
def modulesAction():
    '''
    register image plugin on media archive actions
    '''
    return Action('audio', Parent=mediaArchiveAction(), Script=publishedURI('media-archive-audio/scripts/js/media-archive/'))

@app.deploy
def registerActions():
    addAction(modulesAction())
    
