'''
Created on May 18, 2013

@package: superdesk desk
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Ioan v. Pocol

API specifications for tasks types and associated task statuses.
'''

from ally.api.config import service, call, query, LIMIT_DEFAULT, DELETE, UPDATE, \
    GET
from ally.api.criteria import AsLikeOrdered
from ally.api.type import Iter
from ally.support.api.entity import Entity, IEntityService, QEntity
from superdesk.api.domain_superdesk import modelDesk
from superdesk.desk.api.task_status import TaskStatus

# --------------------------------------------------------------------

@modelDesk
class TaskType(Entity):
    '''
    Provides the task type model.
    '''
    Name = str
    Description = str

# --------------------------------------------------------------------

@query(TaskType)
class QTaskType(QEntity):
    '''
    Provides the query for task type model.
    '''
    name = AsLikeOrdered
    description = AsLikeOrdered

# --------------------------------------------------------------------

@service((Entity, TaskType))
class ITaskTypeService(IEntityService):
    '''
    Provides the service methods for the task type.
    '''

    @call(method=GET)
    def getStatuses(self, taskTypeId:TaskType.Id, offset:int=None, limit:int=LIMIT_DEFAULT, 
                    detailed:bool=True) -> Iter(TaskStatus):
        '''
        Provides all statuses from the associated desk.
        '''

    @call(method=GET, webName="Unassigned")
    def getUnasignedStatuses(self, taskTypeId:TaskType.Id, offset:int=None, limit:int=LIMIT_DEFAULT, 
                       detailed:bool=True) -> Iter(TaskStatus):
        '''
        Provides all statuses associated to the task type.
        '''

    @call(method=UPDATE)
    def attachTaskStatus(self, taskTypeId:TaskType.Id, taskStatusId:TaskStatus.Id):
        '''
        Attach the task status to the task type.
        '''

    @call(method=DELETE)
    def detachTaskStatus(self, taskTypeId:TaskType.Id, taskStatusId:TaskStatus.Id) -> bool:
        '''
        Detach the task status from the task type.
        '''

