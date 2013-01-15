'''
Created on Jan 11, 2013

@package: livedesk
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mugur Rus

API specifications for livedesk blog theme.
'''

from livedesk.api.domain_livedesk import modelLiveDesk
from ally.api.config import query, service
from ally.api.criteria import AsLike
from ally.api.type import Reference
from ally.support.api.keyed import Entity, QEntity, IEntityService

# --------------------------------------------------------------------

@modelLiveDesk
class BlogTheme(Entity):
    '''
    Provides the blog type model.
    '''
    URL = Reference

# --------------------------------------------------------------------

@query(BlogTheme)
class QBlogTheme(QEntity):
    '''
    Provides the query for active blog type model.
    '''
    key = AsLike

# --------------------------------------------------------------------

@service((Entity, BlogTheme), (QEntity, QBlogTheme))
class IBlogThemeService(IEntityService):
    '''
    Provides the service methods for the blog themes.
    '''
