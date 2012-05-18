'''
Created on May 4, 2012

@package: livedesk
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor


Contains the SQL alchemy meta for livedesk blog posts API.
'''

from ..api.blog_post import IBlogPostService
from ..meta.blog_post import BlogPostMapped, BlogPostEntry
from ally.container import wire
from ally.container.ioc import injected
from ally.support.sqlalchemy.util_service import buildQuery, buildLimits, handle
from livedesk.api.blog_post import BlogPost
from sqlalchemy.exc import SQLAlchemyError
from superdesk.post.api.post import QPostUnpublished, QPostPublished, \
    IPostService, Post
from superdesk.collaborator.meta.collaborator import CollaboratorMapped
from superdesk.person.meta.person import PersonMapped
from superdesk.source.meta.source import SourceMapped
from sqlalchemy.orm.util import aliased
from ally.support.sqlalchemy.session import SessionSupport
from sqlalchemy.orm.exc import NoResultFound
from ally.exception import InputError, Ref
from ally.internationalization import _
from datetime import datetime

# --------------------------------------------------------------------

UserPerson = aliased(PersonMapped)

@injected
class BlogPostServiceAlchemy(SessionSupport, IBlogPostService):
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

    def getById(self, blogId, postId):
        '''
        @see: IBlogPostService.getById
        '''
        sql = self.session().query(BlogPostMapped)
        sql = sql.filter(BlogPostMapped.Blog == blogId)
        sql = sql.filter(BlogPostMapped.Id == postId)

        try: return sql.one()
        except NoResultFound: raise InputError(Ref(_('No such blog post'), ref=BlogPostMapped.Id))

    def getPublished(self, blogId, creatorId=None, authorId=None, offset=None, limit=None, q=None):
        '''
        @see: IBlogPostService.getPublished
        '''
        assert q is None or isinstance(q, QPostPublished), 'Invalid query %s' % q
        sql = self._buildQuery(blogId, creatorId, authorId, q)
        sql = sql.filter(BlogPostMapped.PublishedOn != None)
        if not q: sql = sql.order_by(BlogPostMapped.PublishedOn.desc())
        sql = buildLimits(sql, offset, limit)
        return (post for post in sql.all())

    def getUnpublished(self, blogId, creatorId=None, authorId=None, offset=None, limit=None, q=None):
        '''
        @see: IBlogPostService.getUnpublished
        '''
        assert q is None or isinstance(q, QPostUnpublished), 'Invalid query %s' % q
        sql = self._buildQuery(blogId, creatorId, authorId, q)
        sql = sql.filter(BlogPostMapped.PublishedOn == None)
        sql = buildLimits(sql, offset, limit)
        return (post for post in sql.all())

    def insert(self, blogId, post):
        '''
        @see: IBlogPostService.insert
        '''
        assert isinstance(post, Post), 'Invalid post %s' % post
        post.CreatedOn = datetime.now()
        postDb = BlogPostEntry()
        postDb.Blog = blogId
        postDb.blogPostId = self.postService.insert(post)
        try:
            self.session().add(postDb)
            self.session().flush((postDb,))
        except SQLAlchemyError as e: handle(e, BlogPost)
        return postDb.blogPostId

    def publish(self, blogId, postId):
        '''
        @see: IBlogPostService.publish
        '''
        post = self.getById(blogId, postId)
        assert isinstance(post, Post)
        if post.PublishedOn: raise InputError(Ref(_('Already published'), ref=Post.PublishedOn))
        post.PublishedOn = datetime.now()
        self.postService.update(post)
        return postId

    def insertAndPublish(self, blogId, post):
        '''
        @see: IBlogPostService.insertAndPublish
        '''
        assert isinstance(post, Post), 'Invalid post %s' % post
        post.CreatedOn = post.PublishedOn = datetime.now()
        postDb = BlogPostEntry()
        postDb.Blog = blogId
        postDb.blogPostId = self.postService.insert(post)
        try:
            self.session().add(postDb)
            self.session().flush((postDb,))
        except SQLAlchemyError as e: handle(e, BlogPost)
        return postDb.blogPostId

    def update(self, blogId, post):
        '''
        @see: IBlogPostService.update
        '''
        assert isinstance(post, Post), 'Invalid post %s' % post
        post.UpdatedOn = datetime.now()
        self.postService.update(post)

    # ----------------------------------------------------------------

    def _buildQuery(self, blogId, creatorId=None, authorId=None, q=None):
        '''
        Builds the general query for posts.
        '''
        sql = self.session().query(BlogPostMapped)
        sql = sql.outerjoin(CollaboratorMapped).outerjoin(PersonMapped).outerjoin(SourceMapped)
        sql = sql.join(UserPerson, BlogPostMapped.Creator == UserPerson.Id)
        sql = sql.filter(BlogPostMapped.Blog == blogId)
        if creatorId: sql = sql.filter(BlogPostMapped.Creator == creatorId)
        if authorId: sql = sql.filter(BlogPostMapped.Author == authorId)
        if q: sql = buildQuery(sql, q, BlogPostMapped)
        return sql
