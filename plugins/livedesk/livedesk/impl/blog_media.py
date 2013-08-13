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

    def getAll(self, blogId, typeId=None, offset=None, limit=None, detailed=True):
        '''
        @see: IBlogMediaService.getAll
        '''
        return ()

    def exchange(self, firstId, secondId):
        '''
        @see: IBlogMediaService.exchange
        '''
        return
