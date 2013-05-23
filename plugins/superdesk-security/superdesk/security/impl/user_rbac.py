'''
Created on Jan 21, 2013

@package: superdesk security
@copyright 2011 Sourcefabric o.p.s.
@license http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Implementation for user RBAC.
'''

from ally.api.extension import IterPart
from ally.container import wire
from ally.container.ioc import injected
from ally.container.support import setup
from ally.support.sqlalchemy.session import SessionSupport
from ally.support.sqlalchemy.util_service import buildQuery, buildLimits
from security.api.right import QRight
from security.meta.right import RightMapped
from security.rbac.api.rbac import QRole
from security.rbac.core.spec import IRbacService
from security.rbac.meta.rbac import RoleMapped
from security.rbac.meta.rbac_intern import RbacRole, RbacRight
from sqlalchemy.orm.exc import NoResultFound
from superdesk.security.api.user_rbac import IUserRbacService
from superdesk.security.core.spec import IUserRbacSupport
from superdesk.security.meta.security_intern import RbacUser

# --------------------------------------------------------------------

@injected
@setup(IUserRbacService, IUserRbacSupport, name='userRbacService')
class UserRbacServiceAlchemy(SessionSupport, IUserRbacService, IUserRbacSupport):
    '''
    Implementation for @see: IUserRbacService
    '''
    
    rbacService = IRbacService; wire.entity('rbacService')
    # Rbac service to use for complex role operations.
    
    def __init__(self):
        assert isinstance(self.rbacService, IRbacService), 'Invalid rbac service %s' % self.rbacService
    
    def getRoles(self, userId, offset=None, limit=None, detailed=False, q=None):
        '''
        @see: IUserRbacService.getRoles
        '''
        if limit == 0: entities = ()
        else: entities = None
        if detailed or entities is None:
            rbacId = self.rbacIdFor(userId)
            if not rbacId: return IterPart((), 0, offset, limit) if detailed else ()
            
            sql = self.rbacService.rolesForRbacSQL(rbacId)
            if q:
                assert isinstance(q, QRole), 'Invalid query %s' % q
                sql = buildQuery(sql, q, RoleMapped)
            if entities is None: entities = buildLimits(sql, offset, limit).all()
            if detailed: return IterPart(entities, sql.count(), offset, limit)
        return entities
        
    def getRights(self, userId, typeId=None, offset=None, limit=None, detailed=False, q=None):
        '''
        @see: IUserRbacService.getRights
        '''
        if limit == 0: entities = ()
        else: entities = None
        if detailed or entities is None:
            rbacId = self.rbacIdFor(userId)
            if not rbacId: return IterPart((), 0, offset, limit) if detailed else ()
            
            sql = self.rbacService.rightsForRbacSQL(rbacId)
            if typeId: sql = sql.filter(RightMapped.Type == typeId)
            if q:
                assert isinstance(q, QRight), 'Invalid query %s' % q
                sql = buildQuery(sql, q, RightMapped)
            if entities is None: entities = buildLimits(sql, offset, limit).all()
            if detailed: return IterPart(entities, sql.count(), offset, limit)
        return entities

    def assignRole(self, userId, roleId):
        '''
        @see: IUserRbacService.assignRole
        '''
        rbacId = self.rbacIdFor(userId)
        if not rbacId: rbacId = self._rbacCreate(userId)
        else:
            sql = self.session().query(RbacRole).filter(RbacRole.rbac == rbacId).filter(RbacRole.role == roleId)
            if sql.count() > 0: return  # The role is already mapped to user
        self.session().add(RbacRole(rbac=rbacId, role=roleId))
    
    def unassignRole(self, userId, roleId):
        '''
        @see: IUserRbacService.unassignRole
        '''
        rbacId = self.rbacIdFor(userId)
        if not rbacId: return False
        sql = self.session().query(RbacRole).filter(RbacRole.rbac == rbacId).filter(RbacRole.role == roleId)
        return sql.delete() > 0
        
    def assignRight(self, userId, rightId):
        '''
        @see: IUserRbacService.assignRight
        '''
        rbacId = self.rbacIdFor(userId)
        if not rbacId: rbacId = self._rbacCreate(userId)
        else:
            sql = self.session().query(RbacRight).filter(RbacRight.rbac == rbacId).filter(RbacRight.right == rightId)
            if sql.count() > 0: return  # The right is already mapped to user
        self.session().add(RbacRight(rbac=rbacId, right=rightId))
    
    def unassignRight(self, userId, rightId):
        '''
        @see: IUserRbacService.unassignRight
        '''
        rbacId = self.rbacIdFor(userId)
        if not rbacId: return False
        sql = self.session().query(RbacRight).filter(RbacRight.rbac == rbacId).filter(RbacRight.right == rightId)
        return sql.delete() > 0
        
    # ----------------------------------------------------------------
    
    def rbacIdFor(self, userId):
        '''
        @see: IUserRbacSupport.rbacIdFor
        '''
        try: rbacId, = self.session().query(RbacUser.Id).filter(RbacUser.userId == userId).one()
        except NoResultFound: return
        return rbacId
    
    # ----------------------------------------------------------------
    
    def _rbacCreate(self, userId):
        '''
        Provides the rbac id for the user id, optionally generate one.
        '''
        rbacUser = RbacUser(userId=userId)
        self.session().add(rbacUser)
        self.session().flush((rbacUser,))
        return rbacUser.Id
