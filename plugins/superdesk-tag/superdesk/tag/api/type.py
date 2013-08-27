'''
Created on August 26, 2013

@package: superdesk tag
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Martin Saturka

API specifications for superdesk tag types.
'''

from ally.api.config import service
from ally.support.api.keyed import Entity, IEntityGetService, IEntityFindService
from superdesk.api.domain_superdesk import modelData

# --------------------------------------------------------------------

@modelData
class TagType(Entity):
    '''
    Provides the tag type model.
    '''

# --------------------------------------------------------------------

# No query

# --------------------------------------------------------------------

@service((Entity, TagType))
class ITagTypeService(IEntityGetService, IEntityFindService):
    '''
    Provides the service methods for the tag types.
    '''
