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
from sql_alchemy.impl.entity import EntityGetCRUDServiceAlchemy
from sqlalchemy.exc import SQLAlchemyError
from superdesk.post.api.post import QPostUnpublished, QPostPublished, \
    IPostService
from superdesk.collaborator.meta.collaborator import CollaboratorMapped
from superdesk.person.meta.person import Person
from superdesk.source.meta.source import SourceMapped
from sqlalchemy.orm.util import aliased

# --------------------------------------------------------------------

UserPerson = aliased(Person)

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
        if not q: sql = sql.order_by(BlogPostMapped.PublishedOn.desc())
        sql = buildLimits(sql, offset, limit)
        return (post for post in self._processResults(sql.all()))

    def getUnpublished(self, blogId, creatorId=None, authorId=None, offset=None, limit=None, q=None):
        '''
        @see: IBlogPostService.getUnpublished
        '''
        assert q is None or isinstance(q, QPostUnpublished), 'Invalid query %s' % q
        sql = self._buildQuery(blogId, creatorId, authorId, q)
        sql = sql.filter(BlogPostMapped.PublishedOn == None)
        sql = buildLimits(sql, offset, limit)
        return (post for post in self._processResults(sql.all()))

    def insert(self, post):
        '''
        @see: IBlogPostService.insert
        '''
        assert isinstance(post, BlogPost), 'Invalid post %s' % post
        postDb = BlogPostEntry()
        postDb.Id = self.postService.insert(post)
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
        sql = self.session().query(BlogPostMapped, Person.FirstName, Person.LastName, SourceMapped.Name,
                                   UserPerson.FirstName, UserPerson.LastName)
        sql = sql.outerjoin(CollaboratorMapped).outerjoin(Person).outerjoin(SourceMapped)
        sql = sql.join(UserPerson, BlogPostMapped.Creator == UserPerson.Id)
        sql = sql.filter(BlogPostMapped.Blog == blogId)
        if creatorId: sql = sql.filter(BlogPostMapped.Creator == creatorId)
        if authorId: sql = sql.filter(BlogPostMapped.Author == authorId)
        if q: sql = buildQuery(sql, q, BlogPostMapped)
        return sql

    def _processResults(self, results):
        '''
        Process the author name based on the results tuples.
        '''
        for result in results:
            post, authorFirstName, authorLastName, sourceName, creatorFirstName, creatorLastName = result
            assert isinstance(post, BlogPost)
            if authorFirstName or authorLastName:
                name = '%s %s' % ('' if authorFirstName is None else authorFirstName,
                                  '' if authorLastName is None else authorLastName)
                post.AuthorName = name.strip()
            elif sourceName:
                post.AuthorName = sourceName
            else:
                name = '%s %s' % ('' if creatorFirstName is None else creatorFirstName,
                                  '' if creatorLastName is None else creatorLastName)
                post.AuthorName = name.strip()
            yield post
