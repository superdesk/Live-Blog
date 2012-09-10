'''
Created on May 4, 2012

@package: livedesk
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Contains the SQL alchemy meta for blog API.
'''

from ..api.blog import IBlogService, QBlog, Blog
from ..meta.blog import BlogMapped
from ..meta.blog_admin import AdminEntry
from ally.container.ioc import injected
from ally.exception import InputError, Ref
from ally.internationalization import _
from ally.support.sqlalchemy.util_service import buildQuery, buildLimits
from datetime import datetime
from sql_alchemy.impl.entity import EntityCRUDServiceAlchemy
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.sql.expression import exists
from ally.api.extension import IterPart

# --------------------------------------------------------------------

@injected
class BlogServiceAlchemy(EntityCRUDServiceAlchemy, IBlogService):
    '''
    Implementation for @see: IBlogService
    '''

    def __init__(self):
        '''
        Construct the blog service.
        '''
        EntityCRUDServiceAlchemy.__init__(self, BlogMapped)

    def getBlog(self, blogId):
        '''
        @see: IBlogService.getBlog
        '''
        sql = self.session().query(BlogMapped)
        sql = sql.filter(BlogMapped.Id == blogId)

        try: return sql.one()
        except NoResultFound: raise InputError(Ref(_('Unknown id'), ref=Blog.Id))

    def getAll(self, languageId=None, adminId=None, offset=None, limit=None, detailed=False, q=None):
        '''
        @see: IBlogService.getAll
        '''
        sql = self._buildQuery(languageId, adminId, q)
        sqlLimit = buildLimits(sql, offset, limit)
        if detailed: return IterPart(sqlLimit.all(), sql.count(), offset, limit)
        return sqlLimit.all()

    def getLiveWhereAdmin(self, adminId, languageId=None, q=None):
        '''
        @see: IBlogService.getLiveWhereAdmin
        '''
        sql = self._buildQuery(languageId, adminId, q)
        sql = sql.filter(BlogMapped.ClosedOn == None)
        return sql.all()

    def getLive(self, languageId=None, q=None):
        '''
        @see: IBlogService.getLive
        '''
        sql = self._buildQuery(languageId, None, q)
        sql = sql.filter((BlogMapped.ClosedOn == None) & (BlogMapped.LiveOn != None))
        return sql.all()

    def insert(self, blog):
        '''
        @see: IBlogService.insert
        '''
        assert isinstance(blog, Blog), 'Invalid blog %s' % blog
        if blog.CreatedOn is None: blog.CreatedOn = datetime.now()
        return super().insert(blog)

    # ----------------------------------------------------------------

    def _buildQuery(self, languageId=None, adminId=None, q=None):
        '''
        Builds the general query for blogs.
        '''
        sql = self.session().query(BlogMapped)
        if languageId: sql = sql.filter(BlogMapped.Language == languageId)
        if adminId:
            sql = sql.filter((BlogMapped.Creator == adminId) |
                             exists().where((AdminEntry.adminId == adminId) & (AdminEntry.Blog == BlogMapped.Id)))
        if q:
            assert isinstance(q, QBlog), 'Invalid query %s' % q
            sql = buildQuery(sql, q, BlogMapped)
        return sql
