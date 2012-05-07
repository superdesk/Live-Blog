'''
Created on May 4, 2012

@package: livedesk
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

API specifications for livedesk blog posts.
'''

from .blog import Blog
from ally.api.config import service, call
from livedesk.api.domain_livedesk import modelLiveDesk
from superdesk.post.api.post import Post, QPostPublished, QPostUnpublished
from ally.support.api.entity import IEntityGetCRUDService, Entity
from superdesk.user.api.user import User
from superdesk.collaborator.api.collaborator import Collaborator
from ally.api.type import Iter

# --------------------------------------------------------------------

@modelLiveDesk
class BlogPost(Post):
    '''
    Provides the blog post model.
    '''
    Blog = Blog
    AuthorName = str

# --------------------------------------------------------------------

# No query

# --------------------------------------------------------------------

@service((Entity, BlogPost))
class IBlogPostService(IEntityGetCRUDService):
    '''
    Provides the service methods for the blog posts.
    '''

    @call(webName='Published')
    def getPublished(self, blogId:Blog.Id, creatorId:User.Id=None, authorId:Collaborator.Id=None,
                     offset:int=None, limit:int=None, q:QPostPublished=None) -> Iter(BlogPost):
        '''
        Provides all the blogs published posts.
        '''

    @call(webName='Unpublished')
    def getUnpublished(self, blogId:Blog.Id, creatorId:User.Id=None, authorId:Collaborator.Id=None, offset:int=None,
                       limit:int=None, q:QPostUnpublished=None) -> Iter(BlogPost):
        '''
        Provides all the unpublished blogs posts.
        '''

