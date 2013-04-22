'''
Created on Apr 8, 2013

@package: superdesk desk
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Martin Saturka

API specifications for task statuses.
'''

from ally.api.config import service
from ally.support.api.keyed import Entity, IEntityGetService, IEntityFindService
from superdesk.api.domain_superdesk import modelDesk

# --------------------------------------------------------------------

@modelDesk
class TaskStatus(Entity):
    '''
    Provides the task status model.
    '''
    Active = bool

# --------------------------------------------------------------------
# No query
# --------------------------------------------------------------------

@service((Entity, TaskStatus))
class ITaskStatusService(IEntityGetService, IEntityFindService):
    '''
    Provides the service methods for the task statuses.
    '''
