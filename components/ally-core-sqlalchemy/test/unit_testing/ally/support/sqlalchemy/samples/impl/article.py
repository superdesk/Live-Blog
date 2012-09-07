'''
Created on Aug 25, 2011

@package: ally core sql alchemy
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

SQL alchemy implementation for article API.
'''

from ..api.article import IArticleService
from ..meta.article import Article
from .entity import EntityServiceAlchemy

# --------------------------------------------------------------------

class ArticleServiceAlchemy(EntityServiceAlchemy, IArticleService):
    '''
    Implementation for @see: IArticleService
    '''

    def __init__(self): EntityServiceAlchemy.__init__(self, Article)

    def getByArticleType(self, id, offset=None, limit=None):
        '''
        @see: IArticleService.getByArticleType
        '''
        return self._getAll(Article.Type == id, offset, limit)
