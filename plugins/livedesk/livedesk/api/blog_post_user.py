'''
Created on August 28, 2013

@package: livedesk
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Martin Saturka

API specifications for livedesk blog post users.
'''

from ally.api.config import service, call
from ally.support.api.entity import Entity, IEntityService
from livedesk.api.blog import Blog
from livedesk.api.domain_livedesk import modelLiveDesk
from superdesk.user.api.user import User
from superdesk.post.api.post import Post

# --------------------------------------------------------------------

@modelLiveDesk
class BlogPostUser(Entity):
    '''
    Provides the blog post tag model.
    '''
    Blog = Blog
    Post = Post
    User = User

# --------------------------------------------------------------------

# No query

# --------------------------------------------------------------------

@service((Entity, BlogPostUser))
class IBlogPostUserService(IEntityService):
    '''
    BlogPostUser model service interface
    '''

    @call
    def getAll(self, blogId:Blog.Id=None, postId:Post.Id=None, offset:int=None,
               limit:int=LIMIT_DEFAULT, detailed:bool=True) -> Iter(BlogPostUser):
        '''
        Provides all the available blog post users.
        '''
