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
from ..gui_security import acl
from ..superdesk_security.acl import filterAuthenticated
from .acl import filterCollaboratorBlog
from .service import collaboratorSpecification
from __plugin__.livedesk.acl import filterAdminBlog
from ally.container import ioc
from ally.internationalization import NC_
from distribution.container import app
from gui.action.api.action import Action
from livedesk.api.blog import IBlogService
from livedesk.api.blog_collaborator import IBlogCollaboratorService
from livedesk.api.blog_post import IBlogPostService
from livedesk.api.blog_theme import IBlogThemeService
from livedesk.api.blog_type import IBlogTypeService
from livedesk.api.blog_type_post import IBlogTypePostService
from livedesk.impl.blog_collaborator import CollaboratorSpecification
from superdesk.person.api.person import IPersonService
from superdesk.person_icon.api.person_icon import IPersonIconService

# --------------------------------------------------------------------

@ioc.entity
def menuAction():
    return Action('livedesk', Parent=defaults.menuAction(), Label=NC_('menu', 'Live Blogs'))

@ioc.entity
def subMenuAction():
    return Action('submenu', Parent=menuAction(), Script=publishedURI('livedesk/scripts/js/submenu-live-blogs.js'))

@ioc.entity
def modulesAction():
    return Action('livedesk', Parent=defaults.modulesAction())

@ioc.entity
def dashboardAction():
    return Action('livedesk', Parent=defaults.modulesDashboardAction(), Script=publishedURI('livedesk/scripts/js/dashboard.js'))

@ioc.entity
def modulesAddAction():
    return Action('add', Parent=modulesAction(), Script=publishedURI('livedesk/scripts/js/add-live-blogs.js'))

@ioc.entity
def modulesEditAction():  # TODO: change to view
    return Action('edit', Parent=modulesAction(), Script=publishedURI('livedesk/scripts/js/edit-live-blogs.js'))

@ioc.entity
def modulesBlogEditAction():  # TODO: change to view
    return Action('blog-edit', Parent=modulesAction(), Script=publishedURI('livedesk/scripts/js/edit-live-blogs.js'))

@ioc.entity
def modulesBlogPublishAction():
    return Action('blog-publish', Parent=modulesAction(), Script=publishedURI('livedesk/scripts/js/blog-publish.js'))

@ioc.entity
def modulesBlogPostPublishAction():
    return Action('blog-post-publish', Parent=modulesAction(), Script=publishedURI('livedesk/scripts/js/blog-post-publish.js'))

@ioc.entity
def modulesConfigureAction():
    return Action('configure', Parent=modulesAction(), Script=publishedURI('livedesk/scripts/js/configure-blog.js'))

@ioc.entity
def modulesManageCollaboratorsAction():
    return Action('manage-collaborators', Parent=modulesAction(),
                  Script=publishedURI('livedesk/scripts/js/manage-collaborators.js'))

@ioc.entity
def modulesArchiveAction():
    return Action('archive', Parent=modulesAction(), Script=publishedURI('livedesk/scripts/js/archive.js'))

# --------------------------------------------------------------------

@ioc.entity
def rightLivedeskView():
    return acl.actionRight(NC_('security', 'Livedesk view'), NC_('security', '''
    Allows read only access to users for livedesk.'''))

@ioc.entity
def rightManageOwnPost():
    return acl.actionRight(NC_('security', 'Manage own post'), NC_('security', '''
    Allows the creation and management of own posts in livedesk.'''))

@ioc.entity
def rightBlogEdit():
    return acl.actionRight(NC_('security', 'Blog edit'), NC_('security', '''
    Allows for editing the blog.'''))

@ioc.entity
def rightLivedeskUpdate():
    return acl.actionRight(NC_('security', 'Livedesk edit'), NC_('security', '''
    Allows edit access to users for livedesk.'''))

# --------------------------------------------------------------------

