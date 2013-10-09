'''
Created on May 3, 2012

@package: superdesk posts
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Contains the SQL alchemy implementation for post API.
'''

from ..api.post import IPostService, QWithCId
from ..meta.post import PostMapped
from ally.api.criteria import AsRange
from ally.container import wire
from ally.container.ioc import injected
from ally.container.support import setup
from sql_alchemy.impl.entity import EntityGetServiceAlchemy
from sqlalchemy.orm.exc import NoResultFound
from superdesk.collaborator.meta.collaborator import CollaboratorMapped
from superdesk.post.api.post import Post, QPostUnpublished, QPost, QPostPublished
from superdesk.source.meta.source import SourceMapped
from sqlalchemy.sql.functions import current_timestamp
from sql_alchemy.support.util_service import iterateCollection, buildQuery, \
    insertModel, updateModel
from ally.api.error import IdError, InputError

# --------------------------------------------------------------------

COPY_EXCLUDE = ('Type', 'IsModified', 'IsPublished', 'AuthorName')

@injected
@setup(IPostService, name='postService')
class PostServiceAlchemy(EntityGetServiceAlchemy, IPostService):
    '''Implementation for @see: IPostService'''
    default_source_name = 'internal'; wire.config('default_source_name', doc='''
    The default source name used when a source was not supplied''')

    meta_max_size = 65535; wire.config('meta_max_size', doc='''
    The maximal size for the meta part of a post; limited only by db system if zero.''')
    content_max_size = 65535; wire.config('content_max_size', doc='''
    The maximal size for the content part of a post; limited only by db system if zero.''')
    content_plain_max_size = 65535; wire.config('content_plain_max_size', doc='''
    The maximal size for the content plain part of a post; limited only by db system if zero.''')

    def __init__(self):
        '''
        Construct the post service.
        '''
        EntityGetServiceAlchemy.__init__(self, PostMapped)

    def getUnpublished(self, creatorId=None, authorId=None, q=None, **options):
        '''
        @see: IPostService.getUnpublished
        '''
        assert q is None or isinstance(q, QPostUnpublished), 'Invalid query %s' % q
        sql = self._buildQuery(creatorId, authorId, q)
        sql = sql.filter(PostMapped.PublishedOn == None)
        return iterateCollection(sql, **options)

    def getPublished(self, creatorId=None, authorId=None, q=None, **options):
        '''
        @see: IPostService.getPublished
        '''
        assert q is None or isinstance(q, QPost), 'Invalid query %s' % q
        sql = self._buildQuery(creatorId, authorId, q)
        sql = sql.filter(PostMapped.PublishedOn != None)
        return iterateCollection(sql, **options)

    def getAll(self, creatorId=None, authorId=None, q=None, **options):
        '''
        @see: IPostService.getPublished
        '''
        assert q is None or isinstance(q, QPost), 'Invalid query %s' % q
        sql = self._buildQuery(creatorId, authorId, q)
        return iterateCollection(sql, **options)

    def getUnpublishedBySource(self, sourceId, q=None, **options):
        '''
        @see: IPostService.getUnpublishedBySource
        '''
        assert q is None or isinstance(q, QPostUnpublished), 'Invalid query %s' % q
        sql = self._buildQueryBySource(sourceId).filter(PostMapped.PublishedOn == None)
        sql = self._buildQueryWithCId(q, sql)
        return iterateCollection(sql, **options)

    def getUnpublishedBySourceType(self, sourceTypeKey, q=None, **options):
        '''
        @see: IPostService.getUnpublishedBySourceType
        '''
        assert q is None or isinstance(q, QPostUnpublished), 'Invalid query %s' % q
        sql = self._buildQueryBySourceType(sourceTypeKey)
        sql = sql.filter(PostMapped.PublishedOn == None)
        sql = self._buildQueryWithCId(q, sql)
        return iterateCollection(sql, **options)

    def getPublishedBySource(self, sourceId, q=None, **options):
        '''
        @see: IPostService.getPublishedBySource
        '''
        assert q is None or isinstance(q, QPostPublished), 'Invalid query %s' % q
        sql = self._buildQueryBySource(sourceId)
        sql = sql.filter(PostMapped.PublishedOn != None)
        sql = self._buildQueryWithCId(q, sql)
        return iterateCollection(sql, **options)

    def getPublishedBySourceType(self, sourceTypeKey, q=None, **options):
        '''
        @see: IPostService.getPublishedBySourceType
        '''
        assert q is None or isinstance(q, QPostPublished), 'Invalid query %s' % q
        sql = self._buildQueryBySourceType(sourceTypeKey)
        sql = sql.filter(PostMapped.PublishedOn != None)
        sql = self._buildQueryWithCId(q, sql)
        return iterateCollection(sql, **options)

    def getAllBySource(self, sourceId, q=None, **options):
        '''
        @see: IPostService.getAllBySource
        '''
        assert q is None or isinstance(q, QPost), 'Invalid query %s' % q
        sql = self._buildQueryBySource(sourceId)
        sql = self._buildQueryWithCId(q, sql)
        return iterateCollection(sql, **options)

    def getAllBySourceType(self, sourceTypeKey, q=None, **options):
        '''
        @see: IPostService.getAllBySourceType
        '''
        assert q is None or isinstance(q, QPost), 'Invalid query %s' % q
        sql = self._buildQueryBySourceType(sourceTypeKey)
        sql = self._buildQueryWithCId(q, sql)
        return iterateCollection(sql, **options)

    def insert(self, post):
        '''
        @see: IPostService.insert
        '''
        assert isinstance(post, Post), 'Invalid post %s' % post
        post = self._adjustTexts(post)

        if post.CreatedOn is None: post.CreatedOn = current_timestamp()
        if not post.Author:
            try: coll = self.session().query(CollaboratorMapped).filter(CollaboratorMapped.User == post.Creator).one()
            except NoResultFound:
                coll = CollaboratorMapped()
                coll.User = post.Creator
                src = self.session().query(SourceMapped).filter(SourceMapped.Name == self.default_source_name).one()
                coll.Source = src.Id
                self.session().add(coll)
                self.session().flush((coll,))
            post.Author = coll.Id
        return insertModel(PostMapped, post).Id

    def update(self, post):
        '''
        @see: IPostService.update
        '''
        assert isinstance(post, Post), 'Invalid post %s' % post
        postDb = self.session().query(PostMapped).get(post.Id)
        if not postDb or postDb.DeletedOn is not None: raise IdError(Post.Id)

        if post.UpdatedOn is None: post.UpdatedOn = current_timestamp()
        post = self._adjustTexts(postDb)
        updateModel(post)

    def delete(self, id):
        '''
        @see: IPostService.delete
        '''
        postDb = self.session().query(PostMapped).get(id)
        if not postDb or postDb.DeletedOn is not None: return False
        postDb.DeletedOn = current_timestamp()
        updateModel(postDb)
        return True

    # ----------------------------------------------------------------

    def _buildQuery(self, creatorId=None, authorId=None, q=None):
        '''
        Builds the general query for posts.
        '''
        sql = self.session().query(PostMapped.Id)
        if creatorId: sql = sql.filter(PostMapped.Creator == creatorId)
        if authorId: sql = sql.filter(PostMapped.Author == authorId)
        addDeleted = False
        if q:
            sql = buildQuery(sql, q, PostMapped)
            addDeleted = QPostUnpublished.deletedOn in q
        if not addDeleted: sql = sql.filter(PostMapped.DeletedOn == None)
        return sql

    def _buildQueryBySource(self, sourceId):
        sql = self.session().query(PostMapped.Id)
        sql = sql.join(CollaboratorMapped, PostMapped.Author == CollaboratorMapped.Id)
        sql = sql.filter(CollaboratorMapped.Source == sourceId)
        return sql

    def _buildQueryBySourceType(self, sourceTypeKey):
        sql = self.session().query(PostMapped.Id)
        sql = sql.join(CollaboratorMapped, PostMapped.Author == CollaboratorMapped.Id)
        sql = sql.join(SourceMapped, CollaboratorMapped.Source == SourceMapped.Id)
        sql = sql.filter(SourceMapped.Type == sourceTypeKey)
        return sql

    def _buildQueryWithCId(self, q, sql):
        if q:
            if QWithCId.cId in q and q.cId:
                if AsRange.start in q.cId:
                    sql = sql.filter(PostMapped.Id >= q.cId.start)
                if AsRange.since in q.cId:
                    sql = sql.filter(PostMapped.Id > q.cId.since)
                if AsRange.end in q.cId:
                    sql = sql.filter(PostMapped.Id <= q.cId.end)
                if AsRange.until in q.cId:
                    sql = sql.filter(PostMapped.Id < q.cId.until)
            sql = buildQuery(sql, q, PostMapped)
        return sql

    def _adjustTexts(self, postDb):
        '''
        Corrects the Meta, Content, ContentPlain fields
        '''
        # TODO: implement the proper fix using SQLAlchemy compilation rules
        nohigh = { i: None for i in range(0x10000, 0x110000) }
        if postDb.Meta:
            postDb.Meta = postDb.Meta.translate(nohigh)
            if self.meta_max_size and (len(postDb.Meta) > self.meta_max_size):
                raise InputError(_('Too long Meta part')) # can not truncate json data
        if postDb.Content:
            postDb.Content = postDb.Content.translate(nohigh)
            if self.content_max_size and (len(postDb.Content) > self.content_max_size):
                raise InputError(_('Too long Content part')) # can not truncate structured data
        if postDb.ContentPlain:
            postDb.ContentPlain = postDb.ContentPlain.translate(nohigh)
            if self.content_plain_max_size: postDb.ContentPlain = postDb.ContentPlain[:self.content_plain_max_size]

        return postDb
