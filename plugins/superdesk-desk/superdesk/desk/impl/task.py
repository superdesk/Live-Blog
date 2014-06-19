'''
Created on April 2, 2013

@package: superdesk desk
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Martin Saturka

Contains the SQL alchemy implementation for desk task API.
'''

from ..api.task import ITaskService, Task, QTask
from ..meta.task import TaskMapped, TaskNest
from ..meta.task_status import TaskStatusMapped
from ..meta.task_link import TaskLinkMapped
from ally.container.ioc import injected
from ally.container.support import setup
from ally.api.error import InputError
from ally.support.api.util_service import copyContainer
from sql_alchemy.support.util_service import buildQuery, buildLimits
from sql_alchemy.impl.entity import EntityServiceAlchemy
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.sql.expression import and_, or_
from ally.api.extension import IterPart
from superdesk.person_icon.api.person_icon import IPersonIconService
from ally.container import wire
from ally.core.error import DevelError

# --------------------------------------------------------------------

@injected
@setup(ITaskService, name='taskService')
class TaskServiceAlchemy(EntityServiceAlchemy, ITaskService):
    '''
    Implementation for @see: ITaskService
    '''

    personIconService = IPersonIconService; wire.entity('personIconService')

    def __init__(self):
        '''
        Construct the desk task service.
        '''
        EntityServiceAlchemy.__init__(self, TaskMapped, QTask)

    def getAll(self, deskId=None, userId=None, statusKey=None, thumbSize=None, offset=None, limit=None, detailed=False, q=None):
        '''
        @see: ITaskService.getAll
        dealing with status part
        '''
        sql = self.session().query(TaskMapped)
        if deskId:
            sql = sql.filter(TaskMapped.Desk == deskId)
        if userId:
            sql = sql.filter(TaskMapped.User == userId)
        sql = sql.filter(TaskMapped.Parent == None)
        if statusKey:
            sql = sql.join(TaskStatusMapped).filter(TaskStatusMapped.Name == statusKey)
        if q:
            sql = buildQuery(sql, q, TaskMapped)
        sqlLimit = buildLimits(sql, offset, limit)
        if detailed: return IterPart(self._addImages(sqlLimit.all(), thumbSize), sql.count(), offset, limit)
        return sqlLimit.all()

    def insert(self, task):
        '''
        @see: ITaskService.insert
        dealing with status, parent and nested_sets parts
        '''
        assert isinstance(task, Task), 'Invalid task %s' % task
        taskDb = TaskMapped()
        taskDb.statusId = self._statusId(task.Status)
        copyContainer(task, taskDb, exclude=('Status', 'Parent',))

        # putting into nested sets
        nestDb = TaskNest()
        nestDb.upperBar = 1
        nestDb.lowerBar = 2

        taskDb.Parent = None
        if task.Parent is not None:
            parentDb = self.session().query(TaskMapped).get(task.Parent)
            if not parentDb: raise InputError('Unknown parent task %s' % Task.Parent)
            taskDb.Parent = parentDb.Id
            try: nestDbParent = self.session().query(TaskNest).filter(TaskNest.task == parentDb.Id).one()
            except NoResultFound: raise InputError('Unknown parent task %s' % Task.Parent)
        else:
            nestDbParent = None

        try:
            self.session().add(taskDb)
            self.session().flush((taskDb,))

            nestDb.task = taskDb.Id
            nestDb.group = taskDb.Id

            self.session().add(nestDb)
            self.session().flush((nestDb,))

        except SQLAlchemyError as e:
            raise DevelError(e, taskDb)

        if nestDbParent: self._attach(nestDbParent, nestDb)

        task.Id = taskDb.Id
        return task.Id

    def update(self, task):
        '''
        @see: ITaskService.update
        dealing with status and parent parts
        '''
        assert isinstance(task, Task), 'Invalid task %s' % task
        taskDb = self.session().query(TaskMapped).get(task.Id)
        if not taskDb: raise InputError('Unknown task %s' % Task.Id)
        if Task.Status in task: taskDb.statusId = self._statusId(task.Status)

        if Task.Parent in task:
            if taskDb.Parent != task.Parent:
                try: nestDb = self.session().query(TaskNest).filter(TaskNest.task == taskDb.Id).one()
                except NoResultFound: raise InputError('Unknown task %s' % Task.Id)

                if task.Parent is None:
                    self._detach(nestDb)
                    taskDb.Parent = None

                else:
                    try: nestDbParent = self.session().query(TaskNest).filter(TaskNest.task == task.Parent).one()
                    except NoResultFound: raise InputError('Unknown parent task %s' % Task.Parent)

                    # check whether the subtree_node is not an ancestor of the parent_node
                    if nestDb.group == nestDbParent.group and nestDb.upperBar <= nestDbParent.upperBar and \
                    nestDb.lowerBar >= nestDbParent.lowerBar:
                        raise InputError('Can not create a cycle in the task tree')

                    self._detach(nestDb)
                    self._attach(nestDbParent, nestDb)
                    taskDb.Parent = task.Parent

        try:
            self.session().flush((copyContainer(task, taskDb, exclude=('Status', 'Parent')),))
        except SQLAlchemyError as e: raise DevelError(e, TaskMapped)


    def delete(self, taskId):
        '''
        @see: ITaskService.delete
        dealing with nested_sets part
        '''

        taskDb = self.session().query(TaskMapped).get(taskId)
        if not taskDb: raise InputError('Unknown task %s' % Task.Id)
        nestDb = None
        try:
            nestDb = self.session().query(TaskNest).filter(TaskNest.task == taskId).one()
        except NoResultFound:
            raise InputError('Unknown task %s' % Task.Id)

        if (nestDb.upperBar + 1) != nestDb.lowerBar:
            raise InputError('Task %(task)d has subtasks: %s' % (dict(task=taskId), Task.Id))

        if taskDb.Parent:
            self._detach(nestDb)

        try:
            sql = self.session().query(TaskLinkMapped)
            sql = sql.filter(or_(TaskLinkMapped.Head == taskId, TaskLinkMapped.Tail == taskId))
            sql = sql.delete()
        except:
            pass

        self.session().delete(nestDb)
        self.session().delete(taskDb)

        return True

    def getSubtasks(self, taskId, statusKey=None, thumbSize=None, offset=None, limit=None, detailed=False, q=None):
        '''
        @see: ITaskService.getSubtasks
        '''
        return self._addImages(self._getSubnodes(taskId, False, statusKey, offset, limit, detailed, q), thumbSize)

    def getSubtree(self, taskId, statusKey=None, thumbSize=None, offset=None, limit=None, detailed=False, q=None):
        '''
        @see: ITaskService.getSubtree
        '''
        return self._addImages(self._getSubnodes(taskId, True, statusKey, offset, limit, detailed, q), thumbSize)

    # ----------------------------------------------------------------

    def _getSubnodes(self, taskId, wholeSubtree, statusKey=None, offset=None, limit=None, detailed=False, q=None):
        '''
        Makes the task list retrieval.
        '''
        taskDb = self.session().query(TaskMapped).get(taskId)
        if not taskDb: raise InputError('Unknown task %s' % Task.Id)
        nestDb = None
        try:
            nestDb = self.session().query(TaskNest).filter(TaskNest.task == taskId).one()
        except NoResultFound:
            raise InputError('Unknown task %s' % Task.Id)

        sql = self.session().query(TaskMapped)

        if not wholeSubtree:
            sql = sql.filter(TaskMapped.Parent == taskId)

        if statusKey:
            sql = sql.join(TaskStatusMapped).filter(TaskStatusMapped.Name == statusKey)
        if q:
            sql = buildQuery(sql, q, TaskMapped)

        sql = sql.join(TaskNest, TaskMapped.Id == TaskNest.task)
        sql = sql.filter(TaskNest.group == nestDb.group)
        sql = sql.filter(TaskNest.upperBar > nestDb.upperBar)
        sql = sql.filter(TaskNest.lowerBar < nestDb.lowerBar)

        sqlLimit = buildLimits(sql, offset, limit)
        if detailed: return IterPart(sqlLimit.all(), sql.count(), offset, limit)
        return sqlLimit.all()

    def _statusId(self, key):
        '''
        Provides the task status id that has the provided key.
        '''
        try:
            sql = self.session().query(TaskStatusMapped.id).filter(TaskStatusMapped.Name == key)
            return sql.one()[0]
        except NoResultFound:
            raise InputError('Invalid task status %(status)s: %s' % (dict(status=key), Task.Status))

    def _attach(self, nestDb, nestDbSubtask):
        '''
        Sets the nested sets on subtask attaching.
        '''

        # since the subtree_node is a root of its (sub)tree here, and parent is not in that (sub)tree,
        # we are sure that groups of parent_node and subtree_node are different
        taskGroup = nestDb.group
        subtaskGroup = nestDbSubtask.group

        subtaskUpper = nestDbSubtask.upperBar
        subtaskLower = nestDbSubtask.lowerBar
        subtaskWidth = 1 + subtaskLower - subtaskUpper

        taskLower = nestDb.lowerBar

        diffLift = taskLower - subtaskUpper

        # forming the gap in base tree, on the lower bars
        sql = self.session().query(TaskNest).filter(TaskNest.group == taskGroup)
        sql = sql.filter(TaskNest.lowerBar >= taskLower)
        sql = sql.update({TaskNest.lowerBar: TaskNest.lowerBar + subtaskWidth})

        # forming the gap in base tree, on the upper bars
        sql = self.session().query(TaskNest).filter(TaskNest.group == taskGroup)
        sql = sql.filter(TaskNest.upperBar >= taskLower)
        sql = sql.update({TaskNest.upperBar: TaskNest.upperBar + subtaskWidth})

        # moving the new subtree down
        sql = self.session().query(TaskNest).filter(TaskNest.group == subtaskGroup)
        sql = sql.update({TaskNest.upperBar: (TaskNest.upperBar + diffLift), TaskNest.lowerBar: (TaskNest.lowerBar + diffLift)})

        # setting new group id for the sub-tree
        sql = self.session().query(TaskNest).filter(TaskNest.group == subtaskGroup)
        sql = sql.update({TaskNest.group: taskGroup})

        return True

    def _detach(self, nestDbSubtask):
        '''
        Sets the nested sets on subtask detaching.
        '''

        taskGroup = nestDbSubtask.group
        subtaskGroup = nestDbSubtask.id

        if taskGroup == subtaskGroup:
            return True

        subtaskUpper = nestDbSubtask.upperBar
        subtaskLower = nestDbSubtask.lowerBar
        subtaskWidth = 1 + subtaskLower - subtaskUpper
        diffLift = subtaskUpper - 1

        # setting new group id for the sub-tree
        sql = self.session().query(TaskNest).filter(TaskNest.group == taskGroup)
        sql = sql.filter(and_(TaskNest.upperBar >= subtaskUpper, TaskNest.lowerBar <= subtaskLower))
        sql = sql.update({TaskNest.group: subtaskGroup})

        # removing the gap in remaining tree, on the upper bars
        sql = self.session().query(TaskNest).filter(TaskNest.group == taskGroup)
        sql = sql.filter(TaskNest.upperBar > subtaskUpper)
        sql = sql.update({TaskNest.upperBar: TaskNest.upperBar - subtaskWidth})

        # removing the gap in remaining tree, on the lower bars
        sql = self.session().query(TaskNest).filter(TaskNest.group == taskGroup)
        sql = sql.filter(TaskNest.lowerBar > subtaskUpper)
        sql = sql.update({TaskNest.lowerBar: TaskNest.lowerBar - subtaskWidth})

        # moving the new tree up
        sql = self.session().query(TaskNest).filter(TaskNest.group == subtaskGroup)
        sql = sql.update({TaskNest.upperBar: (TaskNest.upperBar - diffLift), TaskNest.lowerBar: (TaskNest.lowerBar - diffLift)})

        return True

    # TODO: implement a proper solution
    def _addImage(self, task, thumbSize='medium'):
        '''
        Takes the image for the user and adds the thumbnail to the response
        '''
        assert isinstance(task, Task)

        try:
            if task.User is not None:
                task.UserImage = self.personIconService.getByPersonId(id=task.User, thumbSize=thumbSize).Thumbnail
        except: pass

        return task

    def _addImages(self, tasks, thumbSize='medium'):
        for task in tasks:
            task = self._addImage(task, thumbSize)
            yield task
