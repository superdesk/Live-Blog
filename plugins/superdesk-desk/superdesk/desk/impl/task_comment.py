'''
Created on April 23, 2013

@package: superdesk desk
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Martin Saturka

Contains the SQL alchemy implementation for desk task comment API.
'''

from ..api.task_comment import ITaskCommentService, TaskComment, QTaskComment
from ..meta.task_comment import TaskCommentMapped
from ally.container.ioc import injected
from ally.container.support import setup
from ally.exception import InputError, Ref
from ally.internationalization import _
from ally.support.api.util_service import copy
from ally.support.sqlalchemy.util_service import buildQuery, buildLimits, handle
from sql_alchemy.impl.entity import EntityServiceAlchemy
from sqlalchemy.exc import SQLAlchemyError
from ally.api.extension import IterPart
from sqlalchemy.sql.functions import current_timestamp

# --------------------------------------------------------------------

@injected
@setup(ITaskCommentService, name='taskCommentService')
class TaskCommentServiceAlchemy(EntityServiceAlchemy, ITaskCommentService):
    '''
    Implementation for @see: ITaskCommentService
    '''

    def __init__(self):
        '''
        Construct the desk task comment service.
        '''
        EntityServiceAlchemy.__init__(self, TaskCommentMapped, QTaskComment)

    def getAll(self, taskId, userId=None, offset=None, limit=None, detailed=False, q=None):
        '''
        @see: ITaskCommentService.getAll
        '''
        sql = self.session().query(TaskCommentMapped)
        sql = sql.filter(TaskCommentMapped.Task == taskId)
        if userId:
            sql = sql.filter(TaskCommentMapped.User == userId)
        if q:
            sql = buildQuery(sql, q, TaskCommentMapped)
        sqlLimit = buildLimits(sql, offset, limit)
        if detailed: return IterPart(sqlLimit.all(), sql.count(), offset, limit)
        return sqlLimit.all()

    def insert(self, taskComment):
        '''
        @see: ITaskCommentService.insert
        '''
        assert isinstance(taskComment, TaskComment), 'Invalid task comment %s' % taskComment
        taskCommentDb = TaskCommentMapped()
        copy(taskComment, taskCommentDb, exclude=('CreatedOn', 'UpdatedOn',))

        taskCommentDb.CreatedOn = current_timestamp()
        taskCommentDb.UpdatedOn = taskCommentDb.CreatedOn

        try:
            self.session().add(taskCommentDb)
            self.session().flush((taskCommentDb,))

        except SQLAlchemyError as e:
            handle(e, taskCommentDb)

        taskComment.Id = taskCommentDb.Id
        return taskComment.Id

    def update(self, taskComment):
        '''
        @see: ITaskCommentService.update
        '''
        assert isinstance(taskComment, TaskComment), 'Invalid task comment %s' % taskComment
        taskCommentDb = self.session().query(TaskCommentMapped).get(taskComment.Id)
        if not taskCommentDb: raise InputError(Ref(_('Unknown task comment'), ref=TaskComment.Id))

        if TaskComment.Task in taskComment:
            if taskCommentDb.Task != taskComment.Task:
                raise InputError(Ref(_('Cannont change the task of task comment'), ref=TaskComment.Task))

        if TaskComment.User in taskComment:
            if taskCommentDb.User != taskComment.User:
                raise InputError(Ref(_('Cannont change the user of task comment'), ref=TaskComment.User))

        taskCommentDb.UpdatedOn = current_timestamp()

        try:
            self.session().flush((copy(taskComment, taskCommentDb, exclude=('Task', 'User', 'CreatedOn', 'UpdatedOn',)),))
        except SQLAlchemyError as e: handle(e, TaskCommentMapped)

