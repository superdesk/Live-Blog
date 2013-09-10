'''
Created on May 4, 2012

@package: livedesk
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Contains the SQL alchemy meta for blog API.
'''

from ..api.blog import IBlogService, QBlog, Blog, IBlogSourceService, IBlogConfigurationService
from ..meta.blog import BlogMapped, BlogConfigurationMapped
from support.impl.configuration import createConfigurationImpl
from ally.api.extension import IterPart
from ally.api.criteria import AsBoolean
from ally.container.ioc import injected
from ally.container.support import setup
from ally.exception import InputError, Ref
from ally.internationalization import _
from ally.support.sqlalchemy.util_service import buildQuery, buildLimits
from livedesk.meta.blog_collaborator import BlogCollaboratorMapped
from sql_alchemy.impl.entity import EntityCRUDServiceAlchemy
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.sql.expression import exists, or_
from sqlalchemy.sql.functions import current_timestamp
from superdesk.collaborator.meta.collaborator import CollaboratorMapped
from superdesk.source.api.source import Source, QSource
from superdesk.source.meta.source import SourceMapped
from superdesk.source.meta.type import SourceTypeMapped
from livedesk.meta.blog import BlogSourceDB
from sqlalchemy.exc import SQLAlchemyError, OperationalError
import logging
from superdesk.source.api.source import ISourceService
from ally.container import wire
from superdesk.post.api.post import QPostWithPublished
from superdesk.post.meta.post import PostMapped
from sqlalchemy.orm.util import aliased

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

@injected
@setup(IBlogService, name='blogService')
class BlogServiceAlchemy(EntityCRUDServiceAlchemy, IBlogService):
    '''
    Implementation for @see: IBlogService
    '''
    def __init__(self):
        '''
        Construct the blog service.
        '''
        EntityCRUDServiceAlchemy.__init__(self, BlogMapped)

    def getBlog(self, blogId):
        '''
        @see: IBlogService.getBlog
        '''
        sql = self.session().query(BlogMapped)
        sql = sql.filter(BlogMapped.Id == blogId)

        try: return sql.one()
        except NoResultFound: raise InputError(Ref(_('Unknown id'), ref=Blog.Id))

    def getAll(self, languageId=None, userId=None, offset=None, limit=None, detailed=False, q=None):
        '''
        @see: IBlogService.getAll
        '''
        sql = self._buildQuery(languageId, userId, q)
        sqlLimit = buildLimits(sql, offset, limit)
        if detailed: return IterPart(sqlLimit.all(), sql.count(), offset, limit)
        return sqlLimit.all()

    def getLive(self, languageId=None, userId=None, q=None):
        '''
        @see: IBlogService.getLive
        '''
        sql = self._buildQuery(languageId, userId, q)
        sql = sql.filter((BlogMapped.ClosedOn == None) & (BlogMapped.LiveOn != None))
        return sql.all()

    def putLive(self, blogId):
        '''
        @see: IBlogService.putLive
        '''
        blog = self.session().query(BlogMapped).get(blogId)
        if not blog: raise InputError(_('Invalid blog or credentials'))
        assert isinstance(blog, Blog), 'Invalid blog %s' % blog
        blog.LiveOn = current_timestamp() if blog.LiveOn is None else None
        self.session().merge(blog)


    def insert(self, blog):
        '''
        @see: IBlogService.insert
        '''
        assert isinstance(blog, Blog), 'Invalid blog %s' % blog
        if blog.CreatedOn is None: blog.CreatedOn = current_timestamp()
        return super().insert(blog)

    # ----------------------------------------------------------------

    def _buildQuery(self, languageId=None, userId=None, q=None):
        '''
        Builds the general query for blogs.
        '''
        sql = self.session().query(BlogMapped)
        if languageId: sql = sql.filter(BlogMapped.Language == languageId)
        if userId:
            userFilter = (BlogMapped.Creator == userId) | exists().where((CollaboratorMapped.User == userId) \
                                         & (BlogCollaboratorMapped.blogCollaboratorId == CollaboratorMapped.Id) \
                                         & (BlogCollaboratorMapped.Blog == BlogMapped.Id))
            sql = sql.filter(userFilter)

        if q:
            assert isinstance(q, QBlog), 'Invalid query %s' % q
            sql = buildQuery(sql, q, BlogMapped)

            if (QBlog.isOpen in q) and (AsBoolean.value in q.isOpen):
                if q.isOpen.value:
                    sql = sql.filter(BlogMapped.ClosedOn == None)
                else:
                    sql = sql.filter(BlogMapped.ClosedOn != None)

        return sql

# --------------------------------------------------------------------

