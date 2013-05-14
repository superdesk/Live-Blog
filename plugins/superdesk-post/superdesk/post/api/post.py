'''
Created on May 2, 2012

@package: superdesk posts
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

API specifications for posts.
'''

from ally.api.config import service, call, query, LIMIT_DEFAULT
from ally.api.criteria import AsDateTimeOrdered, AsBoolean
from ally.api.type import Iter
from ally.support.api.entity import Entity, QEntity, IEntityGetCRUDService
from datetime import datetime
from superdesk.api.domain_superdesk import modelData
from superdesk.collaborator.api.collaborator import Collaborator
from superdesk.post.api.type import PostType
from superdesk.user.api.user import User
from superdesk.source.api.source import Source
from superdesk.source.api.type import SourceType

# --------------------------------------------------------------------

@modelData
class Post(Entity):
    '''
    Provides the post message model.
    '''
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
class QPostUnpublished(QEntity):
    '''
    Provides the post message query.
    '''
    createdOn = AsDateTimeOrdered
    isModified = AsBoolean
    updatedOn = AsDateTimeOrdered
    deletedOn = AsDateTimeOrdered

@query(Post)
class QPostPublished(QPostUnpublished):
    '''
    Provides the post message query.
    '''
    publishedOn = AsDateTimeOrdered

@query(Post)
class QPost(QPostPublished):
    '''
    Provides the post message query.
    '''
    deletedOn = AsDateTimeOrdered

# --------------------------------------------------------------------

@service((Entity, Post))
class IPostService(IEntityGetCRUDService):
    '''
    Provides the service methods for the post.
    '''

    @call(webName='Unpublished')
    def getUnpublished(self, creatorId:User.Id=None, authorId:Collaborator.Id=None, offset:int=None,
                       limit:int=LIMIT_DEFAULT, detailed:bool=True, q:QPostUnpublished=None) -> Iter(Post):
        '''
        Provides all the unpublished posts.
        '''

    @call(webName='Published')
    def getPublished(self, creatorId:User.Id=None, authorId:Collaborator.Id=None, offset:int=None,
                     limit:int=LIMIT_DEFAULT, detailed:bool=True, q:QPostPublished=None) -> Iter(Post):
        '''
        Provides all the published posts.
        '''

    @call
    def getAll(self, creatorId:User.Id=None, authorId:Collaborator.Id=None, offset:int=None, limit:int=LIMIT_DEFAULT,
               detailed:bool=True, q:QPost=None) -> Iter(Post):
        '''
        Provides all the posts.
        '''

    @call(webName='Unpublished')
    def getUnpublishedBySource(self, sourceId:Source.Id, offset:int=None, limit:int=LIMIT_DEFAULT,
               detailed:bool=True, q:QPostUnpublished=None) -> Iter(Post):
        '''
        Provides unpublished posts of a source.
        '''

    @call(webName='Unpublished')
    def getUnpublishedBySourceType(self, sourceTypeKey:SourceType.Key, offset:int=None, limit:int=LIMIT_DEFAULT,
               detailed:bool=True, q:QPostUnpublished=None) -> Iter(Post):
        '''
        Provides unpublished posts of a source type.
        '''

    @call(webName='Published')
    def getPublishedBySource(self, sourceId:Source.Id, offset:int=None, limit:int=LIMIT_DEFAULT,
               detailed:bool=True, q:QPostPublished=None) -> Iter(Post):
        '''
        Provides all posts of a source.
        '''

    @call(webName='Published')
    def getPublishedBySourceType(self, sourceTypeKey:SourceType.Key, offset:int=None, limit:int=LIMIT_DEFAULT,
               detailed:bool=True, q:QPostPublished=None) -> Iter(Post):
        '''
        Provides published posts of a source type.
        '''

    @call
    def getAllBySource(self, sourceId:Source.Id, offset:int=None, limit:int=LIMIT_DEFAULT,
               detailed:bool=True, q:QPost=None) -> Iter(Post):
        '''
        Provides published posts of a source.
        '''

    @call
    def getAllBySourceType(self, sourceTypeKey:SourceType.Key, offset:int=None, limit:int=LIMIT_DEFAULT,
               detailed:bool=True, q:QPost=None) -> Iter(Post):
        '''
        Provides all posts of a source type.
        '''
