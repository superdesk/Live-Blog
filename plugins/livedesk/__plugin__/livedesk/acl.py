'''
Created on Jan 15, 2013

@package: livedesk
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the acl setup.
'''

from acl.spec import Filter
from ally.container import ioc, support
from livedesk.api.blog import Blog
from livedesk.api.filter_blog import IBlogAdminFilterService, \
    IBlogCollaboratorFilterService, IBlogStatusFilterService
from superdesk.security.api.filter_authenticated import Authenticated

# --------------------------------------------------------------------

@ioc.entity
def filterAdminBlog():
    '''
    Provides filtering for the admin users blogs.
    '''
    return Filter(1, Authenticated.Id, Blog.Id, support.entityFor(IBlogAdminFilterService))

@ioc.entity
def filterCollaboratorBlog():
    '''
    Provides filtering for the collaborator users blogs.
    '''
    return Filter(2, Authenticated.Id, Blog.Id, support.entityFor(IBlogCollaboratorFilterService))

@ioc.entity
def filterClosedBlog():
    '''
    Provides filtering for the blog posts based on blog status: open/close.
    '''
    return Filter(3, Authenticated.Id, Blog.Id, support.entityFor(IBlogStatusFilterService))
