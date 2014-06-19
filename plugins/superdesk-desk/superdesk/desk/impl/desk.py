'''
Created on April 2, 2013

@package: superdesk desk
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Martin Saturka

Contains the SQL alchemy implementation for desk API.
'''

from ..api.desk import IDeskService, QDesk
from ..meta.desk import DeskMapped, DeskUser, DeskTaskType
from ..meta.task_type import TaskTypeMapped
from ally.container.ioc import injected
from ally.container.support import setup
from sql_alchemy.support.util_service import buildLimits, buildQuery
from ally.api.extension import IterPart
from sql_alchemy.impl.entity import EntityServiceAlchemy
from superdesk.user.meta.user import UserMapped
from sqlalchemy.sql.expression import not_
from sqlalchemy.orm.exc import NoResultFound
from ally.api.error import InputError

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

        sql = self.session().query(UserMapped).join(DeskUser)
        sql = sql.filter(DeskUser.desk == deskId)
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
        sql = sql.filter(not_(UserMapped.Id.in_(self.session().query(DeskUser.user).filter(DeskUser.desk == deskId).subquery())))
        if q:
            sql = buildQuery(sql, q, UserMapped)

        entities = buildLimits(sql, offset, limit).all()
        if detailed: return IterPart(entities, sql.count(), offset, limit)

        return entities

    def attachUser(self, deskId, userId):
        '''
        @see IDeskService.attachUser
        '''
        sql = self.session().query(DeskUser)
        sql = sql.filter(DeskUser.desk == deskId)
        sql = sql.filter(DeskUser.user == userId)
        if sql.count() == 1: return

        deskUser = DeskUser()
        deskUser.desk = deskId
        deskUser.user = userId

        self.session().add(deskUser)
        self.session().flush((deskUser,))

    def detachUser(self, deskId, userId):
        '''
        @see IDeskService.detachUser
        '''
        sql = self.session().query(DeskUser)
        sql = sql.filter(DeskUser.desk == deskId)
        sql = sql.filter(DeskUser.user == userId)
        count_del = sql.delete()

        return (0 < count_del)

    def getTaskTypes(self, deskId, offset=None, limit=None, detailed=False):
        '''
        @see: IDeskService.getTaskTypes
        '''

        sql = self.session().query(TaskTypeMapped).join(DeskTaskType)
        sql = sql.filter(DeskTaskType.desk == deskId)

        entities = buildLimits(sql, offset, limit).all()
        if detailed: return IterPart(entities, sql.count(), offset, limit)

        return entities
    
    def getUnassignedTaskTypes(self, deskId, offset=None, limit=None, detailed=False):
        '''
        @see: IDeskService.getUnassignedTaskTypes
        '''
        sqlDesk = self.session().query(DeskTaskType.taskType)
        sqlDesk = sqlDesk.filter(DeskTaskType.desk == deskId)
        
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
        
        sql = self.session().query(DeskTaskType)
        sql = sql.filter(DeskTaskType.desk == deskId)
        sql = sql.filter(DeskTaskType.taskType == taskTypeId)
        if sql.count() == 1: return

        deskTaskType = DeskTaskType()
        deskTaskType.desk = deskId
        deskTaskType.taskType = taskTypeId

        self.session().add(deskTaskType)
        self.session().flush((deskTaskType,))


    def detachTaskType(self, deskId, taskTypeKey):
        '''
        @see IDeskService.detachUser
        '''
        taskTypeId = self._typeId(taskTypeKey)
        
        sql = self.session().query(DeskTaskType)
        sql = sql.filter(DeskTaskType.desk == deskId)
        sql = sql.filter(DeskTaskType.taskType == taskTypeId)
        count_del = sql.delete()

        return (0 < count_del)
    
    def _typeId(self, key):
        '''
        Provides the task type id that has the provided key.
        '''
        try:
            sql = self.session().query(TaskTypeMapped.id).filter(TaskTypeMapped.Name == key)
            return sql.one()[0]
        except NoResultFound:
            raise InputError('Invalid task type %(type)s') % dict(type=key)       
