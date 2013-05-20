'''
Created on May 18, 2013

@package: superdesk desk
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Ioan v. Pocol

Contains the SQL alchemy implementation for task type status API.
'''

from ..api.task_type import ITaskTypeService
from ..meta.task_type import TaskTypeMapped
from ally.api.extension import IterPart
from ally.container.ioc import injected
from ally.container.support import setup
from ally.support.sqlalchemy.util_service import buildLimits
from sql_alchemy.impl.entity import EntityServiceAlchemy
from sqlalchemy.sql.expression import not_
from superdesk.desk.meta.task_status import TaskStatusMapped
from superdesk.desk.meta.task_type import TaskTypeTaskStatusMapped

# --------------------------------------------------------------------

@injected
@setup(ITaskTypeService, name='taskType')
class TaskTypeServiceAlchemy(EntityServiceAlchemy, ITaskTypeService):
    '''
    Implementation for @see: ITaskTypeService
    '''

    def __init__(self):
        '''
        Construct the task type service.
        '''
        EntityServiceAlchemy.__init__(self, TaskTypeMapped)
        
        
    def getStatuses(self, taskTypeId, offset=None, limit=None, detailed=True):
        '''
        @see: ITaskTypeService.getStatuses
        '''

        sql = self.session().query(TaskStatusMapped).join(TaskTypeTaskStatusMapped)
        sql = sql.filter(TaskTypeTaskStatusMapped.taskType == taskTypeId)
   
        entities = buildLimits(sql, offset, limit).all()
        if detailed: return IterPart(entities, sql.count(), offset, limit)

        return entities


    def getUnasignedStatuses(self, taskTypeId, offset=None, limit=None, detailed=True):
        '''
        @see: ITaskTypeService.getUnasignedStatuses
        '''
        sql = self.session().query(TaskStatusMapped)
        sql = sql.filter(not_(TaskStatusMapped.Id.in_(self.session().query(TaskTypeTaskStatusMapped.taskStatus).filter(TaskTypeTaskStatusMapped.taskType == taskTypeId).subquery())))

        entities = buildLimits(sql, offset, limit).all()
        if detailed: return IterPart(entities, sql.count(), offset, limit)

        return entities


    def attachTaskStatus(self, taskTypeId, taskStatusId):
        '''
        @see ITaskTypeService.attachStatus
        '''
        sql = self.session().query(TaskTypeTaskStatusMapped)
        sql = sql.filter(TaskTypeTaskStatusMapped.taskType == taskTypeId)
        sql = sql.filter(TaskTypeTaskStatusMapped.taskStatus == taskStatusId)
        if sql.count() == 1: return

        taskTypeTaskStatus = TaskTypeTaskStatusMapped()
        taskTypeTaskStatus.desk = taskTypeId
        taskTypeTaskStatus.user = taskStatusId

        self.session().add(taskTypeTaskStatus)
        self.session().flush((taskTypeTaskStatus,))
        

    def detachTaskStatus(self, taskTypeId, taskStatusId) -> bool:
        '''
        @see IDeskService.detachUser
        '''
        sql = self.session().query(TaskTypeTaskStatusMapped)
        sql = sql.filter(TaskTypeTaskStatusMapped.taskType == taskTypeId)
        sql = sql.filter(TaskTypeTaskStatusMapped.taskStatus == taskStatusId)
        count_del = sql.delete()

        return (0 < count_del)
