'''
Created on Jan 21, 2013

@package: superdesk security
@copyright 2011 Sourcefabric o.p.s.
@license http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Implementation for user RBAC.
'''

from ..meta.user_rbac import RbacUserMapped
from acl.core.spec import IAclPermissionProvider
from ally.api.error import IdError
from ally.container.ioc import injected
from ally.container.support import setup
from security.rbac.core.impl.rbac import RbacServiceAlchemy
from security.rbac.meta.rbac import Rbac
from sql_alchemy.support.mapper import tableFor
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.sql.expression import insert
from superdesk.security.api.user_rbac import IUserRbacService
from superdesk.user.meta.user import UserMapped
from ally.container import wire

# --------------------------------------------------------------------

@injected
@setup(IUserRbacService, name='userRbacService')
class UserRbacServiceAlchemy(RbacServiceAlchemy, IAclPermissionProvider, IUserRbacService):
    '''
    Implementation for @see: IUserRbacService
    '''
    
    aclPermissionRightsProvider = IAclPermissionProvider; wire.entity('aclPermissionRightsProvider')
    
    def __init__(self):
        assert isinstance(self.aclPermissionRightsProvider, IAclPermissionProvider), \
        'Invalid acl permission provider %s' % self.aclPermissionRightsProvider
        RbacServiceAlchemy.__init__(self, RbacUserMapped)
    
    def obtainRbacId(self, identifier):
        '''
        @see: RbacServiceAlchemy.obtainRbacId
        '''
        assert isinstance(identifier, int), 'Invalid user id %s' % identifier
        sql = self.session().query(RbacUserMapped.rbacId)
        sql = sql.filter(RbacUserMapped.userId == identifier)
        try: rbacUserId, = sql.one()
        except NoResultFound:
            sql = self.session().query(UserMapped.userId)
            sql = sql.filter(UserMapped.userId == identifier)
            if not sql.count(): raise IdError(UserMapped)
            
            rbac = Rbac()
            self.session().add(rbac)
            self.session().flush((rbac,))
            rbacUserId = rbac.id
            self.session().execute(insert(tableFor(RbacUserMapped), {RbacUserMapped.userId: identifier,
                                                                     RbacUserMapped.rbacId: rbacUserId}))
            
        return rbacUserId

    # ----------------------------------------------------------------
    
    def iteratePermissions(self, acl):
        '''
        @see: IAclPermissionProvider.iteratePermissions
        '''
        rbacId = self.findRbacId(acl)
        if rbacId is None: return ()
        return self.aclPermissionRightsProvider.iteratePermissions(self.sqlRights(rbacId))
