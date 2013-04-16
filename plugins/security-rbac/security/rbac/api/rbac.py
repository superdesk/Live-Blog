'''
Created on Dec 21, 2012

@package: security - role based access control
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

API specifications for RBAC right.
'''

from .domain_rbac import modelRbac
from ally.api.config import query, service, call, UPDATE, DELETE, alias
from ally.api.criteria import AsLikeOrdered
from ally.api.type import Iter
from ally.support.api.entity import Entity, QEntity, IEntityService
from security.api.right import Right, QRight

# --------------------------------------------------------------------

@modelRbac
class Rbac(Entity):
    '''
    Provides the base model that has role based access.
    '''

@modelRbac
class Role(Rbac):
    '''
    Provides the role related data.
    '''
    Name = str
    Description = str

@alias
class ToRole(Role):
    '''
    Role model used as a reference for assignments.
    '''

# --------------------------------------------------------------------

@query(Role)
class QRole(QEntity):
    '''
    Query for role service
    '''
    name = AsLikeOrdered

# --------------------------------------------------------------------

@service((Entity, Role), (QEntity, QRole))
class IRoleService(IEntityService):
    '''
    Role model service API.
    '''
    
    @call
    def getByName(self, name:Role.Name) -> Role:
        '''
        Provides the role based on a provided name.
        '''
    
    @call(webName='Roles')
    def getRoles(self, roleId:Role, offset:int=None, limit:int=None, detailed:bool=True, q:QRole=None) -> Iter(Role):
        '''
        Provides the roles searched by the provided query.
        '''
        
    @call
    def getRights(self, roleId:Role, offset:int=None, limit:int=None, detailed:bool=True, q:QRight=None) -> Iter(Right):
        '''
        Provides the rights for the provided role id searched by the query.
        '''
    
    @call(method=UPDATE)
    def assignRole(self, toRoleId:ToRole.Id, roleId:Role.Id):
        '''
        Assign to the role the other role. 
        '''
    
    @call(method=DELETE)
    def unassignRole(self, toRoleId:ToRole.Id, roleId:Role.Id) -> bool:
        '''
        Unassign from the role the other role. 
        '''
        
    @call(method=UPDATE)
    def assignRight(self, roleId:Role.Id, rightId:Right.Id):
        '''
        Assign to the role the right. 
        '''
    
    @call(method=DELETE)
    def unassignRight(self, roleId:Role.Id, rightId:Right.Id) -> bool:
        '''
        Unassign from the role the right. 
        '''

# --------------------------------------------------------------------
