'''
Created on May 12, 2013

@package: livedesk
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Martin Saturka

Contains the SQL alchemy meta for livedesk blog media API.
'''

from livedesk.api.blog_media import BlogMedia, BlogMediaType, IBlogMediaService, IBlogMediaTypeService
from livedesk.meta.blog_media import BlogMediaMapped, BlogMediaTypeMapped
from sql_alchemy.impl.entity import EntityServiceAlchemy
from sql_alchemy.impl.keyed import EntityGetServiceAlchemy, EntityFindServiceAlchemy
from ally.exception import InputError, Ref
from ally.internationalization import _
from ally.support.sqlalchemy.util_service import buildLimits, handle
from ally.support.api.util_service import copy
from ally.api.extension import IterPart
from ally.container.ioc import injected
from ally.container.support import setup
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import func

# --------------------------------------------------------------------

@injected
@setup(IBlogMediaTypeService, name='blogMediaTypeService')
class BlogMediaTypeServiceAlchemy(EntityGetServiceAlchemy, EntityFindServiceAlchemy, IBlogMediaTypeService):
    '''
    Implementation for @see: IBlogMediaTypeService
    '''

    def __init__(self):
        '''
        Construct the blog media type service.
        '''
        EntityGetServiceAlchemy.__init__(self, BlogMediaTypeMapped)

# --------------------------------------------------------------------

@injected
@setup(IBlogMediaService, name='blogMediaService')
class BlogMediaServiceAlchemy(EntityServiceAlchemy, IBlogMediaService):
    '''
    Implementation for @see: IBlogMediaService
    '''

    def __init__(self):
        '''
        Construct the blog media service.
        '''
        EntityServiceAlchemy.__init__(self, BlogMediaMapped)

    def getAll(self, blogId, typeKey=None, offset=None, limit=None, detailed=False):
        '''
        @see: IBlogMediaService.getAll
        '''
        sql = self.session().query(BlogMediaMapped)
        sql = sql.filter(BlogMediaMapped.Blog == blogId)
        if typeKey:
            sql = sql.join(BlogMediaTypeMapped).filter(BlogMediaMapped.Key == typeKey)
        sql = sql.order_by(BlogMediaMapped.Id)

        sqlLimit = buildLimits(sql, offset, limit)
        if detailed: return IterPart(sqlLimit.all(), sql.count(), offset, limit)
        return sqlLimit.all()

    def insert(self, media:BlogMedia):
        '''
        @see: IBlogMediaService.insert
        '''
        assert isinstance(media, BlogMedia), 'Invalid blog media %s' % media
        mediaDb = BlogMediaMapped()
        copy(media, mediaDb, exclude=('Type',))
        mediaDb.typeId = self._typeId(media.Type)

        if (not BlogMedia.Rank in media) or (media.Rank < 1):
            mediaDb.Rank = self._nextRank(0, mediaDb.Blog, mediaDb.typeId)

        try:
            self.session().add(mediaDb)
            self.session().flush((mediaDb,))
        except SQLAlchemyError as e: handle(e, mediaDb)

        media.Id = mediaDb.Id
        return media.Id

    def update(self, media:BlogMedia):
        '''
        @see: IBlogMediaService.update
        '''
        assert isinstance(media, BlogMedia), 'Invalid blog media %s' % media
        mediaDb = self.session().query(BlogMediaMapped).get(media.Id)
        if not mediaDb: raise InputError(Ref(_('Unknown blog media id'), ref=BlogMedia.Id))

        copy(media, mediaDb, exclude=('Type',))
        if BlogMedia.Type in media: mediaDb.typeId = self._typeId(media.Type)

        if (BlogMedia.Rank in media) and (media.Rank < 1):
            mediaDb.Rank = self._nextRank(mediaDb.Id, mediaDb.Blog, mediaDb.typeId)
    
        try:
            self.session().flush((mediaDb,))
        except SQLAlchemyError as e: handle(e, mediaDb)

    def exchange(self, firstId, secondId):
        '''
        @see: IBlogMediaService.exchange
        '''
        firstMedia = self.session().query(BlogMediaMapped).get(firstId)
        if not firstMedia: raise InputError(Ref(_('Unknown blog media id'), ref=BlogMedia.Id))
        assert isinstance(firstMedia, BlogMediaMapped), 'Invalid blog media %s' % firstMedia

        secondMedia = self.session().query(BlogMediaMapped).get(secondId)
        if not secondMedia: raise InputError(Ref(_('Unknown blog media id'), ref=BlogMedia.Id))
        assert isinstance(secondMedia, BlogMediaMapped), 'Invalid blog media %s' % secondMedia

        if firstMedia.Blog != secondMedia.Blog:
            raise InputError(Ref(_('Blog media have to be of the same blog'),))

        if firstMedia.Type != secondMedia.Type:
            raise InputError(Ref(_('Blog media have to be of the same type'),))

        firstRank, secondRank = secondMedia.Rank, firstMedia.Rank

        try:
            firstMedia.Rank = 0
            self.session().flush((firstMedia,))

            firstMedia.Rank, secondMedia.Rank = firstRank, secondRank
            self.session().flush((secondMedia,))
            self.session().flush((firstMedia,))
        except SQLAlchemyError as e: handle(e, mediaDb)

    # ----------------------------------------------------------------

    def _typeId(self, key):
        '''
        Provides the blog media type id that has the provided key.
        '''
        try:
            sql = self.session().query(BlogMediaTypeMapped.id).filter(BlogMediaTypeMapped.Key == key)
            return sql.one()[0]
        except NoResultFound:
            raise InputError(Ref(_('Invalid blog media type %(type)s') % dict(type=key), ref=BlogMedia.Type))

    def _nextRank(self, entryId, blogId, typeId):
        maxRank, = self.session().query(func.max(BlogMediaMapped.Rank)).filter(BlogMediaMapped.Id != entryId).filter(BlogMediaMapped.Blog == blogId).filter(BlogMediaMapped.typeId == typeId).one()
        if not maxRank: maxRank = 0
        return maxRank + 1
