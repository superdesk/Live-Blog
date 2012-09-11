'''
Created on Mar 6, 2012

@package: superdesk user
@copyright: 2011 Sourcefabric o.p.s.
@license http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mihai Balaceanu

Implementation for user services.
'''

from ally.container.ioc import injected
from ally.container.support import setup
from ally.exception import InputError, Ref
from ally.support.api.util_service import copy
from ally.support.sqlalchemy.util_service import handle
from sql_alchemy.impl.entity import EntityServiceAlchemy
from sqlalchemy.exc import SQLAlchemyError
from superdesk.user.api.user import IUserService, QUser, User
from superdesk.user.meta.user import UserMapped

# --------------------------------------------------------------------

@injected
@setup(IUserService)
class UserServiceAlchemy(EntityServiceAlchemy, IUserService):
    '''
    @see: IUserService
    '''
    def __init__(self):
        EntityServiceAlchemy.__init__(self, UserMapped, QUser)

    def insert(self, user):
        '''
        @see: IUserService.insert
        '''
        assert isinstance(user, User), 'Invalid user %s' % user

        userDb = UserMapped()
        userDb.password = user.Password
        try:
            self.session().add(copy(user, userDb))
            self.session().flush((userDb,))
        except SQLAlchemyError as e: handle(e, userDb)
        user.Id = userDb.Id
        return user.Id

        user.password = user.Password # We set the password value.
        return super().insert(user)

    def update(self, user):
        '''
        @see: IUserService.update
        '''
        assert isinstance(user, User), 'Invalid user %s' % user

        userDb = self.session().query(UserMapped).get(user.Id)
        if not userDb: raise InputError(Ref(_('Unknown id'), ref=UserMapped.Id))
        try:
            self.session().flush((copy(user, userDb),))
        except SQLAlchemyError as e: handle(e, userDb)

