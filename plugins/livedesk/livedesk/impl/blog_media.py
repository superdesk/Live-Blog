'''
Created on May 12, 2013

@package: livedesk
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Martin Saturka

Contains the SQL alchemy meta for livedesk blog media API.
'''

from livedesk.api.blog_media import BlogMedia, IBlogMediaService, IBlogMediaTypeService
from livedesk.meta.blog_media import BlogMediaMapped, BlogMediaTypeMapped
from sql_alchemy.impl.entity import EntityServiceAlchemy, \
    EntityGetServiceAlchemy, EntityFindServiceAlchemy
from ally.internationalization import _
from ally.container.ioc import injected
from ally.container.support import setup
from sqlalchemy import func
from ally.api.error import InputError
from sql_alchemy.support.util_service import iterateCollection
from ally.api.validate import validate

# --------------------------------------------------------------------

@injected
@setup(IBlogMediaTypeService, name='blogMediaTypeService')
@validate(BlogMediaTypeMapped)
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
@validate(BlogMediaMapped)
class BlogMediaServiceAlchemy(EntityServiceAlchemy, IBlogMediaService):
    '''
    Implementation for @see: IBlogMediaService
    '''

    def __init__(self):
        '''
        Construct the blog media service.
        '''
        EntityServiceAlchemy.__init__(self, BlogMediaMapped)

    def getAll(self, blogId, typeKey=None, **options):
        '''
        @see: IBlogMediaService.getAll
        '''
        sql = self.session().query(BlogMediaMapped.Id)
        sql = sql.filter(BlogMediaMapped.Blog == blogId)
        if typeKey:
            sql = sql.join(BlogMediaTypeMapped).filter(BlogMediaMapped.Type == typeKey)
        sql = sql.order_by(BlogMediaMapped.Id)
        return iterateCollection(sql, **options)

    def insert(self, media:BlogMedia):
        '''
        @see: IBlogMediaService.insert
        '''
        assert isinstance(media, BlogMedia), 'Invalid blog media %s' % media
        if (not BlogMedia.Rank in media) or (media.Rank < 1):
            media.Rank = self._nextRank(0, media.Blog, media.typeId)
        return super().insert(media)

    def update(self, media:BlogMedia):
        '''
        @see: IBlogMediaService.update
        '''
        assert isinstance(media, BlogMedia), 'Invalid blog media %s' % media
        if (BlogMedia.Rank in media) and (media.Rank < 1):
            media.Rank = self._nextRank(media.Id, media.Blog, media.Type)
        super().update(media)

    def exchange(self, firstId, secondId):
        '''
        @see: IBlogMediaService.exchange
        '''
        firstMedia = self.session().query(BlogMediaMapped).get(firstId)
        if not firstMedia: raise InputError(_('Unknown blog media id'), BlogMedia.Id)
        assert isinstance(firstMedia, BlogMediaMapped), 'Invalid blog media %s' % firstMedia

        secondMedia = self.session().query(BlogMediaMapped).get(secondId)
        if not secondMedia: raise InputError(_('Unknown blog media id'), BlogMedia.Id)
        assert isinstance(secondMedia, BlogMediaMapped), 'Invalid blog media %s' % secondMedia

        if firstMedia.Blog != secondMedia.Blog:
            raise InputError(_('Blog media have to be of the same blog'),)
        if firstMedia.Type != secondMedia.Type:
            raise InputError(_('Blog media have to be of the same type'),)

        firstRank, secondRank = secondMedia.Rank, firstMedia.Rank

        firstMedia.Rank = 0
        self.session().flush((firstMedia,))

        firstMedia.Rank, secondMedia.Rank = firstRank, secondRank
        self.session().flush((secondMedia,))
        self.session().flush((firstMedia,))

    # ----------------------------------------------------------------

    def _nextRank(self, entryId, blogId, typeId):
        sql = self.session().query(func.max(BlogMediaMapped.Rank)).filter(BlogMediaMapped.Id != entryId)
        sql = sql.filter(BlogMediaMapped.Blog == blogId).filter(BlogMediaMapped.Type == typeId).one()
        maxRank, = sql.one()
        if not maxRank: maxRank = 0
        return maxRank + 1