@injected
@setup(IBlogSourceService, name='blogSourceService')
class BlogSourceServiceAlchemy(EntityCRUDServiceAlchemy, IBlogSourceService):
    '''
    Implementation for @see: IBlogSourceService
    '''
    sources_auto_delete = ['chained blog', ]; wire.config('sources_auto_delete', doc='''
    List of source types for sources that should be deleted under deleting all of their usage''')
    blog_provider_type = 'blog provider'; wire.config('blog_provider_type', doc='''
    Key of the source type for blog providers''')

    sourceService = ISourceService; wire.entity('sourceService')
    # The source service used to manage all operations on sources

    def __init__(self):
        '''
        Construct the blog source service.
        '''

    def getSource(self, blogId, sourceId):
        '''
        @see: IBlogSourceService.getSource
        '''
        source = self.session().query(SourceMapped).get(sourceId)
        if not source:
            raise InputError(Ref(_('Unknown source'),))
        sql = self.session().query(BlogSourceDB)
        sql = sql.filter(BlogSourceDB.blog == blogId).filter(BlogSourceDB.source == sourceId)
        return source

    def getSources(self, blogId):
        '''
        @see: IBlogSourceService.getSources
        '''
        sql = self.session().query(SourceMapped)
        sql = sql.join(BlogSourceDB, SourceMapped.Id == BlogSourceDB.source)
        sql = sql.join(BlogMapped, BlogMapped.Id == BlogSourceDB.blog).filter(BlogMapped.Id == blogId)

        sql_prov = self.session().query(SourceMapped.URI)
        sql_prov = sql_prov.join(SourceTypeMapped, SourceTypeMapped.id == SourceMapped.typeId)
        sql_prov = sql_prov.filter(SourceTypeMapped.Key == self.blog_provider_type)

        sql = sql.filter(or_(SourceMapped.OriginURI == None, SourceMapped.OriginURI.in_(sql_prov)))
        return sql.all()

    def addSource(self, blogId, source):
        '''
        @see: IBlogSourceService.addSource
        NB: The source must have the correct type set in.
            This way, we can reuse it for other purposes, apart from the chained blogs.
        '''
        assert isinstance(blogId, int), 'Invalid blog identifier %s' % blogId
        assert isinstance(source, Source), 'Invalid source %s' % source

        # insert source if it didn't exist yet
        q = QSource(name=source.Name, uri=source.URI)
        sources = self.sourceService.getAll(typeKey=source.Type, q=q)
        if not sources: sourceId = self.sourceService.insert(source)
        else:
            source.Id = sourceId = sources[0].Id
            self.sourceService.update(source)

        ent = BlogSourceDB()
        ent.blog = blogId
        ent.source = sourceId
        try:
            self.session().add(ent)
            self.session().flush((ent,))
        except SQLAlchemyError:
            raise InputError(Ref(_('Cannot add blog-source link.'),))
        return sourceId

    def deleteSource(self, blogId, sourceId):
        '''
        @see: IBlogSourceService.deleteSource
        '''
        assert isinstance(blogId, int), 'Invalid blog identifier %s' % blogId
        assert isinstance(sourceId, int), 'Invalid source identifier %s' % sourceId
        try:
            res = self.session().query(BlogSourceDB).filter(BlogSourceDB.blog == blogId).filter(BlogSourceDB.source == sourceId).delete() > 0
            if res:
                sourceTypeKey, = self.session().query(SourceTypeMapped.Key).join(SourceMapped, SourceTypeMapped.id == SourceMapped.typeId).filter(SourceMapped.Id == sourceId).one()
                if sourceTypeKey in self.sources_auto_delete:
                    try:
                        self.sourceService.delete(sourceId)
                    except InputError: pass
            return res
        except OperationalError:
            assert log.debug('Could not delete blog source with blog id \'%s\' and source id \'%s\'', blogId, sourceId, exc_info=True) or True
            raise InputError(Ref(_('Cannot delete because is in use'),))

    def getChainedPosts(self, blogId, sourceTypeKey, offset=None, limit=None, detailed=False, q=None):
        '''
        @see: IBlogSourceService.getChainedPosts
        '''
        sql = self.session().query(PostMapped)
        sql = sql.join(CollaboratorMapped).join(SourceMapped).join(SourceTypeMapped)
        sql = sql.filter(SourceTypeMapped.Key == sourceTypeKey)
        sql = sql.join(BlogSourceDB, SourceMapped.Id == BlogSourceDB.source).filter(BlogMapped.Id == blogId)

        if q:
            assert isinstance(q, QPostWithPublished), 'Invalid query %s' % q
            sql = buildQuery(sql, q, PostMapped)

            if q and QPostWithPublished.isPublished in q:
                if q.isPublished.value: sql = sql.filter(PostMapped.PublishedOn != None)
                else: sql = sql.filter(PostMapped.PublishedOn == None)

        sqlLimit = buildLimits(sql, offset, limit)
        if detailed: return IterPart(sqlLimit.all(), sql.count(), offset, limit)
        return sqlLimit.all()

# --------------------------------------------------------------------

BlogConfigurationServiceAlchemy = createConfigurationImpl(IBlogConfigurationService, BlogConfigurationMapped)
BlogConfigurationServiceAlchemy = setup(IBlogConfigurationService, name='blogConfigurationService')(BlogConfigurationServiceAlchemy)
BlogConfigurationServiceAlchemy = injected()(BlogConfigurationServiceAlchemy)
'''
Implementation for @see: IBlogConfigurationService

This implementation is automatically generated.
See the configuration modules of the support package.
'''
