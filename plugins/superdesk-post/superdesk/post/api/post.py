'''
Created on May 2, 2012

@package: superdesk posts
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

API specifications for posts.
'''

from ally.api.config import service, call, query
from ally.api.criteria import AsDateTimeOrdered, AsBoolean, AsLikeOrdered, \
    AsRangeOrdered
from ally.api.type import Iter
from datetime import datetime
from superdesk.api.domain_superdesk import modelData
from superdesk.collaborator.api.collaborator import Collaborator
from superdesk.post.api.type import PostType
from superdesk.user.api.user import User
from superdesk.source.api.source import Source
from superdesk.source.api.type import SourceType
from ally.support.api.entity_ided import Entity, QEntity, IEntityGetCRUDService
from ally.api.option import SliceAndTotal # @UnusedImport

# --------------------------------------------------------------------

@modelData
class Post(Entity):
    '''Provides the post message model.'''
    Type = PostType
    Creator = User
    Author = Collaborator
    IsModified = bool
    IsPublished = bool
    Meta = str
    ContentPlain = str
    Content = str
    CreatedOn = datetime
    PublishedOn = datetime
    UpdatedOn = datetime
    DeletedOn = datetime
    AuthorName = str

# --------------------------------------------------------------------

@query(Post)
class QWithCId:
    '''Provides the query for cId.
    TODO: This was added for a possibility to check for just new SMS posts.
          It partially emulates the cId parameter behavior of BlogPosts.
          It should be done more properly at some future.
    '''
    cId = AsRangeOrdered

@query(Post)
class QPostUnpublished(QEntity, QWithCId):
    '''Provides the post message query.'''
    createdOn = AsDateTimeOrdered
    isModified = AsBoolean
    updatedOn = AsDateTimeOrdered
    deletedOn = AsDateTimeOrdered
    content = AsLikeOrdered

@query(Post)
class QPostPublished(QPostUnpublished):
    '''Provides the post message query.'''
    publishedOn = AsDateTimeOrdered

@query(Post)
class QPost(QPostPublished):
    '''Provides the post message query.'''
    deletedOn = AsDateTimeOrdered

# --------------------------------------------------------------------

@query(Post)
class QPostWithPublished(QPost):
    '''Provides the post message query with isPublished option.'''
    isPublished = AsBoolean

# --------------------------------------------------------------------

@service((Entity, Post))
class IPostService(IEntityGetCRUDService):
    '''Provides the service methods for the post.'''

    @call(webName='Unpublished')
    def getUnpublished(self, creatorId:User.Id=None, authorId:Collaborator.Id=None,
                       q:QPostUnpublished=None, **options:SliceAndTotal) -> Iter(Post.Id):
        '''Provides all the unpublished posts.'''

    @call(webName='Published')
    def getPublished(self, creatorId:User.Id=None, authorId:Collaborator.Id=None,
                     q:QPostPublished=None, **options:SliceAndTotal) -> Iter(Post.Id):
        '''Provides all the published posts.'''

    @call
    def getAll(self, creatorId:User.Id=None, authorId:Collaborator.Id=None,
               q:QPost=None, **options:SliceAndTotal) -> Iter(Post.Id):
        '''Provides all the posts.'''

    @call(webName='Unpublished')
    def getUnpublishedBySource(self, sourceId:Source.Id, q:QPostUnpublished=None,
                               **options:SliceAndTotal) -> Iter(Post.Id):
        '''Provides unpublished posts of a source.'''

    @call(webName='Unpublished')
    def getUnpublishedBySourceType(self, sourceTypeKey:SourceType.Key,
                                   q:QPostUnpublished=None, **options:SliceAndTotal) -> Iter(Post.Id):
        '''Provides unpublished posts of a source type.'''

    @call(webName='Published')
    def getPublishedBySource(self, sourceId:Source.Id, q:QPostPublished=None,
                             **options:SliceAndTotal) -> Iter(Post.Id):
        '''Provides all posts of a source.'''

    @call(webName='Published')
    def getPublishedBySourceType(self, sourceTypeKey:SourceType.Key, q:QPostPublished=None,
                                 **options:SliceAndTotal) -> Iter(Post.Id):
        '''Provides published posts of a source type.'''

    @call
    def getAllBySource(self, sourceId:Source.Id, q:QPost=None, **options:SliceAndTotal) -> Iter(Post.Id):
        '''Provides published posts of a source.'''

    @call
    def getAllBySourceType(self, sourceTypeKey:SourceType.Key, q:QPost=None,
                           **options:SliceAndTotal) -> Iter(Post.Id):
        '''Provides all posts of a source type.'''

    @call
    def update(self, post:Post):
        '''Updates the post.'''
