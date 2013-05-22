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
from sqlalchemy.sql.expression import not_
from superdesk.desk.meta.task_status import TaskStatusMapped
from superdesk.desk.meta.task_type import TaskTypeTaskStatusMapped
from sql_alchemy.impl.keyed import EntityServiceAlchemy
from sqlalchemy.orm.exc import NoResultFound
from ally.exception import InputError

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
        
        
    def getStatuses(self, taskTypeKey, offset=None, limit=None, detailed=True):
        '''
        @see: ITaskTypeService.getStatuses
        '''

        sql = self.session().query(TaskStatusMapped).join(TaskTypeTaskStatusMapped)
        sql = sql.filter(TaskTypeTaskStatusMapped.taskType == taskTypeKey)
   
        entities = buildLimits(sql, offset, limit).all()
        if detailed: return IterPart(entities, sql.count(), offset, limit)

        return entities


    def getUnasignedStatuses(self, taskTypeKey, offset=None, limit=None, detailed=True):
        '''
        @see: ITaskTypeService.getUnasignedStatuses
        '''
        sqlTask = self.session().query(TaskTypeTaskStatusMapped.taskStatus)
        sqlTask = sqlTask.filter(TaskTypeTaskStatusMapped.taskType == taskTypeKey)
        
        sql = self.session().query(TaskStatusMapped)
        sql = sql.filter(not_(TaskStatusMapped.id.in_(sqlTask.subquery())))

        entities = buildLimits(sql, offset, limit).all()
        if detailed: return IterPart(entities, sql.count(), offset, limit)

        return entities


    def attachTaskStatus(self, taskTypeKey, taskStatusKey):
        '''
        @see ITaskTypeService.attachStatus
        '''
        taskTypeId = self._typeId(taskTypeKey)
        taskStatusId = self._statusId(taskStatusKey)
        
        sql = self.session().query(TaskTypeTaskStatusMapped)
        sql = sql.filter(TaskTypeTaskStatusMapped.taskType == taskTypeId)
        sql = sql.filter(TaskTypeTaskStatusMapped.taskStatus == taskStatusId)
        if sql.count() == 1: return

        taskTypeTaskStatus = TaskTypeTaskStatusMapped()
        taskTypeTaskStatus.desk = taskTypeId
        taskTypeTaskStatus.user = taskStatusId

        self.session().add(taskTypeTaskStatus)
        self.session().flush((taskTypeTaskStatus,))
        

    def detachTaskStatus(self, taskTypeKey, taskStatusKey) -> bool:
        '''
        @see IDeskService.detachUser
        '''
        taskTypeId = self._typeId(taskTypeKey)
        taskStatusId = self._statusId(taskStatusKey)
        
        sql = self.session().query(TaskTypeTaskStatusMapped)
        sql = sql.filter(TaskTypeTaskStatusMapped.taskType == taskTypeId)
        sql = sql.filter(TaskTypeTaskStatusMapped.taskStatus == taskStatusId)
        count_del = sql.delete()

        return (0 < count_del)
    
    def _statusId(self, key):
        '''
        Provides the task status id that has the provided key.
        '''
        try:
            sql = self.session().query(TaskStatusMapped.id).filter(TaskStatusMapped.Key == key)
            return sql.one()[0]
        except NoResultFound:
            raise InputError('Invalid task status %(status)s') % dict(status=key)
        
    def _typeId(self, key):
        '''
        Provides the task type id that has the provided key.
        '''
        try:
            sql = self.session().query(TaskTypeMapped.id).filter(TaskTypeMapped.Key == key)
            return sql.one()[0]
        except NoResultFound:
            raise InputError('Invalid task type %(type)s') % dict(type=key)        
