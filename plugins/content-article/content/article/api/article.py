'''
Created on Mar 14, 2013

@package: content article
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Rus Mugurel

API specifications for article.
'''

from content.packager.api.domain_content import modelContent
from ally.support.api.entity import Entity, QEntity, IEntityService
from ally.api.config import query, service, call, UPDATE, GET
from ally.api.criteria import AsLike, AsDateOrdered
from content.packager.api.item import Item
from ally.api.type import Reference, Iter
from datetime import datetime

# --------------------------------------------------------------------

@modelContent
class Article(Entity):
    '''
    Provides the article model.
    '''
    Item = Item
    Creator = str
    Author = str
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

    @call(method=GET, webName='Search')
    def search(self, text:str) -> Iter(Article):
        '''
        Perform a search on articles for the given text

        @param text: str
            The text to search for
        @return: list of article entities
        '''
