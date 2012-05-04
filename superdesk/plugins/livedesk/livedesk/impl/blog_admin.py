'''
Created on May 4, 2012

@package: livedesk
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Contains the SQL alchemy meta for blog administrators API.
'''

from ..api.blog_admin import IBlogAdminService
from ally.container.ioc import injected
from ally.exception import InputError, Ref
from ally.internationalization import _
from ally.support.sqlalchemy.util_service import buildLimits
from livedesk.meta.blog_admin import BlogAdminMapped
from sql_alchemy.impl.entity import EntityGetServiceAlchemy
from sqlalchemy.exc import OperationalError

# --------------------------------------------------------------------

@injected
class BlogAdminServiceAlchemy(EntityGetServiceAlchemy, IBlogAdminService):
    '''
    Implementation for @see: IBlogAdminService
    '''

    def __init__(self):
        '''
        Construct the blog administrator service.
        '''
        EntityGetServiceAlchemy.__init__(self, BlogAdminMapped)

    def getAll(self, blogId=None, userId=None, offset=None, limit=None):
        '''
        @see: IBlogAdminService.getAll
        '''
        sql = self.session().query(BlogAdminMapped)
        if blogId: sql = sql.filter(BlogAdminMapped.Blog == blogId)
        if userId: sql = sql.filter(BlogAdminMapped.User == userId)
        sql = buildLimits(sql, offset, limit)
        return sql.all()

    def addAdmin(self, blogId, userId):
        '''
        @see: IBlogAdminService.addAdmin
        '''
        sql = self.session().query(BlogAdminMapped)
        sql = sql.filter(BlogAdminMapped.Blog == blogId)
        sql = sql.filter(BlogAdminMapped.User == userId)
        if sql.count() > 0: raise InputError(_('Already an administrator for this blog'))

        bgu = BlogAdminMapped()
        bgu.Blog = blogId
        bgu.User = userId
        self.session().add(bgu)
        self.session().flush((bgu,))
        return bgu.Id

    def removeAdmin(self, blogId, userId):
        '''
        @see: IBlogAdminService.removeAdmin
        '''
        try:
            sql = self.session().query(BlogAdminMapped)
            sql = sql.filter(BlogAdminMapped.Blog == blogId)
            sql = sql.filter(BlogAdminMapped.User == userId)
            return sql.delete() > 0
        except OperationalError:
            raise InputError(Ref(_('Cannot remove'), model=BlogAdminMapped))

    def remove(self, userId):
        '''
        @see: IBlogAdminService.remove
        '''
        try:
            return self.session().query(BlogAdminMapped).filter(BlogAdminMapped.Id == id).delete() > 0
        except OperationalError:
            raise InputError(Ref(_('Cannot remove'), model=BlogAdminMapped))
