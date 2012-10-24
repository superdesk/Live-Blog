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
from ally.support.sqlalchemy.session import SessionSupport
from ally.container.support import setup
from livedesk.meta.blog_admin import AdminMapped, AdminEntry
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm.exc import NoResultFound

# --------------------------------------------------------------------

@injected
@setup(IBlogAdminService)
class BlogAdminServiceAlchemy(SessionSupport, IBlogAdminService):
    '''
    Implementation for @see: IBlogAdminService
    '''

    def __init__(self):
        '''
        Construct the blog administrator service.
        '''

    def getById(self, blogId, userId):
        '''
        @see: IBlogAdminService.getById
        '''
        sql = self.session().query(AdminMapped)
        sql = sql.filter(AdminMapped.Blog == blogId)
        sql = sql.filter(AdminMapped.Id == userId)

        try: return sql.one()
        except NoResultFound: raise InputError(Ref(_('No administrator'), ref=AdminMapped.Id))

    def getAll(self, blogId):
        '''
        @see: IBlogAdminService.getAll
        '''
        sql = self.session().query(AdminMapped).filter(AdminMapped.Blog == blogId)
        return sql.all()

    def addAdmin(self, blogId, userId):
        '''
        @see: IBlogAdminService.addAdmin
        '''
        sql = self.session().query(AdminEntry)
        sql = sql.filter(AdminEntry.Blog == blogId)
        sql = sql.filter(AdminEntry.adminId == userId)
        if sql.count() > 0: raise InputError(Ref(_('Already an administrator'), ref=AdminMapped.Id))

        bge = AdminEntry()
        bge.Blog = blogId
        bge.adminId = userId
        self.session().add(bge)
        self.session().flush((bge,))
        return bge.adminId

    def removeAdmin(self, blogId, userId):
        '''
        @see: IBlogAdminService.removeAdmin
        '''
        try:
            sql = self.session().query(AdminEntry)
            sql = sql.filter(AdminEntry.Blog == blogId)
            sql = sql.filter(AdminEntry.adminId == userId)
            return sql.delete() > 0
        except OperationalError:
            raise InputError(Ref(_('Cannot remove'), model=AdminMapped))
