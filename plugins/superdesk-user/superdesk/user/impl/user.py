'''
Created on Mar 6, 2012

@package: superdesk user
@copyright: 2011 Sourcefabric o.p.s.
@license http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mihai Balaceanu

Implementation for user services.
'''

from ally.api.criteria import AsLike, AsBoolean
from ally.api.extension import IterPart
from ally.container import wire
from ally.container.ioc import injected
from ally.container.support import setup
from ally.exception import InputError, Ref
from ally.internationalization import _
from ally.support.api.util_service import copy
from ally.support.sqlalchemy.session import SessionSupport
from ally.support.sqlalchemy.util_service import handle, buildQuery, buildLimits
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.sql.functions import current_timestamp
from superdesk.user.api.user import IUserService, QUser, User, Password
from superdesk.user.meta.user import UserMapped
from superdesk.user.meta.user_type import UserTypeMapped
from uuid import uuid4

# --------------------------------------------------------------------

ALL_NAMES = (UserMapped.Name, UserMapped.FirstName, UserMapped.LastName, UserMapped.EMail, UserMapped.PhoneNumber)

@injected
@setup(IUserService, name='userService')
class UserServiceAlchemy(SessionSupport, IUserService):
    '''
    @see: IUserService
    '''
    default_user_type_key = 'standard'; wire.config('default_user_type_key', doc='''
    Default user type for users without specified the user type key''')

    def __init__(self):
        '''
        Construct the service
        '''

    def getById(self, id):
        '''
        @see: IUserService.getById
        '''
        user = self.session().query(UserMapped).get(id)
        if not user: raise InputError(Ref(_('Unknown user id'), ref=User.Id))
        assert isinstance(user, UserMapped), 'Invalid user %s' % user
        return user
    
    def getByUuid(self, uuid):
        '''
        @see: IUserService.getByUuid
        '''
        sql = self.session().query(UserMapped)
        sql = sql.filter(UserMapped.Uuid == uuid)
        user = sql.one()
        
        assert isinstance(user, UserMapped), 'Invalid user %s' % user
        return user

    def getAll(self, offset=None, limit=None, detailed=False, q=None):
        '''
        @see: IUserService.getAll
        '''
        if limit == 0: entities = ()
        else: entities = None
        if detailed or entities is None:
            sql = self.session().query(UserMapped)

            activeUsers = True
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

                if (QUser.inactive in q) and (AsBoolean.value in q.inactive):
                        activeUsers = not q.inactive.value

            sql = sql.filter(UserMapped.Active == activeUsers)
            sql = sql.filter(UserMapped.Type == self.default_user_type_key)

            if entities is None: entities = buildLimits(sql, offset, limit).all()
            if detailed: return IterPart(entities, sql.count(), offset, limit)
        return entities

    def insert(self, user):
        '''
        @see: IUserService.insert
        '''
        assert isinstance(user, User), 'Invalid user %s' % user
        
        if user.Uuid is None: user.Uuid= str(uuid4().hex)
        if user.Cid is None: user.Cid = 0    

        userDb = UserMapped()
        userDb.password = user.Password
        userDb.CreatedOn = current_timestamp()
        userDb.typeId = self._userTypeId(user.Type)
        try:
            self.session().add(copy(user, userDb, exclude=('Type',)))
            self.session().flush((userDb,))
        except SQLAlchemyError as e: handle(e, userDb)
        user.Id = userDb.Id
        return user.Id

    def update(self, user):
        '''
        @see: IUserService.update
        Should not this be handeled automatically via entity service?
        '''
        assert isinstance(user, User), 'Invalid user %s' % user

        userDb = self.session().query(UserMapped).get(user.Id)
        if not userDb:
            assert isinstance(userDb, UserMapped), 'Invalid user %s' % userDb
            raise InputError(Ref(_('Unknown user id'), ref=User.Id))
        try:
            if user.Type: userDb.typeId = self._userTypeId(user.Type)
            userDb.Cid = userDb.Cid if userDb.Cid else 0
            userDb.Cid = user.Cid if user.Cid else userDb.Cid + 1
            self.session().flush((copy(user, userDb, exclude=('Type', 'CId')),))
        except SQLAlchemyError as e: handle(e, userDb)

    def delete(self, id):
        '''
        @see: IUserService.delete
        '''
        userDb = self.session().query(UserMapped).get(id)
        if not userDb or not userDb.Active: return False
        assert isinstance(userDb, UserMapped), 'Invalid user %s' % userDb
        userDb.Active = False
        self.session().merge(userDb)
        return True
   
    def changePassword(self, id, password):
        '''
        @see: IUserService.changePassword
        '''
        assert isinstance(password, Password), 'Invalid password change %s' % password
        try: userDb = self.session().query(UserMapped).filter(UserMapped.Id == id).one() #.filter(UserMapped.password == password.OldPassword).one()
        except NoResultFound: userDb = None
        
        if not userDb:
            assert isinstance(userDb, UserMapped), 'Invalid user %s' % userDb
            raise InputError(Ref(_('Invalid user id or old password'), ref=User.Id))
        
        try:
            userDb.password = password.NewPassword
            self.session().flush((userDb,))
        except SQLAlchemyError as e: handle(e, userDb)

    # ----------------------------------------------------------------

    def _userTypeId(self, key):
        '''
        Provides the user type id that has the provided key.
        '''
        if not key: key = self.default_user_type_key

        try:
            sql = self.session().query(UserTypeMapped.id).filter(UserTypeMapped.Key == key)
            return sql.one()[0]
        except NoResultFound:
            raise InputError(Ref(_('Invalid user type %(userType)s') % dict(userType=key), ref=User.Type))

