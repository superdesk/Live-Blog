'''
Created on May 18, 2013

@package: superdesk desk
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Ioan v. Pocol

API specifications for tasks types and associated task statuses.
'''

from ally.api.config import service, call, LIMIT_DEFAULT, DELETE, UPDATE, GET
from ally.api.type import Iter
from superdesk.api.domain_superdesk import modelDesk
from superdesk.desk.api.task_status import TaskStatus
from ally.support.api.keyed import Entity, IEntityService

# --------------------------------------------------------------------

@modelDesk
class TaskType(Entity):
    '''
    Provides the task type model.
    '''
    Active = bool

# --------------------------------------------------------------------
# no query
# --------------------------------------------------------------------

@service((Entity, TaskType))
class ITaskTypeService(IEntityService):
    '''
    Provides the service methods for the task type.
    '''

    @call(method=GET)
    def getStatuses(self, taskTypeKey:TaskType.Key, offset:int=None, limit:int=LIMIT_DEFAULT, 
                    detailed:bool=True) -> Iter(TaskStatus):
        '''
        Provides all statuses from the associated desk.
        '''

    @call(method=GET, webName="Unassigned")
    def getUnasignedStatuses(self, taskTypeKey:TaskType.Key, offset:int=None, limit:int=LIMIT_DEFAULT, 
                       detailed:bool=True) -> Iter(TaskStatus):
        '''
        Provides all statuses associated to the task type.
        '''

    @call(method=UPDATE)
    def attachTaskStatus(self, taskTypeKey:TaskType.Key, taskStatusKey:TaskStatus.Key):
        '''
        Attach the task status to the task type.
        '''

    @call(method=DELETE)
    def detachTaskStatus(self, taskTypeKey:TaskType.Key, taskStatusKey:TaskStatus.Key) -> bool:
        '''
        Detach the task status from the task type.
        '''

