'''
Created on Mar 14, 2013

@package: content article
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Rus Mugurel

API specifications for article.
'''

from ally.api.config import query, service, call, UPDATE, LIMIT_DEFAULT, DELETE, GET
from ally.api.criteria import AsLike, AsDateOrdered
from ally.api.type import Reference, Iter
from ally.support.api.entity import Entity, QEntity, IEntityService
from content.packager.api.domain_content import modelContent
from content.packager.api.item import Item
from datetime import datetime
from superdesk.user.api.user import User
from superdesk.person.api.person import Person
from ..api.target_type import TargetType

# --------------------------------------------------------------------

@modelContent
class Article(Entity):
    '''
    Provides the article model.
    '''
    Item = Item
    Creator = User
    Author = Person
    Content = str
    PublishedOn = datetime
    IsPublished = bool
    Preview = Reference

# --------------------------------------------------------------------

@query(Article)
class QArticle(QEntity):
    '''
    Provides the article query.
    '''
    creator = AsLike
    author = AsLike
    publishedOn = AsDateOrdered
    search = AsLike

# --------------------------------------------------------------------

@service((Entity, Article), (QEntity, QArticle))
class IArticleService(IEntityService):
    '''
    Provides the service methods for Article model.
    '''

    @call(method=UPDATE, webName="Publish")
    def publish(self, id:Article.Id):
        '''
        Publish the article identified by the given id.

        @param id: int
            The article identifier
        '''

    @call(method=UPDATE, webName="Unpublish")
    def unpublish(self, id:Article.Id):
        '''
        Unpublish the article identified by the given id.

        @param id: int
            The article identifier
        '''

# --------------------------------------------------------------------

@service
class IArticleTargetTypeService:
    '''
    Provides the TargetType-related service methods for Article model.
    '''

    @call(method=GET)
    def getTargetTypes(self, id:Article.Id, offset:int=None, limit:int=LIMIT_DEFAULT, detailed:bool=True) -> Iter(TargetType):
        '''
        Provides all target types of an article.
        '''

    @call(method=GET, webName="Unassigned")
    def getUnassignedTargetTypes(self, id:Article.Id, offset:int=None, limit:int=LIMIT_DEFAULT, detailed:bool=True) -> Iter(TargetType):
        '''
        Returns a list of target types that are not assigned to the given article.
        '''

    @call(method=UPDATE)
    def attachTargetType(self, id:Article.Id, targetKey:TargetType.Key):
        '''
        Sets a target type for an article.
        '''

    @call(method=DELETE)
    def detachTargetType(self, id:Article.Id, targetKey:TargetType.Key) -> bool:
        '''
        Unsets a target type from an article.
        '''

