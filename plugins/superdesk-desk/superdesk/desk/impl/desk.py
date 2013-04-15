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
from ally.support.sqlalchemy.util_service import buildLimits
from ally.api.extension import IterPart
from sql_alchemy.impl.entity import EntityServiceAlchemy
from superdesk.user.meta.user import UserMapped

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
        EntityServiceAlchemy.__init__(self, DeskMapped)

    def listUsers(self, deskId, orderBy=None, offset=None, limit=None, detailed=False):
        '''
        @see: IDeskService.listUsers
        '''

        sql = self.session().query(UserMapped).join(DeskUserMapped)
        sql = sql.filter(DeskUserMapped.desk == deskId)
        if orderBy == 'name':
            sql = sql.order_by(UserMapped.Name)
        if orderBy == 'id':
            sql = sql.order_by(UserMapped.Id)

        entities = buildLimits(sql, offset, limit).all()
        if detailed: return IterPart(entities, sql.count(), offset, limit)

        return entities

    def attachUser(self, deskId, userId):
        # TODO: Martin: the UPDATE function are not mandatory to return something, so you can remove the bool and just not return anything,
        # thus you avoid the return True.
        '''
        @see IDeskService.attachUser
        '''
        sql = self.session().query(DeskUserMapped)
        sql = sql.filter(DeskUserMapped.desk == deskId)
        sql = sql.filter(DeskUserMapped.user == userId)
        if sql.count() == 1: return True

        desk_user = DeskUserMapped()
        desk_user.desk = deskId
        desk_user.user = userId

        self.session().add(desk_user)
        self.session().flush((desk_user,))

        return True

    def detachUser(self, deskId, userId):
        '''
        @see IDeskService.detachUser
        '''
        sql = self.session().query(DeskUserMapped)
        sql = sql.filter(DeskUserMapped.desk == deskId)
        sql = sql.filter(DeskUserMapped.user == userId)
        sql.delete()
        # TODO: Martin: should be sql.delete() > 0 in order to validate if something has been deleted.
        return True

