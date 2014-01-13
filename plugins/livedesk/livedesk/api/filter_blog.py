'''
Created on Jan 12, 2013

@package: livedesk
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

The filter used to check if the authenticated user has access to a requested blog.
'''

from acl.api.domain_filter import aliasFilter
from acl.api.filter import IsAllowed, IAclFilter
from ally.api.config import service, call, GET
from livedesk.api.blog import Blog
from superdesk.security.api.filter_authenticated import Authenticated

# --------------------------------------------------------------------

@aliasFilter
class HasBlog(IsAllowed):
    '''
    It is allowed for blog.
    '''
    
# --------------------------------------------------------------------

@service
class IBlogAdminFilterService(IAclFilter):
    '''
    Provides the service that checks if the authenticated user has administrative access to a requested blog.
    '''
    
    @call(method=GET, webName='Administrator')
    def isAllowed(self, userId:Authenticated.Id, blogId:Blog.Id) -> HasBlog.HasAccess:
        '''
        @see: IAclFilter.isAllowed
        '''
        
@service
class IBlogCollaboratorFilterService(IAclFilter):
    '''
    Provides the service that checks if the authenticated user has access to a requested blog as a collaborator.
    '''
    
    @call(method=GET, webName='Collaborator')
    def isAllowed(self, userId:Authenticated.Id, blogId:Blog.Id) -> HasBlog.HasAccess:
        '''
        @see: IAclFilter.isAllowed
        '''

@service
class IBlogStatusFilterService(IAclFilter):
    '''
    Provides the service that checks if the blog is open/close and post operations are permitted.
    '''

    @call(method=GET, webName='Status')
    def isAllowed(self, userId:Authenticated.Id, blogId:Blog.Id) -> HasBlog.HasAccess:
        '''
        @see: IAclFilter.isAllowed
        '''
