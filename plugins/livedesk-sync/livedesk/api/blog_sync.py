'''
Created on April 26, 2013

@package: livedesk
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mugur Rus

API specifications for liveblog sync.
'''

from ally.support.api.entity import Entity, IEntityService, QEntity
from livedesk.api.blog import Blog
from datetime import datetime
from livedesk.api.domain_livedesk import modelLiveDesk
from ally.api.config import query, service, LIMIT_DEFAULT, call, UPDATE
from ally.api.criteria import AsRangeOrdered, AsDateTimeOrdered, AsBoolean
from superdesk.source.api.source import Source
from ally.api.type import Iter
from superdesk.source.api.type import SourceType

# --------------------------------------------------------------------

@modelLiveDesk(name='Sync')
class BlogSync(Entity):
    '''
    Provides the blog sync model. It is used for all kind of blog sync, currently chainde blog and SMS
    '''
    Blog = Blog
    Source = Source
    CId = int
    LastActivity = datetime
    Auto = bool

# --------------------------------------------------------------------

@query(BlogSync)
class QBlogSync(QEntity):
    '''
    Provides the query for BlogSync.
    '''
    cId = AsRangeOrdered
    lastActivity = AsDateTimeOrdered
    auto = AsBoolean

# --------------------------------------------------------------------

@service((Entity, BlogSync), (QEntity, QBlogSync))
class IBlogSyncService(IEntityService):
    '''
    Provides the service methods for the blog sync.
    '''
    
    @call(webName="checkTimeout", method=UPDATE)
    def checkTimeout(self, blogSyncId:BlogSync.Id, timeout:int) -> bool:
        '''
        Returns true if the last activity is older than timeout and if it is older update the last activity value
        '''
    
    @call
    def getBySourceType(self, sourceType:SourceType.Key, offset:int=None, limit:int=LIMIT_DEFAULT, detailed:bool=True, q:QBlogSync=None) -> Iter(BlogSync):
        '''
        Returns the list of blog sync models for source type.

        @param sourceType: SourceType.Key
            The source(provider) identifier    
        @param offset: integer
            The offset to retrieve the entities from.
        @param limit: integer
            The limit of entities to retrieve.
        @param detailed: boolean
            If true will present the total count, limit and offset for the partially returned collection.
        @param q: QBlogSync
            The query to search by.
        '''
        
    @call
    def getByBlog(self, blogId:Blog.Id, offset:int=None, limit:int=LIMIT_DEFAULT, detailed:bool=True, q:QBlogSync=None) -> Iter(BlogSync):
        '''
        Returns the list of blog sync models for blog.

        @param blogId: Blog.Id
            The blog id  
        @param offset: integer
            The offset to retrieve the entities from.
        @param limit: integer
            The limit of entities to retrieve.
        @param detailed: boolean
            If true will present the total count, limit and offset for the partially returned collection.
        @param q: QBlogSync
            The query to search by.
        '''    