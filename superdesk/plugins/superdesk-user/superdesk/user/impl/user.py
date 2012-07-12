'''
Created on Mar 6, 2012

@package superdesk
@copyright 2011 Sourcefabric o.p.s.
@license http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mihai Balaceanu

@author: Mihai Balaceanu
'''

from superdesk.user.api.user import IUserService, QUser
from ally.container.ioc import injected
from sql_alchemy.impl.entity import EntityServiceAlchemy
from superdesk.user.meta.user import UserMapped
from ally.core.authentication.api.authentication import IAuthenticate, User
from ally.exception import InputError

# --------------------------------------------------------------------

@injected
class UserServiceAlchemy(EntityServiceAlchemy, IUserService, IAuthenticate):
    '''
    @see: IUserService
    '''
    def __init__(self):
        EntityServiceAlchemy.__init__(self, UserMapped, QUser)

    def getUserKey(self, userName):
        '''
        See IAuthenticate.getUserKey
        '''
        if not userName: raise InputError('Empty user name')
        q = QUser()
        q.name = userName
        u = self.getAll(0, 1, q)
        try:
            if isinstance(u, list): return u[0].Password
            else: return next(u).Password
        except (IndexError, StopIteration): raise InputError('Invalid user name %s' % userName)

    def getUserData(self, userName):
        '''
        See IAuthenticate.getUserKey
        '''
        if not userName: raise InputError('Empty user name')
        q = QUser()
        q.name = userName
        u = self.getAll(0, 1, q)
        try:
            if isinstance(u, list): ent = u[0]
            else: ent = next(u).Password
        except (IndexError, StopIteration): raise InputError('Invalid user name %s' % userName)
        user = User()
        user.UserName, user.FirstName, user.LastName, user.EMail, user.Address = \
        ent.Name, ent.FirstName, ent.LastName, ent.EMail, ent.Address
        return user
