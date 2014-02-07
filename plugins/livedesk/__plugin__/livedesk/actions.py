'''
Created on May 3rd, 2012

@package: Livedesk
@copyright: 2011 Sourcefabric o.p.s.
@license:  http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mihai Balaceanu
'''

from ..acl import gui
from ..gui_action import defaults
from ..gui_action.service import addAction
from ..gui_core.gui_core import publishedURI
from ..superdesk_security.acl import filterAuthenticated
from .acl import filterCollaboratorBlog
from .service import collaboratorSpecification
from __plugin__.livedesk.acl import filterAdminBlog, filterClosedBlog
from acl.right_action import RightAction
from ally.container import ioc, support
from ally.internationalization import NC_
from ally.support.util import ref
from gui.action.api.action import Action
from livedesk.api.blog import IBlogService, IBlogSourceService
from livedesk.api.blog_collaborator import IBlogCollaboratorService
from livedesk.api.blog_post import IBlogPostService
from livedesk.api.blog_theme import IBlogThemeService
from livedesk.api.blog_type import IBlogTypeService
from livedesk.api.blog_type_post import IBlogTypePostService
from livedesk.impl.blog_collaborator import CollaboratorSpecification
from superdesk.person.api.person import IPersonService
from superdesk.person_icon.api.person_icon import IPersonIconService
from superdesk.source.api.source import ISourceService
from livedesk.api.blog_sync import IBlogSyncService
from superdesk.collaborator.api.collaborator import ICollaboratorService
from livedesk.api.comment import IBlogCommentService
from __plugin__.captcha.acl import captcha
from superdesk.verification.api.verification import IPostVerificationService
from superdesk.language.api.language import ILanguageService
from security.rbac.api.rbac import IRoleService
from superdesk.post.api.post import IPostService
from superdesk.post.api.type import IPostTypeService
from superdesk.source.api.type import ISourceTypeService
from superdesk.verification.api.status import IVerificationStatusService
from superdesk.user.api.user_type import IUserTypeService
from livedesk.api.blog_media import IBlogMediaTypeService
from security.api.right import IRightService
from security.api.right_type import IRightTypeService
from livedesk.api.version import IVersionService
from superdesk.media_archive.api.meta_data import IMetaDataService
from superdesk.user.api.user import IUserService
from superdesk.security.api.user_rbac import IUserRbacService
from general_setting.api.general_setting import IGeneralSettingService

# --------------------------------------------------------------------

support.listenToEntities(Action, listeners=addAction)
support.loadAllEntities(Action)

# --------------------------------------------------------------------

@ioc.entity
def menuAction() -> Action:
    return Action('livedesk', Parent=defaults.menuAction(), Label=NC_('menu', 'Live Blogs'))

@ioc.entity
def subMenuAction() -> Action:
    return Action('submenu', Parent=menuAction(), Script=publishedURI('livedesk/scripts/js/submenu-live-blogs.js'))

@ioc.entity
def modulesAction() -> Action:
    return Action('livedesk', Parent=defaults.modulesAction())

@ioc.entity
def dashboardAction() -> Action:
    return Action('livedesk', Parent=defaults.modulesDashboardAction(), Script=publishedURI('livedesk/scripts/js/dashboard.js'))

@ioc.entity
def modulesAddAction() -> Action:
    return Action('add', Parent=modulesAction(), Script=publishedURI('livedesk/scripts/js/add-live-blogs.js'))

@ioc.entity
def modulesEditAction() -> Action:  # TODO: change to view
    return Action('edit', Parent=modulesAction(), Script=publishedURI('livedesk/scripts/js/edit-live-blogs.js'))

@ioc.entity
def modulesBlogEditAction() -> Action:  # TODO: change to view
    return Action('blog-edit', Parent=modulesAction(), Script=publishedURI('livedesk/scripts/js/edit-live-blogs.js'))

@ioc.entity
def modulesBlogPublishAction() -> Action:
    return Action('blog-publish', Parent=modulesAction(), Script=publishedURI('livedesk/scripts/js/blog-publish.js'))

@ioc.entity
def modulesBlogPostPublishAction() -> Action:
    return Action('blog-post-publish', Parent=modulesAction(), Script=publishedURI('livedesk/scripts/js/blog-post-publish.js'))

@ioc.entity
def modulesConfigureAction() -> Action:
    return Action('configure', Parent=modulesAction(), Script=publishedURI('livedesk/scripts/js/configure-blog.js'))

@ioc.entity
def modulesManageCollaboratorsAction() -> Action:
    return Action('manage-collaborators', Parent=modulesAction(),
                  Script=publishedURI('livedesk/scripts/js/manage-collaborators.js'))
@ioc.entity
def modulesManageFeedsAction() -> Action:
    return Action('manage-feeds', Parent=modulesAction(),
                  Script=publishedURI('livedesk/scripts/js/manage-feeds.js'))
@ioc.entity
def modulesArchiveAction() -> Action:
    return Action('archive', Parent=modulesAction(), Script=publishedURI('livedesk/scripts/js/archive.js'))

# --------------------------------------------------------------------

@ioc.entity
def rightLivedeskView() -> RightAction:
    return gui.actionRight(NC_('security', 'Livedesk view'), NC_('security', '''
    Allows read only access to users for livedesk.'''))

@ioc.entity
def rightManageOwnPost() -> RightAction:
    return gui.actionRight(NC_('security', 'Manage own post'), NC_('security', '''
    Allows the creation and management of own posts in livedesk.'''))

