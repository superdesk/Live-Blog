'''
Created on Sept 26, 2012

@package ally core request
@copyright 2011 Sourcefabric o.p.s.
@license http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mihai Balaceanu
'''

from superdesk.article.api.article_ctx import IArticleCtxService
from sql_alchemy.impl.entity import EntityNQServiceAlchemy
from superdesk.article.meta.article_ctx import ArticleCtxMapped
from ally.container.ioc import injected
from ally.container.support import setup
from ally.support.sqlalchemy.util_service import buildLimits

# --------------------------------------------------------------------

@injected
@setup(IArticleCtxService)
class ArticleCtxServiceAlchemy(EntityNQServiceAlchemy, IArticleCtxService):
    
    def __init__(self):
        EntityNQServiceAlchemy.__init__(self, ArticleCtxMapped)
        
    # ---------------------------------------------------------------- <- really cool looking line

    def _buildQuery(self, articleId):
        '''
        Builds the general query for contexts.
        '''
        sql = self.session().query(ArticleCtxMapped)
        sql = sql.filter(ArticleCtxMapped.Article == articleId)

        return sql
        
    def getAll(self, articleId, offset=None, limit=None):
        '''
        @see: IArticleCtxService.getAll
        '''
        sql = self._buildQuery(articleId)
        sql = buildLimits(sql, offset, limit)
        return sql.all()