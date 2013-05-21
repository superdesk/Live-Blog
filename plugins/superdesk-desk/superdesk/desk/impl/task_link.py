'''
Created on April 2, 2013

@package: superdesk desk
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Martin Saturka

Contains the SQL alchemy implementation for desk task API.
'''

from ..api.task_link import ITaskLinkService, TaskLink, QTaskLink
from ..meta.task_link import TaskLinkMapped
from ..meta.task_link_type import TaskLinkTypeMapped
from ally.container.ioc import injected
from ally.container.support import setup
from ally.exception import InputError, Ref
from ally.internationalization import _
from ally.support.api.util_service import copy
from ally.support.sqlalchemy.util_service import buildQuery, buildLimits, handle
from sql_alchemy.impl.entity import EntityServiceAlchemy
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.sql.expression import or_
from ally.api.extension import IterPart

# --------------------------------------------------------------------

@injected
@setup(ITaskLinkService, name='taskLinkService')
class TaskLinkServiceAlchemy(EntityServiceAlchemy, ITaskLinkService):
    '''
    Implementation for @see: ITaskLinkService
    '''

    def __init__(self):
        '''
        Construct the desk task link service.
        '''
        EntityServiceAlchemy.__init__(self, TaskLinkMapped, QTaskLink)

    def getAll(self, typeKey=None, offset=None, limit=None, detailed=False, q=None):
        '''
        @see: ITaskLinkService.getAll
        '''
        sql = self.session().query(TaskLinkMapped)
        if typeKey:
            sql = sql.join(TaskLinkTypeMapped).filter(TaskLinkTypeMapped.Key == typeKey)
        if q:
            sql = buildQuery(sql, q, TaskLinkMapped)
        sqlLimit = buildLimits(sql, offset, limit)
        if detailed: return IterPart(sqlLimit.all(), sql.count(), offset, limit)
        return sqlLimit.all()

    def getHead(self, headId, typeKey=None, offset=None, limit=None, detailed=False, q=None):
        '''
        @see: ITaskLinkService.getHead
        '''
        sql = self.session().query(TaskLinkMapped)
        sql = sql.filter(TaskLinkMapped.Head == headId)
        if typeKey:
            sql = sql.join(TaskLinkTypeMapped).filter(TaskLinkTypeMapped.Key == typeKey)
        if q:
            sql = buildQuery(sql, q, TaskLinkMapped)
        sqlLimit = buildLimits(sql, offset, limit)
        if detailed: return IterPart(sqlLimit.all(), sql.count(), offset, limit)
        return sqlLimit.all()

    def getTail(self, tailId, typeKey=None, offset=None, limit=None, detailed=False, q=None):
        '''
        @see: ITaskLinkService.getTail
        '''
        sql = self.session().query(TaskLinkMapped)
        sql = sql.filter(TaskLinkMapped.Tail == tailId)
        if typeKey:
            sql = sql.join(TaskLinkTypeMapped).filter(TaskLinkTypeMapped.Key == typeKey)
        if q:
            sql = buildQuery(sql, q, TaskLinkMapped)
        sqlLimit = buildLimits(sql, offset, limit)
        if detailed: return IterPart(sqlLimit.all(), sql.count(), offset, limit)
        return sqlLimit.all()

    def getSide(self, sideId, typeKey=None, offset=None, limit=None, detailed=False, q=None):
        '''
        @see: ITaskLinkService.getSide
        '''
        sql = self.session().query(TaskLinkMapped)
        sql = sql.filter(or_(TaskLinkMapped.Head == sideId, TaskLinkMapped.Tail == sideId))
        if typeKey:
            sql = sql.join(TaskLinkTypeMapped).filter(TaskLinkTypeMapped.Key == typeKey)
        if q:
            sql = buildQuery(sql, q, TaskLinkMapped)
        sqlLimit = buildLimits(sql, offset, limit)
        if detailed: return IterPart(sqlLimit.all(), sql.count(), offset, limit)
        return sqlLimit.all()

    def insert(self, taskLink):
        '''
        @see: ITaskLinkService.insert
        '''
        assert isinstance(taskLink, TaskLink), 'Invalid task link %s' % taskLink
        taskLinkDb = TaskLinkMapped()
        taskLinkDb.typeId = self._linkTypeId(taskLink.Type)

        copy(taskLink, taskLinkDb, exclude=('Type',))

        if taskLinkDb.Head == taskLinkDb.Tail:
            raise InputError(Ref(_('Can not link a task to itself'),))

        try:
            self.session().add(taskLinkDb)
            self.session().flush((taskLinkDb,))

        except SQLAlchemyError as e:
            handle(e, taskLinkDb)

        taskLink.Id = taskLinkDb.Id
        return taskLinkDb.Id

    def update(self, taskLink):
        '''
        @see: ITaskLinkService.update
        '''
        assert isinstance(taskLink, TaskLink), 'Invalid task link %s' % taskLink
        taskLinkDb = self.session().query(TaskLinkMapped).get(taskLink.Id)
        if not taskLinkDb: raise InputError(Ref(_('Unknown task link id'), ref=TaskLink.Id))
        if TaskLink.Type in taskLink: taskLinkDb.typeId = self._linkTypeId(taskLink.Type)

        copy(taskLink, taskLinkDb, exclude=('Type',))

        if taskLinkDb.Head == taskLinkDb.Tail:
            raise InputError(Ref(_('Can not link a task to itself'),))

        try:
            self.session().flush((taskLinkDb,))
        except SQLAlchemyError as e: handle(e, TaskLinkMapped)

    # ----------------------------------------------------------------

    def _linkTypeId(self, key):
        '''
        Provides the task link type id that has the provided key.
        '''
        try:
            sql = self.session().query(TaskLinkTypeMapped.id).filter(TaskLinkTypeMapped.Key == key)
            return sql.one()[0]
        except NoResultFound:
            raise InputError(Ref(_('Invalid task link type %(type)s') % dict(type=key), ref=TaskLink.Type))
