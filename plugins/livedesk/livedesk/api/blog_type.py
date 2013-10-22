'''
Created on Aug 30, 2012

@package: livedesk
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mugur Rus

API specifications for livedesk blog type.
'''

from ally.api.config import service
from livedesk.api.domain_livedesk import modelLiveDesk
from ally.support.api.entity_named import Entity, IEntityNQService

# --------------------------------------------------------------------

@modelLiveDesk
class BlogType(Entity):
    '''
    Provides the blog type model.
    '''

# --------------------------------------------------------------------

@service((Entity, BlogType))
class IBlogTypeService(IEntityNQService):
    '''
    Provides the service methods for the blogs.
    '''
