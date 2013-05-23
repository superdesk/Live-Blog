'''
Created on May 21, 2013

@package: content article
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Martin Saturka

API specifications for output target types.
'''

from ally.api.config import service
from ally.support.api.keyed import Entity, IEntityGetService, IEntityFindService
from content.packager.api.domain_content import modelContent

# --------------------------------------------------------------------

@modelContent
class TargetType(Entity):
    '''
    Provides the output target type model.
    '''

# --------------------------------------------------------------------
# No query
# --------------------------------------------------------------------

@service((Entity, TargetType))
class ITargetTypeService(IEntityGetService, IEntityFindService):
    '''
    Provides the service methods for the output target types.
    '''
