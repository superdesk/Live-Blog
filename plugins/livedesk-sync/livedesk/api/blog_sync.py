'''
Created on April 26, 2013

@package: livedesk
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mugur Rus

API specifications for liveblog sync.
'''

from livedesk.api.blog import Blog
from datetime import datetime
from livedesk.api.domain_livedesk import modelLiveDesk
from ally.api.config import query, service, call
from ally.api.criteria import AsRangeOrdered, AsDateTimeOrdered, AsBoolean
from superdesk.source.api.source import Source
from ally.api.type import Iter
from superdesk.user.api.user import User
from ally.support.api.entity_ided import Entity, IEntityService, QEntity
from ally.api.option import SliceAndTotal # @UnusedImport

# --------------------------------------------------------------------

@modelLiveDesk(name='Sync')
class BlogSync(Entity):
    '''
    Provides the blog sync model.
    '''
    Blog = Blog
    Source = Source
    CId = int
    Start = datetime
    Auto = bool
    Creator = User

# --------------------------------------------------------------------

@query(BlogSync)
class QBlogSync(QEntity):
    '''
    Provides the query for BlogSync.
    '''
    cId = AsRangeOrdered
    syncStart = AsDateTimeOrdered
    auto = AsBoolean

# --------------------------------------------------------------------

@service((Entity, BlogSync), (QEntity, QBlogSync))
class IBlogSyncService(IEntityService):
    '''
    Provides the service methods for the blog sync.
    '''

    @call
    def getBlogSync(self, blog:Blog.Id, q:QBlogSync=None, **options:SliceAndTotal) -> Iter(BlogSync.Id):
        '''
        Returns the list of blog sync models for the given blog.

        @param blog: Blog.Id
            The blog identifier
        @param offset: integer
            The offset to retrieve the entities from.
        @param limit: integer
            The limit of entities to retrieve.
        @param detailed: boolean
            If true will present the total count, limit and offset for the partially returned collection.
        @param q: QBlogSync
            The query to search by.
        '''
