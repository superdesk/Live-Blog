'''
Created on Apr 15, 2013

@package: superdesk desk
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Martin Saturka

API specifications for task link types.
'''

from ally.api.config import service
from ally.support.api.keyed import Entity, IEntityGetService, IEntityFindService
from superdesk.api.domain_superdesk import modelDesk

# --------------------------------------------------------------------

@modelDesk
class TaskLinkType(Entity):
    '''
    Provides the task link type model.
    '''
    IsOn = bool

# --------------------------------------------------------------------
# No query
# --------------------------------------------------------------------

@service((Entity, TaskLinkType))
class ITaskLinkTypeService(IEntityGetService, IEntityFindService):
    '''
    Provides the service methods for the task link types.
    '''
