'''
Created on May 4, 2012

@package: livedesk
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

API specifications for livedesk blog posts.
'''

from .blog import Blog
from ally.api.config import service, call, INSERT, query, UPDATE
from livedesk.api.domain_livedesk import modelLiveDesk
from superdesk.post.api.post import Post, QPostUnpublished, \
    QPost, IPostService
from superdesk.user.api.user import User
from superdesk.collaborator.api.collaborator import Collaborator
from ally.api.type import Iter
from ally.api.criteria import AsRangeOrdered, AsBoolean
from ally.api.authentication import auth
from superdesk.person.api.person import Person
from superdesk.post.api.type import PostType

# --------------------------------------------------------------------

@modelLiveDesk(name=Post)
class BlogPost(Post):
    '''
    Provides the blog post model.
    '''
    CId = int
    Order = float
    Blog = Blog
    AuthorPerson = Person
    AuthorName = str

# --------------------------------------------------------------------

@query(BlogPost)
class QWithCId:
    '''
    Provides the query for cId.
    '''
    cId = AsRangeOrdered

@query(BlogPost)
class QBlogPostUnpublished(QPostUnpublished, QWithCId):
    '''
    Provides the blog post message query.
    '''

@query(BlogPost)
class QBlogPostPublished(QPost, QWithCId):
    '''
    Provides the blog post message query.
    '''
    order = AsRangeOrdered

@query(BlogPost)
class QBlogPost(QPost, QWithCId):
    '''
    Provides the blog post message query.
    '''
    isPublished = AsBoolean

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
    def getPublished(self, blogId:Blog, typeId:PostType=None, creatorId:User=None, authorId:Collaborator=None,
                     offset:int=None, limit:int=None, detailed:bool=True, q:QBlogPostPublished=None) -> Iter(BlogPost):
        '''
        Provides all the blogs published posts.
        '''

    @call(webName='Unpublished')
    def getUnpublished(self, blogId:Blog, typeId:PostType=None, creatorId:User=None, authorId:Collaborator=None,
                       offset:int=None, limit:int=None, q:QBlogPostUnpublished=None) -> Iter(BlogPost):
        '''
        Provides all the unpublished blogs posts.
        '''

    @call(webName='Owned')
    def getOwned(self, blogId:Blog, creatorId:auth(User), typeId:PostType=None, offset:int=None, limit:int=None,
                 q:QBlogPost=None) -> Iter(BlogPost):
        '''
        Provides all the unpublished blogs posts that belong to the creator, this means that the posts will not have
        an Author.
        '''

    @call
    def getAll(self, blogId:Blog, typeId:PostType=None, creatorId:User=None, authorId:Collaborator=None,
                       offset:int=None, limit:int=None, q:QBlogPost=None) -> Iter(BlogPost):
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

    @call(method=UPDATE, webName='Reorder')
    def reorder(self, blogId:Blog.Id, postId:Post.Id, refPostId:Post.Id, before:bool=True):
        '''
        Reorder the post.
        '''

    @call(replaceFor=IPostService)
    def delete(self, id:Post.Id) -> bool:
        '''
        Delete the post for the provided id.
        
        @param id: integer
            The id of the post to be deleted.
            
        @return: True if the delete is successful, false otherwise.
        '''
