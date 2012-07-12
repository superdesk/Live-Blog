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
from ally.core.authentication.api.authentication import IAuthenticate
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
        q = QUser()
        q.name = userName
        u = self.getAll(0, 1, q)
        try: return next(u).Password
        except StopIteration: raise InputError('Invalid user name %s' % userName)
