'''
Created on Mar 21, 2013
@package: superdesk media archive
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Ioan v. Pocol

The implementation for db based search API.
'''
from content.article.api.search_provider import IArticleSearchProvider
from ally.container.ioc import injected
from content.article.api.article import QArticle
from ally.support.sqlalchemy.util_service import buildLimits, buildQuery
from content.article.meta.article import ArticleMapped

# --------------------------------------------------------------------

@injected
class SqlArticleSearchProvider(IArticleSearchProvider):
    '''
    Implementation  @see: IArticleSearchProvider
    '''

    def update(self, metaInfo, metaData):
        '''
        @see: IArticleSearchProvider.update()
        '''
        # do nothing because all search indexes are automatically managed by database server
        pass

    # ----------------------------------------------------------------

    def delete(self, idMetaInfo, metaType):
        '''
        @see: IArticleSearchProvider.delete()
        '''
        # do nothing because all search indexes are automatically managed by database server
        pass

    # ----------------------------------------------------------------

    def buildQuery(self, session, offset=None, limit=1000, q=None):
        '''
        @see: IArticleSearchProvider.buildQuery()
        '''
        
        sql = session.query(ArticleMapped)
        
        if q:
            sql = buildQuery(sql, q, ArticleMapped)
            
            if QArticle.search in q:
                all = q.search.all
                print(all)
                
            
        sql = buildLimits(sql, offset, limit)
        
        #TODO: add all search
        
        return sql