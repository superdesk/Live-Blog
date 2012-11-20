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
from livedesk.api.domain_livedesk import modelLiveDesk
from superdesk.user.api.user import User

# --------------------------------------------------------------------

@modelLiveDesk
class Admin(User):
    '''
    Provides the blog administrator model.
    '''
    Blog = Blog

# --------------------------------------------------------------------

# No query

# --------------------------------------------------------------------

@service
class IBlogAdminService:
    '''
    Provides the service methods for the blog administrators.
    '''

    @call
    def getById(self, blogId:Blog, adminId:Admin) -> Admin:
        '''
        Provides the blog admin based on the id.
        '''

    @call
    def getAll(self, blogId:Blog) -> Iter(Admin):
        '''
        Provides all the blog administrators.
        '''

    @call(method=INSERT, webName='Add')
    def addAdmin(self, blogId:Blog.Id, userId:User.Id) -> Admin.Id:
        '''
        Assigns the user as a user administrator to the blog.
        '''

    @call(method=DELETE, webName='Remove')
    def removeAdmin(self, blogId:Blog, userId:User) -> bool:
        '''
        Removes the user administrator from the blog.
        '''
