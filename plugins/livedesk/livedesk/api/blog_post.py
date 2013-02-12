'''
Created on May 4, 2012

@package: livedesk
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

API specifications for livedesk blog posts.
'''

from .blog import Blog
from ally.api.config import service, call, INSERT, query, UPDATE, extension
from ally.api.criteria import AsRangeOrdered, AsBoolean
from ally.api.extension import IterPart
from ally.api.type import Iter, Reference
from livedesk.api.domain_livedesk import modelLiveDesk
from superdesk.collaborator.api.collaborator import Collaborator
from superdesk.person.api.person import Person
from superdesk.post.api.post import Post, QPostUnpublished, QPost, IPostService
from superdesk.post.api.type import PostType
from superdesk.user.api.user import User
from livedesk.api.blog_collaborator_group import BlogCollaboratorGroup

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
    AuthorImage = Reference

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

@extension
class IterPost(IterPart):
    '''
    The post iterable that provides extended information on the posts collection. The offset more is constructed without
	the cId filtering, the idea is if you provide in your query a filter saying that you require elements that have an
	order greater then a certain value and also provide a cId in your filtering, you will have a return that is presenting
	you the changed entries based on the cId, but the offsetMore will present you how many posts there are that are greater
	then the provided order with no regards to cId. This is helpful when requesting the next page because the offset more
	will tell you exactly fron where you next page will start. As a conclusion to have a relevant offsetMore you need to
	query based on order and cId.
    '''
    offsetMore = int
    lastCId = int

# --------------------------------------------------------------------

@service
class IBlogPostService:
    '''
    Provides the service methods for the blog posts.
    '''

    @call
    def getById(self, blogId:Blog, postId:BlogPost, thumbSize:str=None) -> BlogPost:
        '''
        Provides the blog post based on the id.
        '''

    @call(webName='Published')
    def getPublished(self, blogId:Blog, typeId:PostType=None, creatorId:User=None, authorId:Collaborator=None, thumbSize:str=None,
                     offset:int=None, limit:int=None, detailed:bool=True, q:QBlogPostPublished=None) -> Iter(BlogPost):
        '''
        Provides all the blogs published posts. The detailed iterator will return a @see: IterPost.
        '''

    @call(webName='Unpublished')
    def getUnpublished(self, blogId:Blog, typeId:PostType=None, creatorId:User=None, authorId:Collaborator=None, thumbSize:str=None,
                       offset:int=None, limit:int=None, q:QBlogPostUnpublished=None) -> Iter(BlogPost):
        '''
        Provides all the unpublished blogs posts.
        '''
    
    @call(webName='GroupUnpublished')
    def getGroupUnpublished(self, blogId:Blog, groupId:BlogCollaboratorGroup, typeId:PostType=None, authorId:Collaborator=None, thumbSize:str=None,
                       offset:int=None, limit:int=None, q:QBlogPostUnpublished=None) -> Iter(BlogPost):
        '''
        Provides all the unpublished blogs posts for current blog colllaborator group.
        '''

    @call(webName='Owned')
    def getOwned(self, blogId:Blog, creatorId:User, typeId:PostType=None, offset:int=None, limit:int=None,
                 q:QBlogPost=None) -> Iter(BlogPost):
        '''
        Provides all the unpublished blogs posts that belong to the creator, this means that the posts will not have
        an Author.
        '''

    @call
    def getAll(self, blogId:Blog, typeId:PostType=None, creatorId:User=None, authorId:Collaborator=None, thumbSize:str=None,
                       offset:int=None, limit:int=None, q:QBlogPost=None) -> Iter(BlogPost):
        '''
        Provides all the unpublished blogs posts.
        '''

    @call
    def insert(self, blogId:Blog.Id, post:Post) -> BlogPost.Id:
        '''
        Inserts the post in the blog.
        '''

    @call(method=INSERT, webName='Publish')
    def publish(self, blogId:Blog.Id, postId:BlogPost.Id) -> BlogPost.Id:
        '''
        Publishes the post in the blog.
        '''

    @call(webName='Published')
    def insertAndPublish(self, blogId:Blog.Id, post:Post) -> BlogPost.Id:
        '''
        Inserts and publishes the post in the blog.
        '''

    @call(method=INSERT, webName='Unpublish')
    def unpublish(self, blogId:Blog.Id, postId:BlogPost.Id) -> BlogPost.Id:
        '''
        Unpublishes the post in the blog.
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
