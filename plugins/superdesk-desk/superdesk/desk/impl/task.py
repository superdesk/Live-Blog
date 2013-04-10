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
from sqlalchemy.sql.expression import and_
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

        if not taskDb.isRoot:
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

        t_group = task_nestDb.group

        sql = self.session().query(TaskMapped).join(TaskNestMapped)
        sql = sql.filter(TaskNestMapped.group == t_group)
        sql = sql.filter(TaskNestMapped.upperBar < task_nestDb.upperBar)
        sql = sql.filter(TaskNestMapped.lowerBar > task_nestDb.lowerBar)

        if ascending:
            sql = sql.order_by(TaskNestMapped.lowerBar)
        else:
            sql = sql.order_by(TaskNestMapped.upperBar)

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

        t_group = task_nestDb.group

        sql = self.session().query(TaskMapped)

        if statusLabel:
            sql = sql.join(TaskStatusMapped).filter(TaskStatusMapped.Key == statusLabel)
        if q:
            sql = buildQuery(sql, q, TaskMapped)
            if QTask.rootOnly.value in q:
                if q.rootOnly.value:
                    sql = sql.filter(TaskMapped.isRoot == True)

        sql = sql.join(TaskNestMapped)
        sql = sql.filter(TaskNestMapped.group == t_group)
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

        # not attaching itself to itself
        if taskId == subtaskId:
            return False

        taskDb = self.session().query(TaskMapped).get(taskId)
        if not taskDb: raise InputError(Ref(_('Unknown task %(task)d') % dict(task=taskId),))
        task_nestDb = None
        try:
            task_nestDb = self.session().query(TaskNestMapped).filter(TaskNestMapped.task == taskId).one()
        except NoResultFound:
            raise InputError(Ref(_('Unknown task %(task)d') % dict(task=taskId),))

        subtaskDb = self.session().query(TaskMapped).get(subtaskId)
        if not subtaskDb: raise InputError(Ref(_('Unknown subtask %(subtask)d') % dict(subtask=subtaskId),))
        subtask_nestDb = None
        try:
            subtask_nestDb = self.session().query(TaskNestMapped).filter(TaskNestMapped.task == subtaskId).one()
        except NoResultFound:
            raise InputError(Ref(_('Unknown subtask %(subtask)d') % dict(subtask=subtaskId),))

        # check whether the subtree_node is not an ancestor of the parent_node
        if subtask_nestDb.group == task_nestDb.group:
            if subtask_nestDb.upperBar <= task_nestDb.upperBar:
                if subtask_nestDb.lowerBar >= task_nestDb.lowerBar:
                    raise InputError(Ref(_('Node %(task)d is subtask of %(subtask)d') % dict(subtask=subtaskId, task=taskId),))

        if not subtaskDb.isRoot:
            self._detach(subtask_nestDb)
        subtaskDb.isRoot = False

        self._attach(task_nestDb, subtask_nestDb)

        return True

    def detachSubtree(self, taskId, subtaskId):
        '''
        @see ITaskService.detachSubtree
        '''

        # not detaching from itself
        if taskId == subtaskId:
            raise InputError(Ref(_('Nodes %(task)d and (subtask)d are the same nodes') % dict(subtask=subtaskId, task=taskId),))

        taskDb = self.session().query(TaskMapped).get(taskId)
        if not taskDb: raise InputError(Ref(_('Unknown task %(task)d') % dict(task=taskId),))
        task_nestDb = None
        try:
            task_nestDb = self.session().query(TaskNestMapped).filter(TaskNestMapped.task == taskId).one()
        except NoResultFound:
            raise InputError(Ref(_('Unknown task %(task)d') % dict(task=taskId),))

        subtaskDb = self.session().query(TaskMapped).get(subtaskId)
        if not subtaskDb: raise InputError(Ref(_('Unknown subtask %(subtask)d') % dict(subtask=subtaskId),))
        subtask_nestDb = None
        try:
            subtask_nestDb = self.session().query(TaskNestMapped).filter(TaskNestMapped.task == subtaskId).one()
        except NoResultFound:
            raise InputError(Ref(_('Unknown subtask %(subtask)d') % dict(subtask=subtaskId),))

        # check whether the subtree_node is a direct child of the parent_node
        if subtask_nestDb.group != task_nestDb.group:
            raise InputError(Ref(_('Node %(subtask)d is not subtask of %(task)d') % dict(subtask=subtaskId, task=taskId),))

        if subtask_nestDb.upperBar <= task_nestDb.upperBar:
            raise InputError(Ref(_('Node %(subtask)d is not subtask of %(task)d') % dict(subtask=subtaskId, task=taskId),))

        if subtask_nestDb.lowerBar >= task_nestDb.lowerBar:
            raise InputError(Ref(_('Node %(subtask)d is not subtask of %(task)d') % dict(subtask=subtaskId, task=taskId),))

        if subtask_nestDb.depth != (task_nestDb.depth + 1):
            raise InputError(Ref(_('Node %(subtask)d is not subtask of %(task)d') % dict(subtask=subtaskId, task=taskId),))

        self._detach(subtask_nestDb)
        subtaskDb.isRoot = False

        return True

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


    def _attach(self, task_nestDb, subtask_nestDb):

        # since the subtree_node is a root of its (sub)tree here, and parent is not in that (sub)tree,
        # we are sure that groups of parent_node and subtree_node are different
        t_group = task_nestDb.group
        s_group = subtask_nestDb.group

        d_depth = task_nestDb.depth + 1

        s_upper = subtask_nestDb.upperBar
        s_lower = subtask_nestDb.lowerBar
        s_width = 1 + s_lower - s_upper

        t_lower = task_nestDb.lowerBar

        d_lift = t_lower - s_upper

        # forming the gap in base tree, on the lower bars
        sql = self.session().query(TaskNestMapped).filter(TaskNestMapped.group == t_group)
        sql = sql.filter(TaskNestMapped.lowerBar >= t_lower)
        sql = sql.update({TaskNestMapped.lowerBar: TaskNestMapped.lowerBar + s_width})

        # forming the gap in base tree, on the upper bars
        sql = self.session().query(TaskNestMapped).filter(TaskNestMapped.group == t_group)
        sql = sql.filter(TaskNestMapped.upperBar >= t_lower)
        sql = sql.update({TaskNestMapped.upperBar: TaskNestMapped.upperBar + s_width})

        # moving the new subtree down
        sql = self.session().query(TaskNestMapped).filter(TaskNestMapped.group == s_group)
        sql = sql.update({TaskNestMapped.upperBar: (TaskNestMapped.upperBar + d_lift), TaskNestMapped.lowerBar: (TaskNestMapped.lowerBar + d_lift)})

        # adjusting the depth
        sql = self.session().query(TaskNestMapped).filter(TaskNestMapped.group == s_group)
        sql = sql.update({TaskNestMapped.depth: (TaskNestMapped.depth + d_depth)})

        # setting new group id for the sub-tree
        sql = self.session().query(TaskNestMapped).filter(TaskNestMapped.group == s_group)
        sql = sql.update({TaskNestMapped.group: t_group})

        return True

    def _detach(self, subtask_nestDb):

        t_group = subtask_nestDb.group
        s_group = subtask_nestDb.id

        d_depth = subtask_nestDb.depth

        if t_group == s_group:
            return True

        s_upper = subtask_nestDb.upperBar
        s_lower = subtask_nestDb.lowerBar
        s_width = 1 + s_lower - s_upper
        s_lift = s_upper -1

        # setting new group id for the sub-tree
        sql = self.session().query(TaskNestMapped).filter(TaskNestMapped.group == t_group)
        sql = sql.filter(and_(TaskNestMapped.upperBar >= s_upper, TaskNestMapped.lowerBar <= s_lower))
        sql = sql.update({TaskNestMapped.group: s_group})

        # removing the gap in remaining tree, on the upper bars
        sql = self.session().query(TaskNestMapped).filter(TaskNestMapped.group == t_group)
        sql = sql.filter(TaskNestMapped.upperBar > s_upper)
        sql = sql.update({TaskNestMapped.upperBar: TaskNestMapped.upperBar - s_width})

        # removing the gap in remaining tree, on the lower bars
        sql = self.session().query(TaskNestMapped).filter(TaskNestMapped.group == t_group)
        sql = sql.filter(TaskNestMapped.lowerBar > s_upper)
        sql = sql.update({TaskNestMapped.lowerBar: TaskNestMapped.lowerBar - s_width})

        # moving the new tree up
        sql = self.session().query(TaskNestMapped).filter(TaskNestMapped.group == s_group)
        sql = sql.update({TaskNestMapped.upperBar: (TaskNestMapped.upperBar - s_lift), TaskNestMapped.lowerBar: (TaskNestMapped.lowerBar - s_lift)})

        # adjusting the depth
        sql = self.session().query(TaskNestMapped).filter(TaskNestMapped.group == s_group)
        sql = sql.update({TaskNestMapped.depth: (TaskNestMapped.depth - d_depth)})

        return True

