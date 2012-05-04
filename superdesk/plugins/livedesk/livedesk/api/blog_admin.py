'''
Created on May 4, 2012

@package: livedesk
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

API specifications for livedesk blog administrators.
'''

from .blog import Blog
from ally.api.config import service, call, INSERT, DELETE
from ally.api.type import Iter
from ally.support.api.entity import Entity, IEntityGetService
from livedesk.api.domain_livedesk import modelLiveDesk
from superdesk.user.api.user import User

# --------------------------------------------------------------------

@modelLiveDesk
class BlogAdmin(Entity):
    '''
    Provides the blog administrator model.
    '''
    Blog = Blog
    User = User

# --------------------------------------------------------------------

# No query

# --------------------------------------------------------------------

@service((Entity, BlogAdmin))
class IBlogAdminService(IEntityGetService):
    '''
    Provides the service methods for the blog administrators.
    '''

    @call
    def getAll(self, blogId:Blog.Id=None, userId:User.Id=None, offset:int=None, limit:int=None) -> Iter(BlogAdmin):
        '''
        Provides all the blog administrators.
        '''

    @call(method=INSERT)
    def addAdmin(self, blogId:Blog.Id, userId:User.Id) -> BlogAdmin.Id:
        '''
        Assigns the user as a user administrator to the blog.
        '''

    @call(method=DELETE)
    def removeAdmin(self, blogId:Blog.Id, userId:User.Id) -> bool:
        '''
        Removes the user administrator from the blog.
        '''

    @call
    def remove(self, blogAdminId:BlogAdmin.Id) -> bool:
        '''
        Removes the blog user administrator.
        '''
