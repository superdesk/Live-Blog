'''
Created on Apr 19, 2012

@package: superdesk posts
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

API specifications for post types.
'''

from ally.api.config import service
from ally.support.api.keyed import Entity, IEntityGetService, IEntityFindService
from superdesk.api.domain_superdesk import modelData

# --------------------------------------------------------------------

@modelData
class PostType(Entity):
    '''
    Provides the post type model.
    '''

# --------------------------------------------------------------------

# No query

# --------------------------------------------------------------------

@service((Entity, PostType))
class IPostTypeService(IEntityGetService, IEntityFindService):
    '''
    Provides the service methods for the post types.
    '''
