'''
Created on Dec 21, 2012

@package: security - role based access control
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Ioan v. Pocol

Provides specification for handling RBAC data.
'''

import abc

# --------------------------------------------------------------------

class IRbacService(metaclass=abc.ABCMeta):
    '''
    Provides support for handling the RBAC data.
    '''
    
    @abc.abstractmethod
    def rightsForRbacSQL(self, rbacId, sql=None):
        '''
        Constructs the SQL alchemy query that fetches the RightModel assigned to the provided rbac id.
        The sql will provide the directly associated rights and the rights of the owned tree roles.
        
        @param rbacId: integer
            The rbac id.
        @param sql: sql
            The sql used for fetching the data if not provided it something like "session().query(RightModel)"
        @return: sql[RightModel]
            The sql alchemy that fetches the rights.
        '''
        
    @abc.abstractmethod
    def rolesForRbacSQL(self, rbacId, sql=None):
        '''
        Constructs the SQL alchemy query that fetches the RoleModel assigned to the provided rbac id.
        The sql will provide all the roles determined from the RBAC structure (directly assigned or inherited)
        
        @param rbacId: integer
            The rbac id.
        @param sql: sql
            The sql used for fetching the data if not provided it something like "session().query(RoleModel)"
        @return: sql[RoleModel]
            The sql alchemy that fetches the roles.
        '''
    
    @abc.abstractmethod    
    def rbacsForRightSQL(self, rightId, sql=None):
        '''
        Constructs the SQL alchemy query that fetches the RbacMapped assigned to the provided right id.
        The sql will provide all the Rbac's determined from the RBAC structure (directly assigned or inherited)
        
        @param rightId: integer
            The right id.   
        @param sql: sql
            The sql used for fetching the data if not provided it something like "session().query(RbacMapped)"
        @return: sql[RbacMapped]
            The sql alchemy that fetches the Rbac's.
        '''
        
    @abc.abstractmethod    
    def rbacsForRoleSQL(self, roleId, sql=None):
        '''
        Constructs the SQL alchemy query that fetches the RbacMapped assigned to the provided role id.
        The sql will provide all the Rbac's determined from the RBAC structure (directly assigned or inherited)
        
        @param roleId: integer
            The role id.   
        @param sql: sql
            The sql used for fetching the data if not provided it something like "session().query(RbacMapped)"
        @return: sql[RbacMapped]
            The sql alchemy that fetches the Rbac's.
        ''' 
        
    @abc.abstractmethod
    def mergeRole(self, roleId):
        '''
        Merges the role into the RBAC structure.
        
        @param roleId: integer
            The role id to be merged.
        '''
    
    @abc.abstractmethod
    def assignRole(self, roleId, toRoleId):
        '''
        Assign the provided role id to the "to" role id.
        
        @param roleId: integer
            The role id to be assigned.
        @param toRoleId: integer
            The role id to be assigned to.
        @return: boolean
            True if the assignment was a success, False otherwise.
        '''
        
    @abc.abstractmethod
    def unassignRole(self, roleId, toRoleId):
        '''
        Unassignes the provided role id from the "to" role id.
        
        @param roleId: integer
            The role id to be unassigned.
        @param toRoleId: integer
            The role id to be unassigned from.
        @return: boolean
            True if the unassign was successful, False otherwise.
        '''
        
    @abc.abstractmethod
    def deleteRole(self, roleId):
        '''
        Delete the role from the RBAC structure, attention the role should not have any child before deletion.
        
        @param roleId: integer
            The role id to be deleted.
        '''

class IRbacSupport(metaclass=abc.ABCMeta):
    '''
    Provides support for querying RBAC data.
    '''
        
    @abc.abstractmethod
    def iterateTypeAndRightsNames(self, rbacId):
        '''
        Iterates the RBAC right types and rights names for the provided rbac id.
        
        @param rbacId: integer
            The rbac id.
        @return: Iterable(tuple(string, Iterable(string)))
            Iterable that provides (right type name, Iterable(right name)).
        '''
