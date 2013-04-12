'''
Created on Dec 21, 2012

@package: security - role based access control
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

RBAC implementation for roles.
'''

from ally.api.extension import IterPart
from ally.container import wire
from ally.container.ioc import injected
from ally.container.support import setup
from ally.exception import InputError, Ref
from ally.internationalization import _
from ally.support.sqlalchemy.util_service import buildQuery, buildLimits
from security.api.right import QRight
from security.meta.right import RightMapped
from security.rbac.api.rbac import IRoleService, QRole, Role
from security.rbac.core.spec import IRbacService
from security.rbac.meta.rbac import RoleMapped
from security.rbac.meta.rbac_intern import RbacRight
from sql_alchemy.impl.entity import EntityServiceAlchemy
from sqlalchemy.orm.exc import NoResultFound

# --------------------------------------------------------------------
    
@injected
@setup(IRoleService, name='roleService')
class RoleServiceAlchemy(EntityServiceAlchemy, IRoleService):
    '''
    Implementation for @see: IRoleService
    '''
    
    rbacService = IRbacService; wire.entity('rbacService')
    # Rbac service to use for complex role operations.
    
    def __init__(self):
        assert isinstance(self.rbacService, IRbacService), 'Invalid rbac service %s' % self.rbacService
        EntityServiceAlchemy.__init__(self, RoleMapped, QRole)
        
    def getByName(self, name):
        '''
        @see: IRoleService.getByName
        '''
        try: return self.session().query(RoleMapped).filter(RoleMapped.Name == name).one()
        except NoResultFound: raise InputError(Ref(_('Unknown name'), ref=Role.Name))
    
    def getRoles(self, roleId, offset=None, limit=None, detailed=False, q=None):
        '''
        @see: IRoleService.getRoles
        '''
        sql = self.rbacService.rolesForRbacSQL(roleId, self.session().query(RoleMapped))
        if detailed:
            entities, total = self._getAllWithCount(None, q, offset, limit, sql)
            return IterPart(entities, total, offset, limit)
        return self._getAll(filter, q, offset, limit, sql)
    
    def getRights(self, roleId, offset=None, limit=None, detailed=False, q=None):
        '''
        @see: IRoleService.getRights
        '''
        if limit == 0: entities = ()
        else: entities = None
        if detailed or entities is None:
            sql = self.rbacService.rightsForRbacSQL(roleId)
            if q:
                assert isinstance(q, QRight), 'Invalid query %s' % q
                sql = buildQuery(sql, q, RightMapped)
            if entities is None: entities = buildLimits(sql, offset, limit).all()
            if detailed: return IterPart(entities, sql.count(), offset, limit)
        return entities
    
    def insert(self, role):
        '''
        @see: EntityCRUDServiceAlchemy.insert
        '''
        roleId = super().insert(role)
        self.rbacService.mergeRole(roleId)
        return roleId
    
    def assignRole(self, toRoleId, roleId):
        '''
        @see: IRoleService.assignRole
        '''
        self.rbacService.assignRole(roleId, toRoleId)

    def unassignRole(self, toRoleId, roleId):
        '''
        @see: IRoleService.unassignRole
        '''
        return self.rbacService.unassignRole(roleId, toRoleId)
    
    def assignRight(self, roleId, rightId):
        '''
        @see: IRoleService.assignRole
        '''
        sql = self.session().query(RbacRight).filter(RbacRight.rbac == roleId).filter(RbacRight.right == rightId)
        if sql.count() > 0: return  # The right is already mapped to role
        self.session().add(RbacRight(rbac=roleId, right=rightId))
        
    def unassignRight(self, roleId, rightId):
        '''
        @see: IRoleService.unassignRole
        '''
        sql = self.session().query(RbacRight).filter(RbacRight.rbac == roleId).filter(RbacRight.right == rightId)
        return sql.delete() > 0

# --------------------------------------------------------------------
