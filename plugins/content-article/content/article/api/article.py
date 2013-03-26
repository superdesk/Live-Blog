'''
Created on Mar 14, 2013

@package: content article
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Rus Mugurel

API specifications for article.
'''

from ally.api.config import criteria, query, service, call, UPDATE, GET
from ally.api.criteria import AsLike, AsDateOrdered, AsOrdered
from ally.api.type import Reference, Iter
from ally.support.api.entity import Entity, QEntity, IEntityService
from content.packager.api.domain_content import modelContent
from content.packager.api.item import Item
from datetime import datetime
from superdesk.user.api.user import User
from superdesk.person.api.person import Person

# --------------------------------------------------------------------

@criteria
class AsLikeAll:
    '''
    Provides criteria that can apply like operator to multiple text columns
    '''
    all = str

# --------------------------------------------------------------------

@criteria
class AsLikeAllOrdered(AsLikeAll, AsOrdered):
    '''
    Provides the like search and also the ordering and boolean expression functionality (see AsLikeAll).
    '''

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
    search = AsLikeAllOrdered

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
