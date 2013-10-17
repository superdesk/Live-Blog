'''
Created on August 12, 2013

@package: livedesk
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Martin Saturka

API specifications for livedesk blog media.
'''

from ally.api.config import service, call, UPDATE
from ally.api.type import Iter
from livedesk.api.blog import Blog
from superdesk.media_archive.api.meta_info import MetaInfo
from livedesk.api.domain_livedesk import modelLiveDesk
from ally.support.api.entity_ided import Entity, IEntityService
from ally.api.option import SliceAndTotal # @UnusedImport
from ally.support.api.entity import IEntityGetPrototype, IEntityFindPrototype

# --------------------------------------------------------------------

@modelLiveDesk(id='Key')
class BlogMediaType:
    '''
    Provides the blog media type model.
    '''
    Key = str

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

@service(('Entity', BlogMediaType),)
class IBlogMediaTypeService(IEntityGetPrototype, IEntityFindPrototype):
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
    def getAll(self, blogId:Blog.Id, typeKey:BlogMediaType.Key=None, **options:SliceAndTotal) -> Iter(BlogMedia.Id):
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
