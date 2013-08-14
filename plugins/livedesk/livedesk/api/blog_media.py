'''
Created on August 12, 2013

@package: livedesk
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Martin Saturka

API specifications for livedesk blog media.
'''

from ally.api.config import service, call, UPDATE, LIMIT_DEFAULT
from ally.api.type import Iter
from livedesk.api.blog import Blog
from superdesk.media_archive.api.meta_info import MetaInfo
from ally.support.api.entity import Entity, IEntityService
from ally.support.api.keyed import Entity as EntityKeyed, IEntityGetService, IEntityFindService
from livedesk.api.domain_livedesk import modelLiveDesk

# --------------------------------------------------------------------

@modelLiveDesk
class BlogMediaType(EntityKeyed):
    '''
    Provides the blog media type model.
    '''

# --------------------------------------------------------------------

@modelLiveDesk
class BlogMedia(Entity):
    '''
    Provides the blog media model.
    '''
    Blog = Blog
    MetaInfo = MetaInfo
    Type = BlogMediaType
    Rank = int

# --------------------------------------------------------------------

# No queries

# --------------------------------------------------------------------

@service((Entity, BlogMediaType),)
class IBlogMediaTypeService(IEntityGetService, IEntityFindService):
    '''
    Provides the service methods for the blog media types.
    '''

# --------------------------------------------------------------------

@service((Entity, BlogMedia),)
class IBlogMediaService(IEntityService):
    '''
    Provides the service methods for the blog media.
    '''

    @call
    def getAll(self, blogId:Blog.Id, typeKey:BlogMediaType.Key=None, offset:int=None, limit:int=LIMIT_DEFAULT, detailed:bool=True) -> Iter(BlogMedia):
        '''
        Provides all blogs media.
        '''

    @call
    def insert(self, media:BlogMedia) -> BlogMedia.Id:
        '''
        Inserts blog media.
        '''

    @call
    def update(self, media:BlogMedia):
        '''
        Updates blog media.
        '''

    @call(method=UPDATE, webName='Exchange')
    def exchange(self, firstId:BlogMedia.Id, secondId:BlogMedia.Id):
        '''
        Exchanges ranks, i.e. reorders, the media.
        '''
