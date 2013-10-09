'''
Created on Apr 19, 2012

@package: superdesk posts
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

API specifications for post types.
'''

from ally.api.config import service
from superdesk.api.domain_superdesk import modelData
from ally.support.api.entity import IEntityGetPrototype, IEntityFindPrototype

# --------------------------------------------------------------------

@modelData(id='Key')
class PostType:
    '''Provides the post type model.'''
    Key = str

# --------------------------------------------------------------------

# No query

# --------------------------------------------------------------------

@service(('Entity', PostType))
class IPostTypeService(IEntityGetPrototype, IEntityFindPrototype):
    '''Provides the service methods for the post types.'''
