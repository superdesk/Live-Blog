'''
Created on August 28, 2013

@package: livedesk
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Martin Saturka

Contains the SQL alchemy meta for livedesk blog post users API.
'''

from livedesk.api.blog_post_user import IBlogPostUserService
from livedesk.meta.blog_post_user import BlogPostUserDB
from livedesk.meta.blog import BlogMapped
from ally.container.ioc import injected
from ally.container.support import setup
from ally.support.sqlalchemy.util_service import buildLimits
from ally.support.sqlalchemy.session import SessionSupport
from superdesk.post.meta.post import PostMapped
from superdesk.user.meta.user import UserMapped
from ally.api.extension import IterPart
from ally.exception import InputError, Ref
from ally.internationalization import _
from sqlalchemy.orm.exc import NoResultFound

# --------------------------------------------------------------------

@injected
@setup(IBlogPostUserService, name='blogPostUserService')
class BlogPostUserServiceAlchemy(SessionSupport, IBlogPostUserService):
    '''
    Implementation for @see: IBlogPostUserService
    '''

    def __init__(self):
        '''
        Construct the blog post user service.
        '''

    def getUser(self, blogId, postId):
        '''
        @see: IBlogPostUserService.getUser
        '''
        sql = self.session().query(UserMapped)

        sql = sql.join(BlogPostUserDB, UserMapped.Id == BlogPostUserDB.user)
        sql = sql.filter(BlogPostUserDB.blog == blogId)
        sql = sql.filter(BlogPostUserDB.post == postId)

        try:
            user = sql.one()
        except NoResultFound:
            raise InputError(Ref(_('No user attached'),))
        return user

    def getAllUsers(self, blogId, postId, offset=None, limit=None, detailed=False):
        '''
        @see: IBlogPostUserService.getAllUsers
        '''
        sql = self.session().query(UserMapped)

        sql = sql.join(BlogPostUserDB, UserMapped.Id == BlogPostUserDB.user)
        sql = sql.filter(BlogPostUserDB.blog == blogId)
        sql = sql.filter(BlogPostUserDB.post == postId)

        sqlLimit = buildLimits(sql, offset, limit)
        if detailed: return IterPart(sqlLimit.all(), sql.count(), offset, limit)
        return sqlLimit.all()

    def attach(self, blogId, postId, userId):
        '''
        @see: IBlogPostUserService.attach
        '''
        self.detach(blogId, postId)

        blogPostUserDb = BlogPostUserDB()

        blogPostUserDb.blog = blogId
        blogPostUserDb.post = postId
        blogPostUserDb.user = userId

        try:
            self.session().add(blogPostUserDb)
            self.session().flush((blogPostUserDb,))
        except SQLAlchemyError as e:
            raise InputError(Ref(_('Can not attach the user'),))

    def detach(self, blogId, postId, userId=None):
        '''
        @see: IBlogPostUserService.detach
        '''
        try:
            sql = self.session().query(BlogPostUserDB)
            sql = sql.filter(BlogPostUserDB.blog == blogId)
            sql = sql.filter(BlogPostUserDB.post == postId)
            if userId:
                sql = sql.filter(BlogPostUserDB.user == userId)
            return sql.delete() > 0
        except OperationalError:
            if userId:
                raise InputError(Ref(_('Can not detach the user'),))
            else:
                raise InputError(Ref(_('Can not detach current users'),))
