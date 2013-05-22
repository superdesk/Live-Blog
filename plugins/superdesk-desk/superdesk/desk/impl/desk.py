'''
Created on April 2, 2013

@package: superdesk desk
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Martin Saturka

Contains the SQL alchemy implementation for desk API.
'''

from ..api.desk import IDeskService
from ..meta.desk import DeskMapped, DeskUserMapped
from ally.container.ioc import injected
from ally.container.support import setup
from ally.support.sqlalchemy.util_service import buildLimits, buildQuery
from ally.api.extension import IterPart
from sql_alchemy.impl.entity import EntityServiceAlchemy
from superdesk.user.meta.user import UserMapped
from sqlalchemy.sql.expression import not_
from superdesk.desk.meta.task_type import TaskTypeMapped
from superdesk.desk.meta.desk import DeskTaskTypeMapped
from superdesk.desk.api.desk import QDesk
from sqlalchemy.orm.exc import NoResultFound
from ally.exception import InputError

# --------------------------------------------------------------------

@injected
@setup(IDeskService, name='deskService')
class DeskServiceAlchemy(EntityServiceAlchemy, IDeskService):
    '''
    Implementation for @see: IDeskService
    '''

    def __init__(self):
        '''
        Construct the desk service.
        '''
        EntityServiceAlchemy.__init__(self, DeskMapped, QDesk)

    def getUsers(self, deskId, offset=None, limit=None, detailed=False, q=None):
        '''
        @see: IDeskService.getUsers
        '''

        sql = self.session().query(UserMapped).join(DeskUserMapped)
        sql = sql.filter(DeskUserMapped.desk == deskId)
        if q:
            sql = buildQuery(sql, q, UserMapped)

        entities = buildLimits(sql, offset, limit).all()
        if detailed: return IterPart(entities, sql.count(), offset, limit)

        return entities

    def getUnassignedUsers(self, deskId, offset=None, limit=None, detailed=False, q=None):
        '''
        @see: IDeskService.getUnassignedUsers
        '''
        sql = self.session().query(UserMapped)
        sql = sql.filter(not_(UserMapped.Id.in_(self.session().query(DeskUserMapped.user).filter(DeskUserMapped.desk == deskId).subquery())))
        if q:
            sql = buildQuery(sql, q, UserMapped)

        entities = buildLimits(sql, offset, limit).all()
        if detailed: return IterPart(entities, sql.count(), offset, limit)

        return entities

    def attachUser(self, deskId, userId):
        '''
        @see IDeskService.attachUser
        '''
        sql = self.session().query(DeskUserMapped)
        sql = sql.filter(DeskUserMapped.desk == deskId)
        sql = sql.filter(DeskUserMapped.user == userId)
        if sql.count() == 1: return

        deskUser = DeskUserMapped()
        deskUser.desk = deskId
        deskUser.user = userId

        self.session().add(deskUser)
        self.session().flush((deskUser,))

    def detachUser(self, deskId, userId):
        '''
        @see IDeskService.detachUser
        '''
        sql = self.session().query(DeskUserMapped)
        sql = sql.filter(DeskUserMapped.desk == deskId)
        sql = sql.filter(DeskUserMapped.user == userId)
        count_del = sql.delete()

        return (0 < count_del)

    def getTaskTypes(self, deskId, offset=None, limit=None, detailed=False):
        '''
        @see: IDeskService.getTaskTypes
        '''

        sql = self.session().query(TaskTypeMapped).join(DeskTaskTypeMapped)
        sql = sql.filter(DeskTaskTypeMapped.desk == deskId)

        entities = buildLimits(sql, offset, limit).all()
        if detailed: return IterPart(entities, sql.count(), offset, limit)

        return entities
    
    def getUnassignedTaskTypes(self, deskId, offset=None, limit=None, detailed=False):
        '''
        @see: IDeskService.getUnassignedTaskTypes
        '''
        sqlDesk = self.session().query(DeskTaskTypeMapped.taskType)
        sqlDesk = sqlDesk.filter(DeskTaskTypeMapped.desk == deskId)
        
        sql = self.session().query(TaskTypeMapped)
        sql = sql.filter(not_(TaskTypeMapped.id.in_(sqlDesk.subquery())))

        entities = buildLimits(sql, offset, limit).all()
        if detailed: return IterPart(entities, sql.count(), offset, limit)

        return entities
    
    def attachTaskType(self, deskId, taskTypeKey):
        '''
        @see IDeskService.attachTaskType
        '''
        taskTypeId = self._typeId(taskTypeKey)
        
        sql = self.session().query(DeskTaskTypeMapped)
        sql = sql.filter(DeskTaskTypeMapped.desk == deskId)
        sql = sql.filter(DeskTaskTypeMapped.taskType == taskTypeId)
        if sql.count() == 1: return

        deskTaskType = DeskTaskTypeMapped()
        deskTaskType.desk = deskId
        deskTaskType.taskType = taskTypeId

        self.session().add(deskTaskType)
        self.session().flush((deskTaskType,))


    def detachTaskType(self, deskId, taskTypeKey):
        '''
        @see IDeskService.detachUser
        '''
        taskTypeId = self._typeId(taskTypeKey)
        
        sql = self.session().query(DeskTaskTypeMapped)
        sql = sql.filter(DeskTaskTypeMapped.desk == deskId)
        sql = sql.filter(DeskTaskTypeMapped.taskType == taskTypeId)
        count_del = sql.delete()

        return (0 < count_del)
    
    def _typeId(self, key):
        '''
        Provides the task type id that has the provided key.
        '''
        try:
            sql = self.session().query(TaskTypeMapped.id).filter(TaskTypeMapped.Key == key)
            return sql.one()[0]
        except NoResultFound:
            raise InputError('Invalid task type %(type)s') % dict(type=key)       