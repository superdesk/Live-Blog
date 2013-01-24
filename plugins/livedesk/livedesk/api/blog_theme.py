'''
Created on Jan 11, 2013

@package: livedesk
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mugur Rus

API specifications for livedesk blog theme.
'''

from livedesk.api.domain_livedesk import modelLiveDesk
from ally.api.config import query, service, call, INSERT
from ally.api.criteria import AsLike
from ally.api.type import Reference
from ally.support.api.entity import Entity, QEntity, IEntityService
from ally.api.model import Content

# --------------------------------------------------------------------

@modelLiveDesk
class BlogTheme(Entity):
    '''
    Provides the blog type model.
    '''
    Name = str
    URL = Reference
    IsLocal = bool

# --------------------------------------------------------------------

@query(BlogTheme)
class QBlogTheme(QEntity):
    '''
    Provides the query for active blog type model.
    '''
    name = AsLike

# --------------------------------------------------------------------

@service((Entity, BlogTheme), (QEntity, QBlogTheme))
class IBlogThemeService(IEntityService):
    '''
    Provides the service methods for the blog themes.
    '''

    @call(method=INSERT, webName='Upload')
    def upload(self, content:Content) -> BlogTheme.Id:
        '''
        Upload the theme, also the entity will have automatically assigned the Id to it.

        @param content: Content
            The theme content packaged in a zip file.

        @return: The id assigned to the theme
        @raise InputError: If the theme is not valid.
        '''
