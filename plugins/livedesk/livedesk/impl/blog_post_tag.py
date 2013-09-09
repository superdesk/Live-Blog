'''
Created on August 26, 2013

@package: livedesk
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Martin Saturka

Contains the SQL alchemy meta for livedesk blog post tags API.
'''

from livedesk.api.blog_post_tag import IBlogPostTagService
from livedesk.meta.blog_post_tag import BlogPostTagDB
from livedesk.meta.blog import BlogMapped
from ally.container.ioc import injected
from ally.container.support import setup
from ally.support.sqlalchemy.util_service import buildLimits
from ally.support.sqlalchemy.session import SessionSupport
from superdesk.post.meta.post import PostMapped
from superdesk.tag.meta.tag import TagMapped
from superdesk.tag.meta.type import TagTypeMapped
from ally.api.extension import IterPart
from ally.exception import InputError, Ref
from ally.internationalization import _
from sqlalchemy.orm.exc import NoResultFound

# --------------------------------------------------------------------

@injected
@setup(IBlogPostTagService, name='blogPostTagService')
class BlogPostTagServiceAlchemy(SessionSupport, IBlogPostTagService):
    '''
    Implementation for @see: IBlogPostTagService
    '''

    def __init__(self):
        '''
        Construct the blog post tag service.
        '''

    def getTagType(self, blogId, postId, tagTypeKey):
        '''
        @see: IBlogSourceService.getTagType
        '''
        try:
            tagType = self.session().query(TagTypeMapped).filter(TagTypeMapped.Key == tagTypeKey).one()
        except NoResultFound:
            raise InputError(Ref(_('Unknown tag type'),))
        return tagType

    def getAllTagTypes(self, blogId, postId, offset=None, limit=None, detailed=False):
        '''
        @see: IBlogPostTagService.getAllTagTypes
        '''
        sql = self.session().query(TagTypeMapped)

        sqlLimit = buildLimits(sql, offset, limit)
        if detailed: return IterPart(sqlLimit.all(), sql.count(), offset, limit)
        return sqlLimit.all()

    def getAll(self, blogId, postId, tagTypeKey, offset=None, limit=None, detailed=False):
        '''
        @see: IBlogPostTagService.getAll
        '''
        sql = self.session().query(TagMapped)

        sql = sql.join(BlogPostTagDB, TagMapped.id == BlogPostTagDB.tag)
        sql = sql.filter(BlogPostTagDB.blog == blogId)
        sql = sql.filter(BlogPostTagDB.post == postId)

        sql = sql.join(TagTypeMapped, TagTypeMapped.id == TagMapped.typeId)
        sql = sql.filter(TagTypeMapped.Key == tagTypeKey)

        sqlLimit = buildLimits(sql, offset, limit)
        if detailed: return IterPart(sqlLimit.all(), sql.count(), offset, limit)
        return sqlLimit.all()

    def attach(self, blogId, postId, tagTypeKey, tagKey):
        '''
        @see: IBlogPostTagService.attach
        '''
        blogPostTagDb = BlogPostTagDB()

        blogPostTagDb.blog = blogId
        blogPostTagDb.post = postId
        blogPostTagDb.tag = self._tagId(tagTypeKey, tagKey)

        try:
            self.session().add(blogPostTagDb)
            self.session().flush((blogPostTagDb,))
        except SQLAlchemyError as e:
            raise InputError(Ref(_('Can not attach the tag'),))

    def detach(self, blogId, postId, tagTypeKey, tagKey):
        '''
        @see: IBlogPostTagService.detach
        '''
        tagId = self._tagId(tagTypeKey, tagKey)

        try:
            sql = self.session().query(BlogPostTagDB)
            sql = sql.filter(BlogPostTagDB.blog == blogId)
            sql = sql.filter(BlogPostTagDB.post == postId)
            sql = sql.filter(BlogPostTagDB.tag == tagId)
            return sql.delete() > 0
        except OperationalError:
            raise InputError(Ref(_('Can not detach the tag'),))

    # ----------------------------------------------------------------

    def _tagId(self, typeKey, key):
        '''
        Provides the tag id that has the provided key and type of type key.
        '''
        try:
            sql = self.session().query(TagMapped.id)
            sql = sql.filter(TagMapped.Key == key)

            sql = sql.join(TagTypeMapped, TagTypeMapped.id == TagMapped.typeId)
            sql = sql.filter(TagTypeMapped.Key == typeKey)

            return sql.one()[0]
        except NoResultFound:
            raise InputError(Ref(_('Invalid combination of tag type %(type)s and tag %(tag)s') % dict(type=typeKey, tag=key),))
