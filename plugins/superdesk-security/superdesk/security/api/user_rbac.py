'''
Created on Jan 21, 2013

@package: superdesk security
@copyright 2011 Sourcefabric o.p.s.
@license http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

API for user rbac services.
'''

from ally.api.config import service, call, UPDATE, DELETE
from ally.api.type import Iter
from security.api.right import Right, QRight
from security.rbac.api.rbac import Role, QRole
from superdesk.user.api.user import User
from security.api.right_type import RightType

# --------------------------------------------------------------------

@service
class IUserRbacService:
    '''
    Provides the user RBAC service.
    '''
    
    @call
    def getRoles(self, userId:User.Id, offset:int=None, limit:int=None, detailed:bool=True, q:QRole=None) -> Iter(Role):
        '''
        The roles for the provided user id and searched by query.
        '''
        
    @call
    def getRights(self, userId:User.Id, typeId:RightType.Id=None, offset:int=None, limit:int=None,
                  detailed:bool=True, q:QRight=None) -> Iter(Right):
        '''
        The rights for the provided user id searched by the query.
        '''

    @call(method=UPDATE)
    def assignRole(self, userId:User.Id, roleId:Role.Id):
        '''
        Assign to the user the role. 
        '''
    
    @call(method=DELETE)
    def unassignRole(self, userId:User.Id, roleId:Role.Id) -> bool:
        '''
        Unassign from the user the role. 
        '''
        
    @call(method=UPDATE)
    def assignRight(self, userId:User.Id, rightId:Right.Id):
        '''
        Assign to the user the right. 
        '''
    
    @call(method=DELETE)
    def unassignRight(self, userId:User.Id, rightId:Right.Id) -> bool:
        '''
        Unassign from the user the right. 
        '''
