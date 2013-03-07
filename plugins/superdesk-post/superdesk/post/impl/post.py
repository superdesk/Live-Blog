'''
Created on May 3, 2012

@package: superdesk posts
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Contains the SQL alchemy implementation for post API.
'''

from ..api.post import IPostService
from ..meta.post import PostMapped
from ..meta.type import PostTypeMapped
from ally.api.extension import IterPart
from ally.container import wire
from ally.container.ioc import injected
from ally.container.support import setup
from ally.exception import InputError, Ref
from ally.internationalization import _
from ally.support.api.util_service import copy
from ally.support.sqlalchemy.util_service import buildQuery, buildLimits
from sql_alchemy.impl.entity import EntityGetServiceAlchemy
from sqlalchemy.orm.exc import NoResultFound
from superdesk.collaborator.meta.collaborator import CollaboratorMapped
from superdesk.post.api.post import Post, QPostUnpublished, QPost
from superdesk.source.meta.source import SourceMapped
from sqlalchemy.sql.functions import current_timestamp

# --------------------------------------------------------------------

COPY_EXCLUDE = ('Type', 'IsModified', 'IsPublished', 'AuthorName')

@injected
@setup(IPostService, name='postService')
class PostServiceAlchemy(EntityGetServiceAlchemy, IPostService):
    '''
    Implementation for @see: IPostService
    '''
    default_source_name = 'internal'; wire.config('default_source_name', doc='''
    The default source name used when a source was not supplied''')

    def __init__(self):
        '''
        Construct the post service.
        '''
        EntityGetServiceAlchemy.__init__(self, PostMapped)

    def getUnpublished(self, creatorId=None, authorId=None, offset=None, limit=None, detailed=False, q=None):
        '''
        @see: IPostService.getUnpublished
        '''
        assert q is None or isinstance(q, QPostUnpublished), 'Invalid query %s' % q
        sql = self._buildQuery(creatorId, authorId, q)
        sql = sql.filter(PostMapped.PublishedOn == None)

        sqlLimit = buildLimits(sql, offset, limit)
        if detailed: return IterPart(sqlLimit.all(), sql.count(), offset, limit)
        return sqlLimit.all()

    def getPublished(self, creatorId=None, authorId=None, offset=None, limit=None, detailed=False, q=None):
        '''
        @see: IPostService.getPublished
        '''
        assert q is None or isinstance(q, QPost), 'Invalid query %s' % q
        sql = self._buildQuery(creatorId, authorId, q)
        sql = sql.filter(PostMapped.PublishedOn != None)

        sqlLimit = buildLimits(sql, offset, limit)
        if detailed: return IterPart(sqlLimit.all(), sql.count(), offset, limit)
        return sqlLimit.all()

    def getAll(self, creatorId=None, authorId=None, offset=None, limit=None, detailed=False, q=None):
        '''
        @see: IPostService.getPublished
        '''
        assert q is None or isinstance(q, QPost), 'Invalid query %s' % q
        sql = self._buildQuery(creatorId, authorId, q)
        sqlLimit = buildLimits(sql, offset, limit)
        if detailed: return IterPart(sqlLimit.all(), sql.count(), offset, limit)
        return sqlLimit.all()

    def insert(self, post):
        '''
        @see: IPostService.insert
        '''
        assert isinstance(post, Post), 'Invalid post %s' % post
        postDb = PostMapped()
        copy(post, postDb, exclude=COPY_EXCLUDE)
        postDb.typeId = self._typeId(post.Type)

        # TODO: implement the proper fix using SQLAlchemy compilation rules
        nohigh = { i: None for i in range(0x10000, 0x110000) }
        if postDb.Meta: postDb.Meta = postDb.Meta.translate(nohigh)
        if postDb.Content: postDb.Content = postDb.Content.translate(nohigh)
        if postDb.ContentPlain: postDb.ContentPlain = postDb.ContentPlain.translate(nohigh)

        if post.CreatedOn is None: postDb.CreatedOn = current_timestamp()
        if not postDb.Author:
            colls = self.session().query(CollaboratorMapped).filter(CollaboratorMapped.User == postDb.Creator).all()
            if not colls:
                coll = CollaboratorMapped()
                coll.User = postDb.Creator
                src = self.session().query(SourceMapped).filter(SourceMapped.Name == PostServiceAlchemy.default_source_name).one()
                coll.Source = src.Id
                self.session().add(coll)
                self.session().flush((coll,))
                colls = (coll,)
            postDb.Author = colls[0].Id

        self.session().add(postDb)
        self.session().flush((postDb,))
        post.Id = postDb.Id
        return post.Id

    def update(self, post):
        '''
        @see: IPostService.update
        '''
        assert isinstance(post, Post), 'Invalid post %s' % post
        postDb = self.session().query(PostMapped).get(post.Id)
        if not postDb or postDb.DeletedOn is not None: raise InputError(Ref(_('Unknown post id'), ref=Post.Id))

        if Post.Type in post: postDb.typeId = self._typeId(post.Type)
        if post.UpdatedOn is None: postDb.UpdatedOn = current_timestamp()

        self.session().flush((copy(post, postDb, exclude=COPY_EXCLUDE),))

    def delete(self, id):
        '''
        @see: IPostService.delete
        '''
        postDb = self.session().query(PostMapped).get(id)
        if not postDb or postDb.DeletedOn is not None: return False

        postDb.DeletedOn = current_timestamp()
        self.session().flush((postDb,))
        return True

    # ----------------------------------------------------------------

    def _buildQuery(self, creatorId=None, authorId=None, q=None):
        '''
        Builds the general query for posts.
        '''
        sql = self.session().query(PostMapped)
        if creatorId: sql = sql.filter(PostMapped.Creator == creatorId)
        if authorId: sql = sql.filter(PostMapped.Author == authorId)
        addDeleted = False
        if q:
            sql = buildQuery(sql, q, PostMapped)
            addDeleted = QPostUnpublished.deletedOn in q
        if not addDeleted: sql = sql.filter(PostMapped.DeletedOn == None)
        return sql

    def _typeId(self, key):
        '''
        Provides the post type id that has the provided key.
        '''
        try:
            sql = self.session().query(PostTypeMapped.id).filter(PostTypeMapped.Key == key)
            return sql.one()[0]
        except NoResultFound:
            raise InputError(Ref(_('Invalid post type %(type)s') % dict(type=key), ref=Post.Type))
