'''
Created on May 2, 2012

@package: superdesk posts
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

API specifications for posts.
'''

from ally.api.config import service, call, query
from ally.api.criteria import AsDateTimeOrdered, AsBoolean
from ally.api.type import Iter, Count
from ally.support.api.entity import Entity, IEntityGetCRUDService
from ally.support.api.keyed import QEntity
from datetime import datetime
from superdesk.api.domain_superdesk import modelSuperDesk
from superdesk.collaborator.api.collaborator import Collaborator
from superdesk.post.api.type import PostType
from superdesk.user.api.user import User

# --------------------------------------------------------------------

@modelSuperDesk
class Post(Entity):
    '''
    Provides the post message model.
    '''
    Type = PostType
    Creator = User
    Author = Collaborator
    IsModified = bool
    Content = str
    CreatedOn = datetime
    PublishedOn = datetime
    UpdatedOn = datetime
    DeletedOn = datetime

# --------------------------------------------------------------------

@query
class QPostUnpublished(QEntity):
    '''
    Provides the post message query.
    '''
    createdOn = AsDateTimeOrdered
    isModified = AsBoolean
    updatedOn = AsDateTimeOrdered

@query
class QPostPublished(QPostUnpublished):
    '''
    Provides the post message query.
    '''
    publishedOn = AsDateTimeOrdered

@query
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

    def getUnpublishedCount(self, creatorId:User.Id=None, authorId:Collaborator.Id=None,
                            q:QPostUnpublished=None) -> Count:
        '''
        Provides the count of unpublished posts.
        '''

    @call(countMethod=getUnpublishedCount, webName='Unpublished')
    def getUnpublished(self, creatorId:User.Id=None, authorId:Collaborator.Id=None, offset:int=None, limit:int=10,
                    q:QPostUnpublished=None) -> Iter(Post):
        '''
        Provides all the unpublished posts.
        '''

    def getPublishedCount(self, creatorId:User.Id=None, authorId:Collaborator.Id=None, q:QPostPublished=None) -> Count:
        '''
        Provides the count of the published posts.
        '''

    @call(countMethod=getPublishedCount, webName='Published')
    def getPublished(self, creatorId:User.Id=None, authorId:Collaborator.Id=None, offset:int=None, limit:int=10,
                    q:QPostPublished=None) -> Iter(Post):
        '''
        Provides all the published posts.
        '''

    def getAllCount(self, creatorId:User.Id=None, authorId:Collaborator.Id=None, q:QPost=None) -> Count:
        '''
        Provides the count of all posts.
        '''

    @call(countMethod=getAllCount)
    def getAll(self, creatorId:User.Id=None, authorId:Collaborator.Id=None, offset:int=None, limit:int=10,
                    q:QPost=None) -> Iter(Post):
        '''
        Provides all the posts.
        '''

