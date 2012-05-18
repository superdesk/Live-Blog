'''
Created on May 4, 2012

@package: livedesk
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

API specifications for livedesk blog posts.
'''

from .blog import Blog
from ally.api.config import service, call, INSERT
from livedesk.api.domain_livedesk import modelLiveDesk
from superdesk.post.api.post import Post, QPostPublished, QPostUnpublished
from superdesk.user.api.user import User
from superdesk.collaborator.api.collaborator import Collaborator
from ally.api.type import Iter

# --------------------------------------------------------------------

@modelLiveDesk(name='Post')
class BlogPost(Post):
    '''
    Provides the blog post model.
    '''
    Blog = Blog
    AuthorName = str

# --------------------------------------------------------------------

# No query

# --------------------------------------------------------------------

@service
class IBlogPostService:
    '''
    Provides the service methods for the blog posts.
    '''

    @call
    def getById(self, blogId:Blog, postId:BlogPost) -> BlogPost:
        '''
        Provides the blog post based on the id.
        '''

    @call(webName='Published')
    def getPublished(self, blogId:Blog, creatorId:User=None, authorId:Collaborator=None,
                     offset:int=None, limit:int=None, q:QPostPublished=None) -> Iter(BlogPost):
        '''
        Provides all the blogs published posts.
        '''

    @call(webName='Unpublished')
    def getUnpublished(self, blogId:Blog, creatorId:User=None, authorId:Collaborator=None,
                       offset:int=None, limit:int=None, q:QPostUnpublished=None) -> Iter(BlogPost):
        '''
        Provides all the unpublished blogs posts.
        '''

    @call
    def insert(self, blogId:Blog.Id, post:Post) -> BlogPost.Id:
        '''
        Inserts the post for the blog.
        '''

    @call(method=INSERT, webName='Publish')
    def publish(self, blogId:Blog.Id, postId:BlogPost.Id) -> BlogPost.Id:
        '''
        Inserts the post for the blog.
        '''

    @call(webName='Published')
    def insertAndPublish(self, blogId:Blog.Id, post:Post) -> BlogPost.Id:
        '''
        Inserts the post for the blog.
        '''

    @call
    def update(self, blogId:Blog.Id, post:Post):
        '''
        Update the post for the blog.
        '''

