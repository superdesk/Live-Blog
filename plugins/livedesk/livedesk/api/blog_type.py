'''
Created on Aug 30, 2012

@package: livedesk
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mugur Rus

API specifications for livedesk blog type.
'''

from ally.api.config import query, service
from ally.api.criteria import AsLike
from ally.support.api.entity import Entity, IEntityService, QEntity
from livedesk.api.domain_livedesk import modelLiveDesk

# --------------------------------------------------------------------

@modelLiveDesk
class BlogType(Entity):
    '''
    Provides the blog type model.
    '''
    Name = str

# --------------------------------------------------------------------

@query(BlogType)
class QBlogType(QEntity):
    '''
    Provides the query for active blog type model.
    '''
    name = AsLike

# --------------------------------------------------------------------

@service((Entity, BlogType), (QEntity, QBlogType))
class IBlogTypeService(IEntityService):
    '''
    Provides the service methods for the blogs.
    '''
