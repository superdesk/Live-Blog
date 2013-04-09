'''
Created on April 2, 2013

@package: superdesk desk
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Martin Saturka

Contains the SQL alchemy implementation for desk task API.
'''

from ..api.task import ITaskService
from ..meta.task import TaskMapped
from ..meta.task_status import TaskStatusMapped
from ally.container.ioc import injected
from ally.container.support import setup
from ally.exception import InputError
from ally.support.api.util_service import copy
from sql_alchemy.impl.entity import EntityServiceAlchemy
from ally.support.sqlalchemy.util_service import buildQuery, buildLimits
from ally.api.extension import IterPart

# --------------------------------------------------------------------

@injected
@setup(ITaskService, name='taskService')
class TaskServiceAlchemy(EntityServiceAlchemy, ITaskService):
    '''
    Implementation for @see: ITaskService
    '''

    def __init__(self):
        '''
        Construct the desk task service.
        '''
        EntityServiceAlchemy.__init__(self, TaskMapped)

    def getAll(self, statusLabel=None, offset=None, limit=None, detailed=False, q=None):
        '''
        @see: ITaskService.getAll
        '''
        sql = self.session().query(TaskMapped)
        if statusLabel:
            sql = sql.join(TaskStatusMapped).filter(TaskStatusMapped.Key == statusLabel)
        if q: sql = buildQuery(sql, q, TaskMapped)
        sqlLimit = buildLimits(sql, offset, limit)
        if detailed: return IterPart(sqlLimit.all(), sql.count(), offset, limit)
        return sqlLimit.all()

    def insert(self, task):
        '''
        @see: ITaskService.insert
        '''
        raise InputError('Not yet implemented')

    def update(self, task):
        '''
        @see: ITaskService.update
        '''
        return False

    def delete(self, id):
        '''
        @see: ITaskService.delete
        '''
        return False

    def listAncestors(self, taskId, ascending=True):
        '''
        @see: ITaskService.listAncestors
        '''

        return ()

    def listSubtasks(self, taskId, orderBy=None, offset=None, limit=None, detailed=False):
        '''
        @see: ITaskService.listSubtasks
        '''

        return ()

    def attachSubtree(self, taskId, subtaskId):
        '''
        @see ITaskService.attachSubtree
        '''

        return False

    def detachSubtree(self, subtaskId):
        '''
        @see ITaskService.detachSubtree
        '''

        return False
