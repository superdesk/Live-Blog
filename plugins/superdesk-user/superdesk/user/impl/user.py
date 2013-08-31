'''
Created on Mar 6, 2012

@package: superdesk user
@copyright: 2011 Sourcefabric o.p.s.
@license http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mihai Balaceanu

Implementation for user services.
'''

from ally.api.criteria import AsLike, AsBoolean
from ally.api.error import InputError
from ally.container import wire
from ally.container.ioc import injected
from ally.container.support import setup
from ally.internationalization import _
from functools import reduce
from sql_alchemy.impl.entity import EntityServiceAlchemy
from sql_alchemy.support.util_service import insertModel
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.sql.expression import or_
from superdesk.user.api.user import IUserService, QUser, User, Password
from superdesk.user.meta.user import UserMapped

# --------------------------------------------------------------------

@injected
@setup(IUserService, name='userService')
class UserServiceAlchemy(EntityServiceAlchemy, IUserService):
    '''
    Implementation for @see: IUserService
    '''
    default_user_type_key = 'standard'; wire.config('default_user_type_key', doc='''
    Default user type for users without specified the user type key''')
    allNames = {UserMapped.Name, UserMapped.FirstName, UserMapped.LastName, UserMapped.EMail, UserMapped.PhoneNumber}

    def __init__(self):
        '''
        Construct the service
        '''
        assert isinstance(self.default_user_type_key, str), 'Invalid default user type %s' % self.default_user_type_key
        assert isinstance(self.allNames, set), 'Invalid all name %s' % self.allNames
        EntityServiceAlchemy.__init__(self, UserMapped, QUser, all=self.queryAll, inactive=self.queryInactive)

    def getAll(self, q=None, **options):
        '''
        @see: IUserService.getAll
        '''
        if q is None: q = QUser(inactive=False)
        elif QUser.inactive not in q: q.inactive = False
        # Making sure that the default query is for active.
        return super().getAll(q, **options)

    def insert(self, user):
        '''
        @see: IUserService.insert
        '''
        assert isinstance(user, User), 'Invalid user %s' % user
        userDb = insertModel(UserMapped, user, password=user.Password)
        assert isinstance(userDb, UserMapped), 'Invalid user %s' % userDb
        return userDb.Id

    def delete(self, id):
        '''
        @see: IUserService.delete
        '''
        userDb = self.session().query(UserMapped).get(id)
        if not userDb or not userDb.Active: return False
        assert isinstance(userDb, UserMapped), 'Invalid user %s' % userDb
        userDb.Active = False
        return True
   
    def changePassword(self, id, password):
        '''
        @see: IUserService.changePassword
        '''
        assert isinstance(password, Password), 'Invalid password change %s' % password
        try: userDb = self.session().query(UserMapped).filter(UserMapped.Id == id).one() 
        # TODO: check why the old password is not verified. .filter(UserMapped.password == password.OldPassword).one()
        except NoResultFound: raise InputError(_('Invalid user or old password'))
        assert isinstance(userDb, UserMapped), 'Invalid user %s' % userDb
        
        userDb.password = password.NewPassword

    # ----------------------------------------------------------------
    
    def queryAll(self, sql, crit):
        '''
        Processes the all query.
        '''
        assert isinstance(crit, AsLike), 'Invalid criteria %s' % crit
        filters = []
        if AsLike.like in crit:
            for col in self.allNames: filters.append(col.like(crit.like))
        elif AsLike.ilike in crit:
            for col in self.allNames: filters.append(col.ilike(crit.ilike))
        sql = sql.filter(reduce(or_, filters))
        return sql
            
    def queryInactive(self, sql, crit):
        '''
        Processes the inactive query.
        '''
        assert isinstance(crit, AsBoolean), 'Invalid criteria %s' % crit
        return sql.filter(UserMapped.Active == (crit.value is False))
