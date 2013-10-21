'''
Created on May 4, 2012

@package: livedesk
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor


Contains the SQL alchemy meta for livedesk blog posts API.
'''

from ..api.blog_post import IBlogPostService, QBlogPostUnpublished, \
    QBlogPostPublished
from ..meta.blog_post import BlogPostMapped, BlogPostEntry
from ally.container import wire
from ally.container.ioc import injected
from ally.container.support import setup
from ally.exception import InputError, Ref
from ally.internationalization import _
from ally.support.sqlalchemy.session import SessionSupport
from ally.support.sqlalchemy.util_service import buildQuery, buildLimits
from livedesk.api.blog_post import QBlogPost, QWithCId, BlogPost, IterPost
from livedesk.meta.blog_collaborator_group import BlogCollaboratorGroupMemberMapped
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm.util import aliased
from sqlalchemy.sql import functions as fn
from sqlalchemy.sql.expression import func, or_
from sqlalchemy.sql.functions import current_timestamp
from sqlalchemy.sql.operators import desc_op
from superdesk.collaborator.meta.collaborator import CollaboratorMapped
from superdesk.person.meta.person import PersonMapped
from superdesk.person_icon.api.person_icon import IPersonIconService
from superdesk.post.api.post import IPostService, Post, QPostUnpublished
from superdesk.post.meta.type import PostTypeMapped
from livedesk.impl.blog_collaborator_group import updateLastAccessOn

# --------------------------------------------------------------------

UserPerson = aliased(PersonMapped)

