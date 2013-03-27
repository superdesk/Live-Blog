'''
Created on Mar 26, 2013

@package: livedesk
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Martin Saturka

API specifications for livedesk blog provider.
'''

from livedesk.api.domain_livedesk import modelLiveDesk
from ally.api.config import query, service
from ally.api.criteria import AsLikeOrdered
from ally.api.type import Reference
from ally.support.api.entity import Entity, QEntity, IEntityService

# --------------------------------------------------------------------

@modelLiveDesk
class BlogProvider(Entity):
    '''
    Provides the blog provider model.
    '''
    Title = str
    Description = str
    URL = Reference

# --------------------------------------------------------------------

@query(BlogProvider)
class QBlogProvider(QEntity):
    '''
    Provides the query for active blog provider model.
    '''
    title = AsLikeOrdered
    description = AsLikeOrdered

# --------------------------------------------------------------------

@service((Entity, BlogProvider), (QEntity, QBlogProvider))
class IBlogProviderService(IEntityService):
    '''
    Provides the service methods for the blog providers.
    '''
