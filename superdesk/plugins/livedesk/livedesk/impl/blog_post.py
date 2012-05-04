'''
Created on May 4, 2012

@package: livedesk
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor


Contains the SQL alchemy meta for livedesk blog posts API.
'''

from ..api.blog_post import IBlogPostService
from ..meta.blog_post import BlogPostMapped
from ally.container import wire
from ally.container.ioc import injected
from ally.support.sqlalchemy.util_service import buildQuery, buildLimits, handle
from livedesk.api.blog_post import BlogPost
from sql_alchemy.impl.entity import EntityGetCRUDServiceAlchemy
from sqlalchemy.exc import SQLAlchemyError
from superdesk.post.api.post import QPostUnpublished, QPostPublished, \
    IPostService

# --------------------------------------------------------------------

@injected
class BlogPostServiceAlchemy(EntityGetCRUDServiceAlchemy, IBlogPostService):
    '''
    Implementation for @see: IBlogPostService
    '''

    postService = IPostService; wire.entity('postService')

    def __init__(self):
        '''
        Construct the blog post service.
        '''
        assert isinstance(self.postService, IPostService), 'Invalid post service %s' % self.postService
        EntityGetCRUDServiceAlchemy.__init__(self, BlogPostMapped)

    def getPublished(self, blogId, creatorId=None, authorId=None, offset=None, limit=None, q=None):
        '''
        @see: IBlogPostService.getPublished
        '''
        assert q is None or isinstance(q, QPostPublished), 'Invalid query %s' % q
        sql = self._buildQuery(blogId, creatorId, authorId, q)
        sql = sql.filter(BlogPostMapped.PublishedOn != None)
        sql = buildLimits(sql, offset, limit)
        return sql.all()

    def getUnpublished(self, blogId, creatorId=None, authorId=None, offset=None, limit=None, q=None):
        '''
        @see: IBlogPostService.getUnpublished
        '''
        assert q is None or isinstance(q, QPostUnpublished), 'Invalid query %s' % q
        sql = self._buildQuery(blogId, creatorId, authorId, q)
        sql = sql.filter(BlogPostMapped.PublishedOn == None)
        sql = buildLimits(sql, offset, limit)
        return sql.all()

    def insert(self, post):
        '''
        @see: IBlogPostService.insert
        '''
        assert isinstance(post, BlogPost), 'Invalid post %s' % post
        postDb = BlogPostMapped()
        postDb.Id = self.insert(post)
        postDb.Blog = post.Blog
        try:
            self.session().add(postDb)
            self.session().flush((postDb,))
        except SQLAlchemyError as e: handle(e, BlogPost)
        return postDb.Id

    def update(self, post):
        '''
        @see: IBlogPostService.update
        '''
        assert isinstance(post, BlogPost), 'Invalid post %s' % post
        self.postService.update(post)

    # ----------------------------------------------------------------

    def _buildQuery(self, blogId, creatorId=None, authorId=None, q=None):
        '''
        Builds the general query for posts.
        '''
        sql = self.session().query(BlogPostMapped).filter(BlogPostMapped.Blog == blogId)
        if creatorId: sql = sql.filter(BlogPostMapped.Creator == creatorId)
        if authorId: sql = sql.filter(BlogPostMapped.Author == authorId)
        if q: sql = buildQuery(sql, q, BlogPostMapped)
        return sql