@ioc.entity
def rightBlogEdit() -> RightAction:
    return gui.actionRight(NC_('security', 'Blog edit'), NC_('security', '''
    Allows for editing the blog.'''))

@ioc.entity
def rightLivedeskUpdate() -> RightAction:
    return gui.actionRight(NC_('security', 'Livedesk edit'), NC_('security', '''
    Allows edit access to users for livedesk.'''))

# --------------------------------------------------------------------

@gui.setup
def registerAclLivedeskView():
    r = rightLivedeskView()
    r.addActions(menuAction(), subMenuAction(), modulesAction(), modulesArchiveAction(), dashboardAction())
    r.allGet(IBlogTypeService, IBlogTypePostService, IPersonService, IPersonIconService)
    r.allGet(IBlogService, IBlogCollaboratorService, IBlogPostService, filter=filterCollaboratorBlog())
    r.allGet(ISourceService)
    r.add(ref(IBlogService).getAll, filter=filterAuthenticated())
    r.allGet(IBlogPostService, filter=filterClosedBlog())
    r.allGet(IPostVerificationService)
    r.allGet(ILanguageService)
    r.allGet(IRoleService)
    r.allGet(IPostService)
    r.allGet(IPostTypeService)
    r.allGet(ISourceTypeService)
    r.allGet(IVerificationStatusService)
    r.allGet(IUserTypeService)
    r.allGet(IBlogMediaTypeService)
    r.allGet(IRightService)
    r.allGet(IRightTypeService)
    r.allGet(IVersionService)
    r.allGet(IMetaDataService)
    r.allGet(IUserService)
    r.allGet(IUserRbacService)
    r.allGet(IGeneralSettingService)
    r.allGet(IBlogSourceService)
    r.allGet(IBlogCommentService)

@gui.setup
def registerAclManageOwnPost():
    r = rightManageOwnPost()
    r.addActions(menuAction(), subMenuAction(), modulesAction(), modulesEditAction(), dashboardAction())
    r.allGet(IBlogService, filter=filterCollaboratorBlog())
    r.allGet(ISourceService)
    r.add(ref(IBlogPostService).delete, filter=filterClosedBlog())
    # TODO: add: filter=filterOwnPost(), also the override crates problems, this should have been on IPostService
    r.add(ref(IBlogPostService).insert, ref(IBlogPostService).update, filter=filterCollaboratorBlog())
    r.add(ref(IBlogPostService).publish, ref(IBlogPostService).insertAndPublish, ref(IBlogPostService).unpublish,
          ref(IBlogPostService).reorder, ref(IBlogCollaboratorService).addCollaborator,
          ref(IBlogCollaboratorService).addCollaboratorAsDefault, filter=filterAdminBlog())
    r.add(ref(IBlogPostService).insert, ref(IBlogPostService).update, ref(IBlogPostService).publish,
          ref(IBlogPostService).insertAndPublish, ref(IBlogPostService).unpublish, ref(IBlogPostService).reorder,
          filter=filterClosedBlog())
    r.add(ref(IBlogPostService).update)  # TODO: add: filter=filterOwnPost()

@gui.setup
def registerAclLivedeskUpdate():
    r = rightLivedeskUpdate()
    r.allGet(IBlogSyncService)
    r.add(ref(IBlogSyncService).insert, ref(IBlogSyncService).update, filter=filterAuthenticated())
    r.add(ref(IBlogSyncService).delete)
    r.addActions(menuAction(), subMenuAction(), modulesAction(), modulesEditAction(), modulesBlogEditAction(),
                 dashboardAction(), modulesAddAction(), modulesConfigureAction(), modulesManageCollaboratorsAction(), modulesManageFeedsAction(),
                 modulesBlogPublishAction(), modulesBlogPostPublishAction())
    r.all(IBlogService, IBlogPostService, IBlogCollaboratorService, IBlogThemeService, IBlogTypePostService, IBlogTypeService,
          IPersonService, IPersonIconService, ISourceService, ICollaboratorService)
    r.add(ref(IBlogPostService).insert, ref(IBlogPostService).update, ref(IBlogPostService).publish,
          ref(IBlogPostService).insertAndPublish, ref(IBlogPostService).unpublish, ref(IBlogPostService).reorder,
          ref(IBlogPostService).delete, filter=filterClosedBlog())
    r.add(ref(IBlogPostService).update)
    r.add(ref(IPostVerificationService).update)

# --------------------------------------------------------------------

@ioc.before(collaboratorSpecification)
def updateCollaboratorSpecification():
    spec = collaboratorSpecification()
    assert isinstance(spec, CollaboratorSpecification)

    spec.type_filter = []
    spec.type_filter.append(('Administrator', filterAdminBlog()))
    spec.type_filter.append(('Collaborator', filterCollaboratorBlog()))

    spec.type_actions = {}
    spec.type_actions['Collaborator'] = [menuAction(), subMenuAction(), modulesAction(),
                                         modulesArchiveAction(), dashboardAction(), modulesEditAction()]
    spec.type_actions['Administrator'] = [menuAction(), subMenuAction(), modulesAction(),
                                modulesBlogEditAction(), modulesEditAction(), dashboardAction(), modulesAddAction(), modulesConfigureAction(),
                                modulesManageCollaboratorsAction(), modulesManageFeedsAction(), modulesBlogPublishAction(), modulesBlogPostPublishAction()]

# --------------------------------------------------------------------

@ioc.before(captcha)
def updateCaptchaForComments():
    captcha().add(ref(IBlogCommentService).addComment)