@injected
@setup(IBlogPostService, name='blogPostService')
class BlogPostServiceAlchemy(SessionSupport, IBlogPostService):
    '''
    Implementation for @see: IBlogPostService
    '''

    postService = IPostService; wire.entity('postService')
    personIconService = IPersonIconService; wire.entity('personIconService')

    def __init__(self):
        '''
        Construct the blog post service.
        '''
        assert isinstance(self.postService, IPostService), 'Invalid post service %s' % self.postService
        assert isinstance(self.personIconService, IPersonIconService), 'Invalid person icon service %s' % self.personIconService

    def getById(self, blogId, postId, thumbSize=None):
        '''
        @see: IBlogPostService.getById
        '''
        sql = self.session().query(BlogPostMapped)
        sql = sql.filter(BlogPostMapped.Blog == blogId)
        sql = sql.filter(BlogPostMapped.Id == postId)

        try: return self._addImage(sql.one(), thumbSize)
        except NoResultFound: raise InputError(Ref(_('No such blog post'), ref=BlogPostMapped.Id))

    def getPublished(self, blogId, typeId=None, creatorId=None, authorId=None, thumbSize=None, offset=None, limit=None,
                     detailed=False, q=None):
        '''
        @see: IBlogPostService.getPublished
        '''
        assert q is None or isinstance(q, QBlogPostPublished), 'Invalid query %s' % q

        sql = self._filterQuery(blogId, typeId, creatorId, authorId, q)
        if q:
            if QWithCId.cId in q and q.cId:
                sql = sql.filter(BlogPostMapped.CId != None)
            sql = buildQuery(sql, q, BlogPostMapped)
        if q is None or QWithCId.cId not in q:
            sql = sql.filter((BlogPostMapped.PublishedOn != None) & (BlogPostMapped.DeletedOn == None))

        sql = sql.order_by(desc_op(BlogPostMapped.Order))

        sqlLimit = buildLimits(sql, offset, limit)
        posts = self._addImages(self._trimPosts(sqlLimit.all()), thumbSize)
        if detailed:
            posts = IterPost(posts, sql.count(), offset, limit)
            posts.lastCId = self.session().query(func.MAX(BlogPostMapped.CId)).filter(BlogPostMapped.Blog == blogId).scalar()
        return posts

    def getUnpublished(self, blogId, typeId=None, creatorId=None, authorId=None, thumbSize=None, offset=None, limit=None,
                       detailed=False, q=None):
        '''
        @see: IBlogPostService.getUnpublished
        '''
        assert q is None or isinstance(q, QBlogPostUnpublished), 'Invalid query %s' % q
        sql = self._filterQuery(blogId, typeId, creatorId, authorId, q)

        deleted = False
        if q:
            if QBlogPostUnpublished.isDeleted in q:
                deleted = q.isDeleted.value  
            if QWithCId.cId in q and q.cId:
                sql = sql.filter(BlogPostMapped.CId != None)
            sql = buildQuery(sql, q, BlogPostMapped)
            
        if q:
            if QWithCId.cId not in q:
                sql = sql.filter(BlogPostMapped.PublishedOn == None) 
                if deleted: sql = sql.filter(BlogPostMapped.DeletedOn != None)
                else: sql = sql.filter(BlogPostMapped.DeletedOn == None)
        else: sql = sql.filter((BlogPostMapped.PublishedOn == None) & (BlogPostMapped.DeletedOn == None))    

        sql = sql.order_by(desc_op(BlogPostMapped.Order))
        sqlLimit = buildLimits(sql, offset, limit)
        posts = self._addImages(self._trimPosts(sqlLimit.all(), unpublished=False, published=True), thumbSize)
        if detailed:
            posts = IterPost(posts, sql.count(), offset, limit)
            posts.lastCId = self.session().query(func.MAX(BlogPostMapped.CId)).filter(BlogPostMapped.Blog == blogId).scalar()
        return posts
    
    def getUnpublishedBySource(self, sourceId, thumbSize=None, offset=None, limit=None, detailed=False, q=None):
        '''
        @see: IBlogPostService.getUnpublished
        '''
        assert q is None or isinstance(q, QBlogPostUnpublished), 'Invalid query %s' % q
        sql = self._buildQueryBySource(sourceId)
        
        deleted = False
        if q:
            if QBlogPostUnpublished.isDeleted in q:
                deleted = q.isDeleted.value                
            sql = buildQuery(sql, q, BlogPostMapped)
        
        if q:
            if QWithCId.cId not in q or QWithCId.cId in q and QWithCId.cId.start not in q and QWithCId.cId.end not in q:
                sql = sql.filter(BlogPostMapped.PublishedOn == None) 
                if deleted: sql = sql.filter(BlogPostMapped.DeletedOn != None)
                else: sql = sql.filter(BlogPostMapped.DeletedOn == None)
        else: sql = sql.filter((BlogPostMapped.PublishedOn == None) & (BlogPostMapped.DeletedOn == None))     
                            
        sql = sql.order_by(desc_op(BlogPostMapped.Order))
        sqlLimit = buildLimits(sql, offset, limit)
        posts = self._addImages(self._trimPosts(sqlLimit.all(), deleted=deleted, unpublished=False, published=True), thumbSize)
        if detailed:
            posts = IterPost(posts, sql.count(), offset, limit)
            
            lastCidSql = self.session().query(func.MAX(BlogPostMapped.CId))
            lastCidSql = lastCidSql.join(CollaboratorMapped, BlogPostMapped.Author == CollaboratorMapped.Id)
            lastCidSql = lastCidSql.filter(CollaboratorMapped.Source == sourceId)
            
            posts.lastCId = lastCidSql.scalar()
            
        return posts

    def getGroupUnpublished(self, blogId, groupId, typeId=None, authorId=None, thumbSize=None, offset=None, limit=None, q=None):
        '''
        @see: IBlogPostService.getUnpublished
        '''
        assert q is None or isinstance(q, QBlogPostUnpublished), 'Invalid query %s' % q

        updateLastAccessOn(self.session(), groupId)

        sql = self._buildQuery(blogId, typeId, None, authorId, q)
        sql = sql.filter(BlogPostMapped.PublishedOn == None)

        # blog collaborator group
        sql = sql.join(BlogCollaboratorGroupMemberMapped, BlogCollaboratorGroupMemberMapped.BlogCollaborator == BlogPostMapped.Creator)
        sql = sql.filter(BlogCollaboratorGroupMemberMapped.Group == groupId)

        sql = sql.order_by(desc_op(BlogPostMapped.Creator))
        sql = sql.order_by(desc_op(BlogPostMapped.Order))
        sql = buildLimits(sql, offset, limit)
        return self._addImages(sql.all())

    def getOwned(self, blogId, creatorId, typeId=None, thumbSize=None, offset=None, limit=None, q=None):
        '''
        @see: IBlogPostService.getOwned
        '''
        assert q is None or isinstance(q, QBlogPost), 'Invalid query %s' % q
        sql = self._buildQuery(blogId, typeId, creatorId, None, q)
        if q and QBlogPost.isPublished in q:
            if q.isPublished.value: sql = sql.filter(BlogPostMapped.PublishedOn != None)
            else: sql = sql.filter(BlogPostMapped.PublishedOn == None)

        sql = sql.order_by(desc_op(BlogPostMapped.Order))
        sql = buildLimits(sql, offset, limit)
        return self._addImages(sql.all(), thumbSize)

    def getAll(self, blogId, typeId=None, creatorId=None, authorId=None, thumbSize=None, offset=None, limit=None, q=None):
        '''
        @see: IBlogPostService.getAll
        '''
        assert q is None or isinstance(q, QBlogPost), 'Invalid query %s' % q
        sql = self._buildQuery(blogId, typeId, creatorId, authorId, q)

        sql = sql.order_by(desc_op(BlogPostMapped.Order))
        sql = buildLimits(sql, offset, limit)
        return self._addImages(sql.all(), thumbSize)

    def insert(self, blogId, post):
        '''
        @see: IBlogPostService.insert
        '''
        assert isinstance(post, Post), 'Invalid post %s' % post

        postEntry = BlogPostEntry(Blog=blogId, blogPostId=self.postService.insert(post))
        postEntry.CId = self._nextCId()
        postEntry.Order = self._nextOrdering(blogId)
        self.session().add(postEntry)

        return postEntry.blogPostId

    def publish(self, blogId, postId):
        '''
        @see: IBlogPostService.publish
        '''
        post = self.getById(blogId, postId)
        assert isinstance(post, Post)

        if post.PublishedOn: raise InputError(Ref(_('Already published'), ref=Post.PublishedOn))

        post.PublishedOn = current_timestamp()
        post.deletedOn = None
        self.postService.update(post)

        postEntry = BlogPostEntry(Blog=blogId, blogPostId=post.Id)
        postEntry.CId = self._nextCId()
        postEntry.Order = self._nextOrdering(blogId)
        self.session().merge(postEntry)

        return postId
    
    def hide(self, blogId, postId):
        '''
        @see: IBlogPostService.hide
        '''
        post = self.getById(blogId, postId)
        assert isinstance(post, Post)

        if post.PublishedOn: raise InputError(Ref(_('Already published'), ref=Post.PublishedOn))

        post.DeletedOn = current_timestamp()
        self.postService.update(post)

        postEntry = BlogPostEntry(Blog=blogId, blogPostId=post.Id)
        postEntry.CId = self._nextCId()
        postEntry.Order = self._nextOrdering(blogId)
        self.session().merge(postEntry)

        return postId
    
    def unhide(self, blogId, postId):
        '''
        @see: IBlogPostService.unhide
        '''
        post = self.getById(blogId, postId)
        assert isinstance(post, Post)

        if post.PublishedOn: raise InputError(Ref(_('Already published'), ref=Post.PublishedOn))

        post.DeletedOn = None
        self.postService.update(post)

        postEntry = BlogPostEntry(Blog=blogId, blogPostId=post.Id)
        postEntry.CId = self._nextCId()
        postEntry.Order = self._nextOrdering(blogId)
        self.session().merge(postEntry)

        return postId

    def insertAndPublish(self, blogId, post):
        '''
        @see: IBlogPostService.insertAndPublish
        '''
        assert isinstance(post, Post), 'Invalid post %s' % post

        postEntry = BlogPostEntry(Blog=blogId, blogPostId=self.postService.insert(post))
        postEntry.CId = self._nextCId()
        postEntry.Order = self._nextOrdering(blogId)
        self.session().add(postEntry)
        self.session().query(BlogPostMapped).get(postEntry.blogPostId).PublishedOn = current_timestamp()

        return postEntry.blogPostId

    def unpublish(self, blogId, postId):
        '''
        @see: IBlogPostService.unpublish
        '''
        post = self.getById(blogId, postId)
        assert isinstance(post, Post)

        if not post.PublishedOn: raise InputError(Ref(_('Already unpublished'), ref=Post.PublishedOn))

        post.PublishedOn = None
        self.postService.update(post)

        postEntry = BlogPostEntry(Blog=blogId, blogPostId=post.Id)
        postEntry.CId = self._nextCId()
        self.session().merge(postEntry)

        return postId

    def update(self, blogId, post):
        '''
        @see: IBlogPostService.update
        '''
        assert isinstance(post, Post), 'Invalid post %s' % post

        self.postService.update(post)

        postEntry = BlogPostEntry(Blog=blogId, blogPostId=post.Id)
        postEntry.CId = self._nextCId()
        self.session().merge(postEntry)

    def reorder(self, blogId, postId, refPostId, before=True):
        '''
        @see: IBlogPostService.reorder
        '''
        sql = self.session().query(BlogPostMapped.Order)
        sql = sql.filter(BlogPostMapped.Blog == blogId)
        sql = sql.filter(BlogPostMapped.Id == refPostId)
        order = sql.scalar()

        if not order: raise InputError(Ref(_('Invalid before post')))

        sql = self.session().query(BlogPostMapped.Order)
        sql = sql.filter(BlogPostMapped.Blog == blogId)
        sql = sql.filter(BlogPostMapped.Id != postId)
        if before:
            sql = sql.filter(BlogPostMapped.Order > order)
            sql = sql.order_by(BlogPostMapped.Order)
        else:
            sql = sql.filter(BlogPostMapped.Order < order)
            sql = sql.order_by(desc_op(BlogPostMapped.Order))

        sql = sql.limit(1)

        orderPrev = sql.scalar()

        if orderPrev: order = (order + orderPrev) / 2
        elif before: order += 1
        else: order -= 1

        sql = self.session().query(BlogPostMapped)
        sql = sql.filter(BlogPostMapped.Blog == blogId)
        sql = sql.filter(BlogPostMapped.Id == postId)

        post = self.getById(blogId, postId)
        assert isinstance(post, BlogPostMapped)

        post.Order = order
        post.CId = self._nextCId()
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

    def _buildQuery(self, blogId, typeId=None, creatorId=None, authorId=None, q=None):
        '''
        Builds the general query for posts.
        '''
        sql = self._filterQuery(blogId, typeId, creatorId, authorId, q)
        if q:
            sql = buildQuery(sql, q, BlogPostMapped)
            if QPostUnpublished.deletedOn not in q and QWithCId.cId not in q:
                sql = sql.filter(BlogPostMapped.DeletedOn == None)

        return sql
    
    def _filterQuery(self, blogId, typeId=None, creatorId=None, authorId=None, q=None):
        '''
        Creates the general query filter for posts based on the provided parameters.
        '''

        sql = self.session().query(BlogPostMapped)
        sql = sql.filter(BlogPostMapped.Blog == blogId)
        if isinstance(q, QWithCId) and QWithCId.search in q:
            all = self._processLike(q.search.ilike) if q.search.ilike is not None else self._processLike(q.search.like)
            sql = sql.filter(or_(BlogPostMapped.Content.ilike(all), BlogPostMapped.ContentPlain.ilike(all)))

        if typeId: sql = sql.join(PostTypeMapped).filter(PostTypeMapped.Key == typeId)
        if creatorId: sql = sql.filter(BlogPostMapped.Creator == creatorId)
        if authorId:
            sql = sql.filter((BlogPostMapped.Author == authorId) |
                             ((CollaboratorMapped.Id == authorId) &
                              (CollaboratorMapped.User == BlogPostMapped.Creator)))

        return sql

    def _buildQueryBySource(self, sourceId):
        sql = self.session().query(BlogPostMapped)
        sql = sql.join(CollaboratorMapped, BlogPostMapped.Author == CollaboratorMapped.Id)
        sql = sql.filter(CollaboratorMapped.Source == sourceId)
        return sql
    
    def _processLike(self, value):
        assert isinstance(value, str), 'Invalid like value %s' % value

        if not value:
            return '%'

        if not value.endswith('%'):
            value = value + '%'

        if not value.startswith('%'):
            value = '%' + value

        return value

    def _trimPosts(self, posts, deleted=True, unpublished=True, published=False):
        '''
        Trim the information from the deleted posts.
        '''
        for post in posts:
            assert isinstance(post, BlogPostMapped)
            if (deleted and BlogPost.DeletedOn in post and post.DeletedOn is not None) \
            or (unpublished and (BlogPost.PublishedOn not in post or post.PublishedOn is None)) \
            or (published and (BlogPost.PublishedOn in post and post.PublishedOn is not None)):
                trimmed = BlogPost()
                trimmed.Id = post.Id
                trimmed.CId = post.CId
                trimmed.IsPublished = post.IsPublished
                trimmed.DeletedOn = post.DeletedOn
                yield trimmed
            else:
                yield post

    def _nextCId(self):
        '''
        Provides the next change Id.
        '''
        max = self.session().query(fn.max(BlogPostMapped.CId)).scalar()
        if max: return max + 1
        return 1

    def _nextOrdering(self, blogId):
        '''
        Provides the next ordering.
        '''
        max = self.session().query(fn.max(BlogPostMapped.Order)).filter(BlogPostMapped.Blog == blogId).scalar()
        if max: return max + 1
        return 1

    # TODO: nasty
    def _addImage(self, post, thumbSize='medium'):
        '''
        Takes the image for the author or creator and adds the thumbnail to the response
        '''
        assert isinstance(post, BlogPost)
        id = post.AuthorPerson if post.AuthorPerson is not None else post.Creator

        try:
            if id is not None:
                post.AuthorImage = self.personIconService.getByPersonId(id=id, thumbSize=thumbSize).Thumbnail
        except: pass

        return post

    def _addImages(self, posts, thumbSize='medium'):
        for post in posts:
            post = self._addImage(post, thumbSize)
            yield post