@app.deploy
def registerActions():
    addAction(menuAction())
    addAction(subMenuAction())
    addAction(modulesAction())
    addAction(modulesAddAction())
    addAction(modulesEditAction())
    addAction(modulesConfigureAction())
    addAction(modulesArchiveAction())
    addAction(modulesManageCollaboratorsAction())
    addAction(modulesBlogPublishAction())
    addAction(modulesBlogPostPublishAction())
    addAction(dashboardAction())
    addAction(modulesBlogEditAction())

@acl.setup
def registerAclLivedeskView():
    rightLivedeskView().addActions(menuAction(), subMenuAction(), modulesAction(), modulesArchiveAction(), dashboardAction())\
    .allGet(IBlogService, filter=filterCollaboratorBlog())\
    .byName(IBlogService, IBlogService.getAll, filter=filterAuthenticated())\
    .allGet(IBlogPostService, filter=filterCollaboratorBlog())\
    .allGet(IBlogCollaboratorService, filter=filterCollaboratorBlog())\
    .allGet(IBlogTypeService)\
    .allGet(IBlogTypePostService)\
    .allGet(IPersonService).allGet(IPersonIconService)

@acl.setup
def registerAclManageOwnPost():
    rightManageOwnPost().addActions(menuAction(), subMenuAction(), modulesAction(), modulesEditAction(), \
                                modulesBlogEditAction(), dashboardAction(), modulesAddAction(), modulesConfigureAction(), \
                                modulesManageCollaboratorsAction(), modulesBlogPublishAction(), modulesBlogPostPublishAction())\
    .allGet(IBlogService, filter=filterCollaboratorBlog())

    rightManageOwnPost().byName(IBlogPostService, IBlogPostService.delete)
    # TODO: add: filter=filterOwnPost(), also the override crates problems, this should have been on IPostService
    rightManageOwnPost().byName(IBlogPostService, IBlogPostService.insert, IBlogPostService.update,
                                filter=filterCollaboratorBlog())
    rightManageOwnPost().byName(IBlogPostService, IBlogPostService.publish, IBlogPostService.insertAndPublish, IBlogPostService.unpublish, IBlogPostService.reorder,
                                filter=filterAdminBlog())
    rightManageOwnPost().byName(IBlogCollaboratorService, IBlogCollaboratorService.addCollaborator, IBlogCollaboratorService.addCollaboratorAsDefault,
                                filter=filterAdminBlog())
    rightManageOwnPost().byName(IBlogPostService, IBlogPostService.update)  # TODO: add: filter=filterOwnPost()

@acl.setup
def registerAclLivedeskUpdate():
    rightLivedeskUpdate().addActions(menuAction(), subMenuAction(), modulesAction(), modulesEditAction(), \
                                modulesBlogEditAction(), dashboardAction(), modulesAddAction(), modulesConfigureAction(), \
                                modulesManageCollaboratorsAction(), modulesBlogPublishAction(), modulesBlogPostPublishAction())\
    .all(IBlogService).all(IBlogPostService).all(IBlogCollaboratorService)\
    .all(IBlogThemeService).all(IBlogTypePostService).all(IBlogTypeService)\
    .all(IPersonService).all(IPersonIconService)

# --------------------------------------------------------------------

@ioc.before(collaboratorSpecification)
def updateCollaboratorSpecification():
    spec = collaboratorSpecification()
    assert isinstance(spec, CollaboratorSpecification)
    
    spec.type_filter = []
    spec.type_filter.append(('Administrator', filterAdminBlog()))
    spec.type_filter.append(('Collaborator', filterCollaboratorBlog()))
    
    spec.type_actions = {}
    spec.type_actions['Collaborator'] = [action.Path for action in (menuAction(), subMenuAction(), modulesAction(),
                                                          modulesArchiveAction(), dashboardAction(), modulesEditAction())]
    spec.type_actions['Administrator'] = [action.Path for action in (menuAction(), subMenuAction(), modulesAction(),
                                modulesBlogEditAction(), modulesEditAction(), dashboardAction(), modulesAddAction(), modulesConfigureAction(),
                                modulesManageCollaboratorsAction(), modulesBlogPublishAction(), modulesBlogPostPublishAction())]
