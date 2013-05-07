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
from ally.api.config import query, service
from ally.api.criteria import AsRangeOrdered, AsDateTimeOrdered, AsBoolean
from superdesk.source.api.source import Source

# --------------------------------------------------------------------

@modelLiveDesk(name='Sync')
class BlogSync(Entity):
    '''
    Provides the blog sync model.
    '''
    Blog = Blog
    Source = Source
    CId = int
    SyncStart = datetime
    Auto = bool

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
