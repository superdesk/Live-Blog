'''
Created on August 28, 2013

@package: livedesk
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Martin Saturka

API specifications for livedesk blog post users.
'''

from ally.api.config import service, call, LIMIT_DEFAULT, UPDATE, DELETE
from livedesk.api.blog import Blog
from livedesk.api.domain_livedesk import modelLiveDesk
from superdesk.user.api.user import User
from superdesk.post.api.post import Post
from ally.api.type import Iter

# --------------------------------------------------------------------

# No model

# --------------------------------------------------------------------

# No query

# --------------------------------------------------------------------

@service
class IBlogPostUserService:
    '''
    BlogPostUser service interface
    '''

    @call
    def getUser(self, blogId:Blog.Id, postId:Post.Id) -> User:
        '''
        Provides the asigned blog post user.
        '''

    @call(webName='List')
    def getAllUsers(self, blogId:Blog.Id, postId:Post.Id, offset:int=None,
               limit:int=LIMIT_DEFAULT, detailed:bool=True) -> Iter(User):
        '''
        Provides all the available blog post users.
        '''

    @call(method=UPDATE)
    def attachUser(self, blogId:Blog.Id, postId:Post.Id, userId:User.Id):
        '''
        Attaches the user to the blog post.
        '''

    @call(method=DELETE)
    def detachUser(self, blogId:Blog.Id, postId:Post.Id, userId:User.Id) -> bool:
        '''
        Detaches the user from the blog post.
        '''

    @call(method=DELETE, webName='User')
    def detachAllUsers(self, blogId:Blog.Id, postId:Post.Id) -> bool:
        '''
        Detaches all users from the blog post.
        '''
