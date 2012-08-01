'''
Created on Aug 25, 2011

@package Newscoop
@copyright 2011 Sourcefabric o.p.s.
@license http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

SQL alchemy implementation for article API.
'''

from ..api.article import Article, IArticleService
from .entity import EntityService

# --------------------------------------------------------------------

class ArticleService(EntityService, IArticleService):
    '''
    Implementation for @see: IArticleService
    '''
    
    def __init__(self): EntityService.__init__(self, Article)
    
    def getByArticleType(self, id, offset=None, limit=None):
        '''
        @see: IArticleService.getByArticleType
        '''
        return [art for art in self._entityById.values() if art.Type == id]
