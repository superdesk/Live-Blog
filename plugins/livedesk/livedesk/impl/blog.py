'''
Created on May 4, 2012

@package: livedesk
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Contains the SQL alchemy meta for blog API.
'''

from ..api.blog import IBlogService, QBlog, Blog, IBlogSourceService
from ..meta.blog import BlogMapped
from ally.api.extension import IterPart
from ally.container.ioc import injected
from ally.container.support import setup
from ally.exception import InputError, Ref
from ally.internationalization import _
from ally.support.sqlalchemy.util_service import buildQuery, buildLimits
from livedesk.meta.blog_collaborator import BlogCollaboratorMapped
from sql_alchemy.impl.entity import EntityCRUDServiceAlchemy
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.sql.expression import exists
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
        EntityCRUDServiceAlchemy.__init__(self, BlogMapped, QBlog)

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
    sources_auto_delete = ['chained blog',]; wire.config('sources_auto_delete', doc='''
    List of source types for sources that should be deleted under deleting all of their usage''')

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
        return sql.join(BlogSourceDB, SourceMapped.Id == BlogSourceDB.source).filter(BlogMapped.Id == blogId).all()

    def addSource(self, blogId, source):
        '''
        @see: IBlogSourceService.addSource
        NB: The source must have the correct type set in.
            This way, we can reuse it for other purposes, apart from the chained blogs.
        '''
        assert isinstance(blogId, int), 'Invalid blog identifier %s' % blogId
        assert isinstance(source, Source), 'Invalid source %s' % source

        q = QSource()
        q.name = source.Name
        sources = self.sourceService.getAll(typeKey=source.Type, offset=0, limit=1, detailed=False, q=q)
        if sources:
            sourceId = sources[0].Id
        else:
            sourceId = self.sourceService.insert(source)
        ent = BlogSourceDB()
        ent.blog = blogId
        ent.source = sourceId
        try:
            self.session().add(ent)
            self.session().flush((ent,))
        except SQLAlchemyError as e:
            raise InputError(Ref(_('Cannot persist BlogSource'),))
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
                    self.sourceService.delete(sourceId)
            return res
        except OperationalError:
            assert log.debug('Could not delete blog source with blog id \'%s\' and source id \'%s\'', blogId, sourceId, exc_info=True) or True
            raise InputError(Ref(_('Cannot delete because is in use'),))

