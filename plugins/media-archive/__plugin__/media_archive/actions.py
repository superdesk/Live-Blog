'''
Created on May 3rd, 2012

@package: Livedesk 
@copyright: 2011 Sourcefabric o.p.s.
@license:  http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mihai Balaceanu
'''

from ..gui_action import defaults
from ..gui_action.service import addAction
from ..gui_core.gui_core import publishedURI
from ally.container import ioc
from ally.internationalization import NC_
from distribution.container import app
from ..gui_security import acl
from gui.action.api.action import Action
from superdesk.media_archive.api.meta_data import IMetaDataService,\
    IMetaDataUploadService
from superdesk.media_archive.api.meta_info import IMetaInfoService,\
    IMetaDataInfoService
from superdesk.media_archive.api.meta_type import IMetaTypeService
from superdesk.media_archive.api.query_criteria import IQueryCriteriaService

# --------------------------------------------------------------------

@ioc.entity   
def menuAction():
    return Action('media-archive', Parent=defaults.menuAction(), Label=NC_('menu', 'Media Archive'), NavBar='/media-archive',
                  Script=publishedURI('media-archive/scripts/js/menu.js'))

@ioc.entity   
def modulesAction():
    return Action('media-archive', Parent=defaults.modulesAction())

@ioc.entity   
def modulesAddAction():
    return Action('add', Parent=modulesAction(),
                  Script=publishedURI('media-archive/scripts/js/add-media.js'))

@ioc.entity   
def modulesMainAction():
    return Action('main', Parent=modulesAction(),
                  Script=publishedURI('media-archive/scripts/js/list.js'))

@ioc.entity   
def modulesConfigureAction():
    return Action('configure', Parent=modulesAction(),
                  Script=publishedURI('media-archive/scripts/js/configure-media-archive.js'))
 
# --------------------------------------------------------------------

@ioc.entity
def rightMediaArchiveView():
    return acl.actionRight(NC_('security', 'IAM view'), NC_('security', '''
    Allows read only access to IAM.''')) 

# --------------------------------------------------------------------

@app.deploy
def registerActions():
    addAction(menuAction())
    addAction(modulesAction())
    addAction(modulesAddAction())
    addAction(modulesMainAction())
    addAction(modulesConfigureAction())

# --------------------------------------------------------------------
    
@acl.setup
def registerAclMediaArchiveView():
    rightMediaArchiveView()\
        .addActions(menuAction(), modulesAction(), modulesMainAction(), modulesAddAction(), modulesConfigureAction())\
        .allGet(IMetaDataService)\
        .all(IMetaDataUploadService)\
        .all(IMetaInfoService)\
        .all(IMetaTypeService)\
        .all(IMetaDataInfoService)\
        .all(IQueryCriteriaService)
