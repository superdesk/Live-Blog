'''
Created on May 4, 2012

@package: livedesk
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Contains the SQL alchemy meta for blog API.
'''

import logging
from sqlalchemy.exc import SQLAlchemyError, OperationalError
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.sql.expression import exists, or_
from sqlalchemy.sql.functions import current_timestamp

from ally.api.criteria import AsBoolean
from ally.api.error import InputError
from ally.container import wire
from ally.container.ioc import injected
from ally.container.support import setup
from ally.internationalization import _
from livedesk.meta.blog import BlogSourceDB
from livedesk.meta.blog_collaborator import BlogCollaboratorMapped, \
    BlogCollaboratorTypeMapped
from sql_alchemy.impl.entity import EntityCRUDServiceAlchemy
from sql_alchemy.support.util_service import buildQuery, iterateCollection
from superdesk.collaborator.meta.collaborator import CollaboratorMapped
from superdesk.post.api.post import QPostWithPublished
from superdesk.post.meta.post import PostMapped
from superdesk.source.api.source import ISourceService, Source, QSource
from superdesk.source.meta.source import SourceMapped
from superdesk.source.meta.type import SourceTypeMapped
from support.core.impl.configuration import ConfigurationServiceAlchemy
from ..api.blog import IBlogService, QBlog, Blog, IBlogSourceService, \
    IBlogConfigurationService
from ..meta.blog import BlogMapped, BlogConfigurationMapped
from ally.api.validate import validate

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

@injected
@setup(IBlogService, name='blogService')
@validate(BlogMapped)
class BlogServiceAlchemy(EntityCRUDServiceAlchemy, IBlogService):
    '''
    Implementation for @see: IBlogService
    '''
    admin_types = ['Administrator']; wire.config('admin_types', doc='''
    The collaborator type(s) name associated with the administrator filter.
    ''')
    collaborator_types = ['Administrator', 'Collaborator']; wire.config('collaborator_types', doc='''
    The collaborator type(s) name associated with the collaborator filter.
    ''')

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
        except NoResultFound: raise InputError(_('Unknown id'), ref=Blog.Id)

    def getAll(self, languageId=None, userId=None, q=None, **options):
        '''
        @see: IBlogService.getAll
        '''
        return iterateCollection(self._buildQuery(languageId, userId, q), **options)

    def getLive(self, languageId=None, userId=None, q=None, **options):
        '''
        @see: IBlogService.getLive
        '''
        sql = self._buildQuery(languageId, userId, q)
        sql = sql.filter((BlogMapped.ClosedOn == None) & (BlogMapped.LiveOn != None))
        return iterateCollection(sql, **options)

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

    def isBlogAdmin(self, userId, blogId):
        '''
        @see: IBlogService.isBlogAdmin
        '''
        return self._isUserAllowed(userId, blogId, self.admin_types)

    def isBlogCollaborator(self, userId, blogId):
        '''
        @see: IBlogService.isBlogCollaborator
        '''
        return self._isUserAllowed(userId, blogId, self.collaborator_types)

    def isBlogOpen(self, userId, blogId):
        '''
        @see: IBlogService.isBlogOpen
        '''
        sql = self.session().query(BlogMapped.Id)
        sql = sql.filter(BlogMapped.Id == blogId).filter(BlogMapped.ClosedOn == None)
        return sql.count() > 0

    # ----------------------------------------------------------------

    def _isUserAllowed(self, userId, blogId, collaboratorTypes):
        '''
        Return true if the user has access to the given blog and his collaborator type
        is in the list of allowed collaborator types.
        '''
        sql = self.session().query(BlogMapped.Id)
        sql = sql.filter(BlogMapped.Id == blogId)
        sql = sql.filter(BlogMapped.Creator == userId)
        if sql.count() > 0: return True

        sql = self.session().query(BlogCollaboratorMapped.Id)
        sql = sql.join(BlogCollaboratorTypeMapped)
        sql = sql.filter(BlogCollaboratorMapped.Blog == blogId)
        sql = sql.filter((BlogCollaboratorMapped.User == userId) & BlogCollaboratorTypeMapped.Name.in_(collaboratorTypes))
        return sql.count() > 0

    def _buildQuery(self, languageId=None, userId=None, q=None):
        '''
        Builds the general query for blogs.
        '''
        sql = self.session().query(BlogMapped.Id)
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
@validate(SourceMapped)
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
            raise InputError(_('Unknown source'),)
        sql = self.session().query(BlogSourceDB)
        sql = sql.filter(BlogSourceDB.blog == blogId).filter(BlogSourceDB.source == sourceId)
        return source

    def getSources(self, blogId, **options):
        '''
        @see: IBlogSourceService.getSources
        '''
        sql = self.session().query(SourceMapped)
        sql = sql.join(BlogSourceDB, SourceMapped.Id == BlogSourceDB.source)
        sql = sql.join(BlogMapped, BlogMapped.Id == BlogSourceDB.blog).filter(BlogMapped.Id == blogId)

        sql_prov = self.session().query(SourceMapped.URI)
        sql_prov = sql_prov.join(SourceTypeMapped)
        sql_prov = sql_prov.filter(SourceTypeMapped.Key == self.blog_provider_type)

        sql = sql.filter(or_(SourceMapped.OriginURI == None, SourceMapped.OriginURI.in_(sql_prov)))
        return iterateCollection(sql, **options)

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
            raise InputError(_('Cannot add blog-source link.'),)
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
                sourceTypeKey, = self.session().query(SourceTypeMapped.Key).join(SourceMapped).filter(SourceMapped.Id == sourceId).one()
                if sourceTypeKey in self.sources_auto_delete:
                    try:
                        self.sourceService.delete(sourceId)
                    except InputError: pass
            return res
        except OperationalError:
            assert log.debug('Could not delete blog source with blog id \'%s\' and source id \'%s\'', blogId, sourceId, exc_info=True) or True
            raise InputError(_('Cannot delete because is in use'),)

    def getChainedPosts(self, blogId, sourceTypeKey, q=None, **options):
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
        return iterateCollection(sql, **options)

# --------------------------------------------------------------------

@setup(IBlogConfigurationService, name='blogConfigurationService')
@validate(BlogConfigurationMapped)
class BlogConfigurationServiceAlchemy(ConfigurationServiceAlchemy, IBlogConfigurationService):
    '''
    Implementation for @see: IBlogConfigurationService

    This implementation is automatically generated.
    See the configuration modules of the support package.
    '''

    def __init__(self):
        ConfigurationServiceAlchemy.__init__(self, BlogConfigurationMapped)
