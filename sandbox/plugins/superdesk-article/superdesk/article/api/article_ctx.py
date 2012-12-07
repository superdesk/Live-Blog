'''
Created on Sept 26, 2012

@package ally core request
@copyright 2011 Sourcefabric o.p.s.
@license http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mihai Balaceanu
'''

from .article import Article
from superdesk.api.domain_superdesk import modelSuperDesk
from ally.support.api.entity import Entity, IEntityNQService
from ally.api.config import service, call
from ally.api.type import Iter

# --------------------------------------------------------------------

@modelSuperDesk
class ArticleCtx(Entity):
    '''
    Article Content model
    '''
    Id = int
    Article = Article
    Content = str
    Type = int
    
@service((Entity, ArticleCtx))    
class IArticleCtxService(IEntityNQService):
    '''
    '''
   
    @call
    def getAll(self, articleId:Article, offset:int=None, limit:int=None) -> Iter(ArticleCtx):
        '''
        '''
