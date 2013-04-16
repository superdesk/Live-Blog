'''
Created on Aug 25, 2011

@package: ally core sql alchemy
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

API specifications for article.
'''

from .article_type import ArticleType
from .entity import Entity, IEntityService
from ally.api.config import model, service, call
from ally.api.type import Iter

# --------------------------------------------------------------------

@model()
class Article(Entity):
    '''
    Provides the article model.
    '''
    Name = str
    Type = ArticleType

# --------------------------------------------------------------------

@service((Entity, Article))
class IArticleService(IEntityService):
    '''
    Provides services for articles.
    '''

    @call
    def getByArticleType(self, id:ArticleType.Id, offset:int=None, limit:int=None) -> Iter(Article):
        '''
        Provides all the articles that belong to the article type.
        
        @param id: integer
            The article type id to retrieve the articles from.
        @param offset: integer
            The offset to retrieve the articles from.
        @param limit: integer
            The limit of sections to retrieve.
        '''
