'''
Created on May 3rd, 2012

@package: Livedesk 
@copyright: 2011 Sourcefabric o.p.s.
@license:  http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mihai Balaceanu

Actions and acl action setups.
'''

from ..acl import gui
from ..gui_action import defaults
from ..gui_action.service import addAction
from ..gui_core.gui_core import publishedURI
from ..superdesk_security.acl import filterAuthenticated
from ..superdesk_user.actions import rightUserUpdate
from acl.right_action import RightAction
from ally.container import ioc, support
from ally.internationalization import NC_
from ally.support.util import ref
from gui.action.api.action import Action
from superdesk.media_archive.api.meta_data import IMetaDataService, \
    IMetaDataUploadService
from superdesk.media_archive.api.meta_info import IMetaInfoService, \
    IMetaDataInfoService
from superdesk.media_archive.api.meta_type import IMetaTypeService
from superdesk.media_archive.api.query_criteria import IQueryCriteriaService
    
# --------------------------------------------------------------------

support.listenToEntities(Action, listeners=addAction)
support.loadAllEntities(Action)

# --------------------------------------------------------------------

@ioc.entity   
def menuAction() -> Action:
    return Action('media-archive', Parent=defaults.menuAction(), Label=NC_('menu', 'Media Archive'), NavBar='/media-archive',
                  Script=publishedURI('media-archive/scripts/js/menu.js'))

@ioc.entity   
def modulesAction() -> Action:
    return Action('media-archive', Parent=defaults.modulesAction())

@ioc.entity   
def modulesAddAction() -> Action:
    return Action('add', Parent=modulesAction(),
                  Script=publishedURI('media-archive/scripts/js/add-media.js'))

@ioc.entity   
def modulesMainAction() -> Action:
    return Action('main', Parent=modulesAction(),
                  Script=publishedURI('media-archive/scripts/js/list.js'))
#TODO: check this action
#@ioc.entity   
#def modulesConfigureAction() -> Action:
#    return Action('configure', Parent=modulesAction(),
#                  Script=publishedURI('media-archive/scripts/js/configure-media-archive.js'))

@ioc.entity   
def modulesTypesAction() -> Action:
    return Action('types', Parent=modulesAction())
 
# --------------------------------------------------------------------

@ioc.entity
def rightMediaArchiveView() -> RightAction:
    return gui.actionRight(NC_('security', 'IAM view'), NC_('security', '''
    Allows read only access to IAM.'''))

@ioc.entity
def rightMediaArchiveUpload() -> RightAction:
    return gui.actionRight(NC_('security', 'IAM upload'), NC_('security', '''
    Allows upload access to IAM.'''))
    
# --------------------------------------------------------------------
    
@gui.setup
def registerAclMediaArchiveView():
    r = rightMediaArchiveView()
    r.addActions(menuAction(), modulesAction(), modulesMainAction(), modulesTypesAction())
    r.allGet(IMetaDataService, IMetaInfoService, IMetaTypeService, IMetaDataInfoService, IQueryCriteriaService)
    
@gui.setup
def registerAclMediaArchiveUpload():
    r = rightMediaArchiveUpload()
    r.addActions(modulesAddAction())
    r.all(IMetaDataUploadService, filter=filterAuthenticated())

@gui.setup
def registerAclUserUpdate():
    r = rightUserUpdate()
    r.add(ref(IMetaDataUploadService).insert, filter=filterAuthenticated())