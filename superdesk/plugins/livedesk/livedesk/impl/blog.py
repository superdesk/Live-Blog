'''
Created on May 4, 2012

@package: livedesk
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Contains the SQL alchemy meta for blog API.
'''

from ..api.blog import IBlogService
from ally.container.ioc import injected
from sql_alchemy.impl.entity import EntityGetCRUDServiceAlchemy
from ally.support.sqlalchemy.util_service import buildQuery, buildLimits
from livedesk.meta.blog import BlogMapped
from livedesk.api.blog import QBlogActive, QBlog

# --------------------------------------------------------------------

@injected
class BlogServiceAlchemy(EntityGetCRUDServiceAlchemy, IBlogService):
    '''
    Implementation for @see: IBlogService
    '''

    def __init__(self):
        '''
        Construct the blog service.
        '''
        EntityGetCRUDServiceAlchemy.__init__(self, BlogMapped)

    def getActiveBlogs(self, languageId=None, creatorId=None, offset=None, limit=None, q=None):
        '''
        @see: IBlogService.getActiveBlogs
        '''
        assert q is None or isinstance(q, QBlogActive), 'Invalid query %s' % q
        sql = self._buildQuery(languageId, creatorId, q)
        sql = sql.filter((BlogMapped.ClosedOn == None) & (BlogMapped.LiveOn != None))
        sql = buildLimits(sql, offset, limit)
        return sql.all()

    def getAllCount(self, languageId=None, creatorId=None, q=None):
        '''
        @see: IBlogService.getAllCount
        '''
        assert q is None or isinstance(q, QBlog), 'Invalid query %s' % q
        return self._buildQuery(languageId, creatorId, q).count()

    def getAll(self, languageId=None, creatorId=None, offset=None, limit=None, q=None):
        '''
        @see: IBlogService.getAll
        '''
        assert q is None or isinstance(q, QBlog), 'Invalid query %s' % q
        sql = self._buildQuery(languageId, creatorId, q)
        sql = buildLimits(sql, offset, limit)
        return sql.all()

    # ----------------------------------------------------------------

    def _buildQuery(self, languageId=None, creatorId=None, q=None):
        '''
        Builds the general query for blogs.
        '''
        sql = self.session().query(BlogMapped)
        if languageId: sql = sql.filter(BlogMapped.Language == languageId)
        if creatorId: sql = sql.filter(BlogMapped.Creator == creatorId)
        if q: sql = buildQuery(sql, q, BlogMapped)
        return sql
