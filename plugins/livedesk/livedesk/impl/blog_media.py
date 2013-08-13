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
from ally.support.sqlalchemy.util_service import buildLimits
from ally.api.extension import IterPart
from ally.container.ioc import injected
from ally.container.support import setup

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

        sqlLimit = buildLimits(sql, offset, limit)
        if detailed: return IterPart(sqlLimit.all(), sql.count(), offset, limit)
        return sqlLimit.all()

    # TODO: the type_based insert/update methods

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

        if firstMedia.MetaInfo != secondMedia.MetaInfo:
            raise InputError(Ref(_('Blog media have to be of the same type'),))

        firstMedia.Rank, secondMedia.Rank = secondMedia.Rank, firstMedia.Rank

        self.session().flush((firstMedia, secondMedia))
