'''
Created on April 2, 2013

@package: superdesk desk
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Martin Saturka

Contains the SQL alchemy implementation for desk task API.
'''

from ..api.task import ITaskService, Task, QTask
from ..meta.task import TaskMapped, TaskNestMapped
from ..meta.task_status import TaskStatusMapped
from ally.container.ioc import injected
from ally.container.support import setup
from ally.exception import InputError, Ref
from ally.internationalization import _
from ally.support.api.util_service import copy
from ally.support.sqlalchemy.util_service import buildQuery, buildLimits, handle
from sql_alchemy.impl.entity import EntityServiceAlchemy
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm.exc import NoResultFound
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
        dealing with status and root_only parts
        '''
        sql = self.session().query(TaskMapped)
        if statusLabel:
            sql = sql.join(TaskStatusMapped).filter(TaskStatusMapped.Key == statusLabel)
        if q:
            sql = buildQuery(sql, q, TaskMapped)
            if QTask.rootOnly.value in q:
                if q.rootOnly.value:
                    sql = sql.filter(TaskMapped.isRoot == True)
        sqlLimit = buildLimits(sql, offset, limit)
        if detailed: return IterPart(sqlLimit.all(), sql.count(), offset, limit)
        return sqlLimit.all()

    def insert(self, task):
        '''
        @see: ITaskService.insert
        dealing with status and nested_sets parts
        '''

        assert isinstance(task, Task), 'Invalid task %s' % task
        taskDb = TaskMapped()
        taskDb.statusId = self._statusId(task.Status)
        taskDb.isRoot = True
        copy(task, taskDb, exclude=('Status',))

        # putting into nested sets
        task_nestDb = TaskNestMapped()
        task_nestDb.upperBar = 1
        task_nestDb.lowerBar = 2
        task_nestDb.depth = 0

        try:
            self.session().add(taskDb)
            self.session().flush((taskDb,))

            task_nestDb.task = taskDb.Id
            task_nestDb.group = taskDb.Id

            self.session().add(task_nestDb)
            self.session().flush((task_nestDb,))

        except SQLAlchemyError as e:
            handle(e, taskDb)


        task.Id = taskDb.Id
        return taskDb.Id

    def update(self, task):
        '''
        @see: ITaskService.update
        dealing with status part
        '''
        assert isinstance(task, Task), 'Invalid task %s' % task
        taskDb = self.session().query(TaskMapped).get(task.Id)
        if not taskDb: raise InputError(Ref(_('Unknown task id'), ref=Task.Id))
        if Task.Status in task: taskDb.statusId = self._statusId(task.Status)

        try:
            self.session().flush((copy(task, taskDb, exclude=('Status',)),))
        except SQLAlchemyError as e: handle(e, TaskMapped)

    def delete(self, taskId):
        '''
        @see: ITaskService.delete
        dealing with nested_sets part
        '''

        taskDb = self.session().query(TaskMapped).get(taskId)
        if not taskDb: raise InputError(Ref(_('Unknown task %(task)d') % dict(task=taskId),))
        task_nestDb = None
        try:
            task_nestDb = self.session().query(TaskNestMapped).filter(TaskNestMapped.task == taskId).one()
        except NoResultFound:
            raise InputError(Ref(_('Unknown task %(task)d') % dict(task=taskId),))

        if (task_nestDb.upperBar + 1) != task_nestDb.lowerBar:
            raise InputError(Ref(_('Task %(task)d has subtasks') % dict(task=taskId), ref=Task.Id))

        self._detach(task_nestDb)

        self.session().delete(task_nestDb)
        self.session().delete(taskDb)

        return True

    def listAncestors(self, taskId, ascending=True):
        '''
        @see: ITaskService.listAncestors
        '''

        taskDb = self.session().query(TaskMapped).get(taskId)
        if not taskDb: raise InputError(Ref(_('Unknown task %(task)d') % dict(task=taskId),))
        task_nestDb = None
        try:
            task_nestDb = self.session().query(TaskNestMapped).filter(TaskNestMapped.task == taskId).one()
        except NoResultFound:
            raise InputError(Ref(_('Unknown task %(task)d') % dict(task=taskId),))

        sql = self.session().query(TaskMapped).join(TaskNestMapped)
        sql = sql.filter(TaskNestMapped.group == taskId)
        sql = sql.filter(TaskNestMapped.upperBar < task_nestDb.upperBar)
        sql = sql.filter(TaskNestMapped.lowerBar > task_nestDb.lowerBar)

        if ascending:
            sql = sql.order_by(TaskNestMapped.lowerBar)
        else:
            sql = sql.order(TaskNestMapped.upperBar)

        return sql.all()

    def listSubtasks(self, taskId, statusLabel=None, wholeSubtree=False, orderBy=None, offset=None, limit=None, detailed=False, q=None):
        '''
        @see: ITaskService.listSubtasks
        '''

        taskDb = self.session().query(TaskMapped).get(taskId)
        if not taskDb: raise InputError(Ref(_('Unknown task %(task)d') % dict(task=taskId),))
        task_nestDb = None
        try:
            task_nestDb = self.session().query(TaskNestMapped).filter(TaskNestMapped.task == taskId).one()
        except NoResultFound:
            raise InputError(Ref(_('Unknown task %(task)d') % dict(task=taskId),))

        sql = self.session().query(TaskMapped)

        if statusLabel:
            sql = sql.join(TaskStatusMapped).filter(TaskStatusMapped.Key == statusLabel)
        if q:
            sql = buildQuery(sql, q, TaskMapped)
            if QTask.rootOnly.value in q:
                if q.rootOnly.value:
                    sql = sql.filter(TaskMapped.isRoot == True)

        sql = sql.join(TaskNestMapped)
        sql = sql.filter(TaskNestMapped.group == taskId)
        sql = sql.filter(TaskNestMapped.upperBar > task_nestDb.upperBar)
        sql = sql.filter(TaskNestMapped.lowerBar < task_nestDb.lowerBar)

        if not wholeSubtree:
            subLevel = task_nestDb.depth + 1
            sql = sql.filter(TaskNestMapped.depth == subLevel)

        sqlLimit = buildLimits(sql, offset, limit)
        if detailed: return IterPart(sqlLimit.all(), sql.count(), offset, limit)
        return sqlLimit.all()

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

    # ----------------------------------------------------------------

    def _statusId(self, label):
        '''
        Provides the task status id that has the provided label.
        '''
        try:
            sql = self.session().query(TaskStatusMapped.id).filter(TaskStatusMapped.Key == label)
            return sql.one()[0]
        except NoResultFound:
            raise InputError(Ref(_('Invalid task status %(status)s') % dict(status=label), ref=Task.Status))

    def _attach(self, taskId, subtaskId):
        return

    def _detach(self, task_nest):
        return

