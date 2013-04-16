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
from sqlalchemy.sql.expression import or_
from superdesk.person.meta.person import PersonMapped
from superdesk.user.meta.user import UserMapped

# --------------------------------------------------------------------

@injected
class SqlArticleSearchProvider(IArticleSearchProvider):
    '''
    Implementation  @see: IArticleSearchProvider
    '''

    def update(self, Article):
        '''
        @see: IArticleSearchProvider.update()
        '''
        # do nothing because all search indexes are automatically managed by database server
        pass

    # ----------------------------------------------------------------

    def delete(self, id):
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
            sql = sql.join(PersonMapped, ArticleMapped.Author == PersonMapped.Id)
            sql = sql.join(UserMapped, ArticleMapped.Creator == UserMapped.Id)

            if QArticle.search in q:
                all = processLike(q.search.all)
                sql = sql.filter(or_(PersonMapped.FullName.like(all), UserMapped.FullName.like(all), ArticleMapped.Content.like(all)))

        count = sql.count()

        sql = buildLimits(sql, offset, limit)

        return (sql, count)

#----------------------------------------------------------------

def processLike(value):
    assert isinstance(value, str), 'Invalid like value %s' % value

    if not value:
        return '%'

    if not value.endswith('%'):
        value = value + '%'

    if not value.startswith('%'):
        value = '%' + value

    return value
