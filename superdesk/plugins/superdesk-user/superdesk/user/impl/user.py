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
from ally.support.sqlalchemy.util_service import handle, buildQuery, buildLimits
from sqlalchemy.exc import SQLAlchemyError
from superdesk.user.api.user import IUserService, QUser, User
from superdesk.user.meta.user import UserMapped
from sqlalchemy.sql.functions import current_timestamp
from ally.support.sqlalchemy.session import SessionSupport
from ally.api.extension import IterPart
from ally.internationalization import _

# --------------------------------------------------------------------

@injected
@setup(IUserService)
class UserServiceAlchemy(SessionSupport, IUserService):
    '''
    @see: IUserService
    '''
    def __init__(self):
        SessionSupport.__init__(self)

    def getById(self, id):
        '''
        @see: IUserService.getById
        '''
        user = self.session().query(UserMapped).get(id)
        if not user or user.DeletedOn is not None:
            assert isinstance(user, UserMapped), 'Invalid user %s' % user
            raise InputError(Ref(_('Unknown user id'), ref=User.Id))
        return user

    def getAll(self, offset=None, limit=None, detailed=False, q=None):
        '''
        @see: IUserService.getAll
        '''
        if limit == 0: entities = ()
        else: entities = None
        if detailed or entities is None:
            sql = self.session().query(UserMapped)
            sql = sql.filter(UserMapped.DeletedOn == None)
            if q:
                assert isinstance(q, QUser), 'Invalid query %s' % q
                sql = buildQuery(sql, q, UserMapped)
            if entities is None: entities = buildLimits(sql, offset, limit).all()
            return IterPart(entities, sql.count(), offset, limit)
        return entities

    def insert(self, user):
        '''
        @see: IUserService.insert
        '''
        assert isinstance(user, User), 'Invalid user %s' % user

        userDb = UserMapped()
        userDb.password = user.Password
        userDb.CreatedOn = current_timestamp()
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
        if not userDb or userDb.DeletedOn is not None:
            assert isinstance(userDb, UserMapped), 'Invalid user %s' % userDb
            raise InputError(Ref(_('Unknown user id'), ref=User.Id))
        try:
            self.session().flush((copy(user, userDb),))
        except SQLAlchemyError as e: handle(e, userDb)

    def delete(self, id):
        '''
        @see: IUserService.delete
        '''
        userDb = self.session().query(UserMapped).get(id)
        if not userDb or userDb.DeletedOn is not None: return False
        assert isinstance(userDb, UserMapped), 'Invalid user %s' % userDb
        userDb.DeletedOn = current_timestamp()
        self.session().merge(userDb)
        return True


