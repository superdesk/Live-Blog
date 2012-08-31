'''
Created on Aug 30, 2012

@package: livedesk
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mugur Rus

Contains the implementation of the blog type post API.
'''

from ..meta.blog_post import BlogPostEntry
from ally.container import wire
from ally.container.ioc import injected
from ally.exception import InputError, Ref
from ally.internationalization import _
from ally.support.sqlalchemy.session import SessionSupport
from ally.support.sqlalchemy.util_service import buildQuery, buildLimits
from ally.container.support import setup
from livedesk.api.blog_post import QBlogPost, QWithCId, BlogPost
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm.util import aliased
from sqlalchemy.sql import functions as fn
from superdesk.person.meta.person import PersonMapped
from superdesk.post.api.post import IPostService, Post, QPostUnpublished
from superdesk.post.meta.type import PostTypeMapped
from sqlalchemy.sql.operators import desc_op
from livedesk.api.blog_type_post import IBlogTypePostService
from livedesk.meta.blog_type_post import BlogTypePostMapped

# --------------------------------------------------------------------

UserPerson = aliased(PersonMapped)

@injected
@setup(IBlogTypePostService)
class BlogTypePostServiceAlchemy(SessionSupport, IBlogTypePostService):
    '''
    Implementation for @see: IBlogPostService
    '''

    postService = IPostService; wire.entity('postService')

    def __init__(self):
        '''
        Construct the blog post service.
        '''
        assert isinstance(self.postService, IPostService), 'Invalid post service %s' % self.postService
        SessionSupport.__init__(self)

    def getById(self, blogTypeId, postId):
        '''
        @see: IBlogPostService.getById
        '''
        sql = self.session().query(BlogTypePostMapped)
        sql = sql.filter(BlogTypePostMapped.Blog == blogTypeId)
        sql = sql.filter(BlogTypePostMapped.Id == postId)

        try: return sql.one()
        except NoResultFound: raise InputError(Ref(_('No such blog post'), ref=BlogTypePostMapped.Id))

    def getAll(self, blogTypeId, typeId=None, offset=None, limit=None, q=None):
        '''
        @see: IBlogPostService.getAll
        '''
        assert q is None or isinstance(q, QBlogPost), 'Invalid query %s' % q
        sql = self._buildQuery(blogTypeId, typeId, q)

        sql = sql.order_by(desc_op(BlogTypePostMapped.ordering))
        sql = buildLimits(sql, offset, limit)
        return self._trimmDeleted(sql.all())

    def insert(self, blogTypeId, post):
        '''
        @see: IBlogPostService.insert
        '''
        assert isinstance(post, Post), 'Invalid post %s' % post

        postEntry = BlogPostEntry(Blog=blogTypeId, blogPostId=self.postService.insert(post))
        postEntry.CId = self._nextCId()
        self.session().add(postEntry)

        return postEntry.blogPostId

    def update(self, blogTypeId, post):
        '''
        @see: IBlogPostService.update
        '''
        assert isinstance(post, Post), 'Invalid post %s' % post

        self.postService.update(post)

        postEntry = BlogPostEntry(Blog=blogTypeId, blogPostId=post.Id)
        postEntry.CId = self._nextCId()
        self.session().merge(postEntry)

    def reorder(self, blogTypeId, postId, refPostId, before=True):
        '''
        @see: IBlogPostService.reorder
        '''
        sql = self.session().query(BlogTypePostMapped.ordering)
        sql = sql.filter(BlogTypePostMapped.Blog == blogTypeId)
        sql = sql.filter(BlogTypePostMapped.Id == refPostId)
        order = sql.scalar()

        if not order: raise InputError(Ref(_('Invalid before post')))

        sql = self.session().query(BlogTypePostMapped.ordering)
        sql = sql.filter(BlogTypePostMapped.Blog == blogTypeId)
        sql = sql.filter(BlogTypePostMapped.Id != postId)
        if before:
            sql = sql.filter(BlogTypePostMapped.ordering > order)
            sql = sql.order_by(BlogTypePostMapped.ordering)
        else:
            sql = sql.filter(BlogTypePostMapped.ordering < order)
            sql = sql.order_by(desc_op(BlogTypePostMapped.ordering))

        sql = sql.limit(1)

        orderPrev = sql.scalar()

        if orderPrev: order = (order + orderPrev) / 2
        else: order -= 1

        sql = self.session().query(BlogTypePostMapped)
        sql = sql.filter(BlogTypePostMapped.Blog == blogTypeId)
        sql = sql.filter(BlogTypePostMapped.Id == postId)

        post = self.getById(blogTypeId, postId)
        assert isinstance(post, BlogTypePostMapped)

        post.ordering = order
        self.session().merge(post)

    def delete(self, id):
        '''
        @see: IBlogPostService.delete
        '''
        if self.postService.delete(id):
            postEntry = self.session().query(BlogPostEntry).get(id)
            if postEntry:
                assert isinstance(postEntry, BlogPostEntry)
                postEntry.CId = self._nextCId()
                self.session().flush((postEntry,))
            return True
        return False

    # ----------------------------------------------------------------

    def _buildQuery(self, blogTypeId, typeId=None, q=None):
        '''
        Builds the general query for posts.
        '''
        sql = self.session().query(BlogTypePostMapped)
        sql = sql.filter(BlogTypePostMapped.Blog == blogTypeId)

        if typeId: sql = sql.join(PostTypeMapped).filter(PostTypeMapped.Key == typeId)
        addDeleted = False
        if q:
            sql = buildQuery(sql, q, BlogTypePostMapped)
            addDeleted = QPostUnpublished.deletedOn in q or QWithCId.cId in q
        if not addDeleted: sql = sql.filter(BlogTypePostMapped.DeletedOn == None)
        return sql

    def _trimmDeleted(self, posts):
        '''
        Trim the information from the deleted posts.
        '''
        for post in posts:
            assert isinstance(post, BlogPost)
            if BlogPost.DeletedOn in post and post.DeletedOn is not None:
                trimmed = BlogPost()
                trimmed.Id = post.Id
                trimmed.CId = post.CId
                trimmed.DeletedOn = post.DeletedOn
                yield trimmed
            else:
                yield post

    def _nextOrdering(self, blogTypeId):
        '''
        Provides the next ordering.
        '''
        max = self.session().query(fn.max(BlogTypePostMapped.ordering)).filter(BlogTypePostMapped.Blog == blogTypeId).scalar()
        if max: return max + 1
        return 1
