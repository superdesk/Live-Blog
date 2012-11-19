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
from ally.api.criteria import AsLike

# --------------------------------------------------------------------

ALL_NAMES = (UserMapped.Name, UserMapped.FirstName, UserMapped.LastName, UserMapped.EMail)

@injected
@setup(IUserService)
class UserServiceAlchemy(SessionSupport, IUserService):
    '''
    @see: IUserService
    '''
    def __init__(self):
        '''
        Construct the service
        '''

    def getById(self, adminId, id):
        '''
        @see: IUserService.getById
        '''
        user = self.session().query(UserMapped).get(id)
        if not user or user.DeletedOn is not None:
            assert isinstance(user, UserMapped), 'Invalid user %s' % user
            raise InputError(Ref(_('Unknown user id'), ref=User.Id))
        return user

    def getAll(self, adminId, offset=None, limit=None, detailed=False, q=None):
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
                if QUser.all in q:
                    filter = None
                    if AsLike.like in q.all:
                        for col in ALL_NAMES:
                            filter = col.like(q.all.like) if filter is None else filter | col.like(q.all.like)
                    elif AsLike.ilike in q.all:
                        for col in ALL_NAMES:
                            filter = col.ilike(q.all.ilike) if filter is None else filter | col.ilike(q.all.ilike)
                    sql = sql.filter(filter)

            if entities is None: entities = buildLimits(sql, offset, limit).all()
            if detailed: return IterPart(entities, sql.count(), offset, limit)
        return entities

    def insert(self, adminId, user):
        '''
        @see: IUserService.insert
        '''
        assert isinstance(user, User), 'Invalid user %s' % user

        sql = self.session().query(UserMapped)
        sql = sql.filter(UserMapped.Name == user.Name)
        sql = sql.filter(UserMapped.DeletedOn == None)
        if sql.count() > 0: raise InputError(Ref(_('There is already a user with this name'), ref=User.Name))

        userDb = UserMapped()
        userDb.password = user.Password
        userDb.CreatedOn = current_timestamp()
        try:
            self.session().add(copy(user, userDb))
            self.session().flush((userDb,))
        except SQLAlchemyError as e: handle(e, userDb)
        user.Id = userDb.Id
        return user.Id

    def update(self, adminId, user):
        '''
        @see: IUserService.update
        '''
        assert isinstance(user, User), 'Invalid user %s' % user

        userDb = self.session().query(UserMapped).get(user.Id)
        if not userDb or userDb.DeletedOn is not None:
            assert isinstance(userDb, UserMapped), 'Invalid user %s' % userDb
            raise InputError(Ref(_('Unknown user id'), ref=User.Id))
        try:
            sql = self.session().query(UserMapped)
            sql = sql.filter(UserMapped.Id != user.Id)
            sql = sql.filter(UserMapped.Name == user.Name)
            sql = sql.filter(UserMapped.DeletedOn == None)
            if sql.count() > 0: raise InputError(Ref(_('There is already a user with this name'), ref=User.Name))
            
            self.session().flush((copy(user, userDb),))
        except SQLAlchemyError as e: handle(e, userDb)
        return True

    def delete(self, adminId, id):
        '''
        @see: IUserService.delete
        '''
        userDb = self.session().query(UserMapped).get(id)
        if not userDb or userDb.DeletedOn is not None: return False
        assert isinstance(userDb, UserMapped), 'Invalid user %s' % userDb
        userDb.DeletedOn = current_timestamp()
        self.session().merge(userDb)
        return True
    
    def changePassword(self, adminId, user):
        '''
        @see: IUserService.changePassword
        '''
        userDb = self.session().query(UserMapped).get(user.Id)
        if not userDb or userDb.DeletedOn is not None:
            assert isinstance(userDb, UserMapped), 'Invalid user %s' % userDb
            raise InputError(Ref(_('Unknown user id'), ref=User.Id))
        try:
            userDb.password = user.Password
            self.session().flush((userDb, ))
        except SQLAlchemyError as e: handle(e, userDb)  

