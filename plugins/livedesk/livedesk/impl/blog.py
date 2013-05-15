'''
Created on May 4, 2012

@package: livedesk
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Contains the SQL alchemy meta for blog API.
'''

from ..api.blog import IBlogService, QBlog, Blog, BlogSource, IBlogSourceService
from ..meta.blog import BlogMapped
from ally.api.extension import IterPart
from ally.container.ioc import injected
from ally.container.support import setup
from ally.exception import InputError, Ref
from ally.internationalization import _
from ally.support.sqlalchemy.util_service import buildQuery, buildLimits, handle
from livedesk.meta.blog_collaborator import BlogCollaboratorMapped
from sql_alchemy.impl.entity import EntityCRUDServiceAlchemy
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.sql.expression import exists
from sqlalchemy.sql.functions import current_timestamp
from superdesk.collaborator.meta.collaborator import CollaboratorMapped
from superdesk.source.api.source import Source
from superdesk.source.meta.source import SourceMapped
from superdesk.source.meta.type import SourceTypeMapped
from livedesk.meta.blog import BlogSourceMapped
from sqlalchemy.exc import SQLAlchemyError, OperationalError
import logging
from superdesk.source.api.source import ISourceService
from ally.container import wire

SOURCES_AUTO_DELETE = ('chained blog',)

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
        return sql

# --------------------------------------------------------------------

@injected
@setup(IBlogSourceService, name='blogSourceService')
class BlogSourceServiceAlchemy(EntityCRUDServiceAlchemy, IBlogSourceService):
    '''
    Implementation for @see: IBlogSourceService
    '''

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
        sql = self.session().query(BlogSourceMapped)
        sql = sql.filter(BlogSourceMapped.Blog == blogId).filter(BlogSourceMapped.Source == sourceId)
        return source

    def getSources(self, blogId):
        '''
        @see: IBlogSourceService.getSources
        '''
        sql = self.session().query(SourceMapped)
        return sql.join(BlogSourceMapped, SourceMapped.Id == BlogSourceMapped.Source).filter(BlogMapped.Id == blogId).all()

    def addSource(self, blogId, source):
        '''
        @see: IBlogSourceService.addSource
        NB: The source must have the correct type set in.
            This way, we can reuse it for other purposes, apart from the chained blogs.
        '''
        assert isinstance(blogId, int), 'Invalid blog identifier %s' % blogId
        assert isinstance(source, Source), 'Invalid source %s' % source
        
        source.Type = self.blogLinkedSourceType
        sourceId = self.sourceService.insert(source)
        ent = BlogSourceMapped()
        ent.Blog = blogId
        ent.Source = sourceId
        try:
            self.session().add(ent)
            self.session().flush((ent,))
        except SQLAlchemyError as e: handle(e, ent)
        return sourceId

    def deleteSource(self, blogId, sourceId):
        '''
        @see: IBlogSourceService.deleteSource
        '''
        assert isinstance(blogId, int), 'Invalid blog identifier %s' % blogId
        assert isinstance(sourceId, int), 'Invalid source identifier %s' % sourceId
        try:
            res = self.session().query(BlogSourceMapped).filter(BlogSourceMapped.Blog == blogId).filter(BlogSourceMapped.Source == sourceId).delete() > 0
            if res:
                sourceType = self.session().query(SourceTypeMapped).join(SourceMapped, SourceTypeMapped.id == SourceMapped.typeId).filter(SourceMapped.Id == sourceId).one()
                if sourceType and (sourceType.Key in SOURCES_AUTO_DELETE):
                    if self.session().query(CollaboratorMapped).filter(CollaboratorMapped.Source == sourceId).count() == 0:
                        self.sourceService.delete(sourceId)
            return res
        except OperationalError:
            assert log.debug('Could not delete blog source with blog id \'%s\' and source id \'%s\'', blogId, sourceId, exc_info=True) or True
            raise InputError(Ref(_('Cannot delete because is in use'), model=BlogSource))

