'''
Created on Mar 8, 2013

@package: content packager
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Rus Mugurel

API specifications for group.
'''

from content.packager.api.domain_content import modelContent
from ally.support.api.entity import Entity, IEntityService
from content.packager.api.reference import Reference
from ally.api.config import query, service, call, LIMIT_DEFAULT
from ally.api.criteria import AsLike
from ally.api.type import Iter

# --------------------------------------------------------------------

@modelContent(id='Id')
class Group:
    '''
    Provides the group model.
    '''
    Id = str
    Role = str
    Mode = str

@modelContent
class GroupReference(Entity):
    '''
    Provides the group reference model.
    '''
    Group = Group
    Reference = Reference

# --------------------------------------------------------------------

@query(Group)
class QGroup:
    '''
    Provides the group query.
    '''
    role = AsLike
    mode = AsLike

# --------------------------------------------------------------------

@service
class IGroupService:
    '''
    Provides the service methods for group.
    '''

    @call
    def getById(self, id:Group.Id) -> Group:
        '''
        Provides the group based on the id.

        @param id: string
            The id of the group to find.
        @raise InputError: If the id is not valid.
        '''

    @call
    def getAll(self, offset:int=None, limit:int=LIMIT_DEFAULT, detailed:bool=True, q:QGroup=None) -> Iter(Group):
        '''
        Provides the groups searched by the provided query.

        @param offset: integer
            The offset to retrieve the groups from.
        @param limit: integer
            The limit of groups to retrieve.
        @param detailed: boolean
            If true will present the total count, limit and offset for the partially returned collection.
        @param q: QGroup
            The query to search by.
        '''

    @call
    def insert(self, group:Group) -> Group.Id:
        '''
        Insert the group, also the group will have automatically assigned the Id to it.

        @param group: Group
            The group to be inserted.

        @return: The id assigned to the group
        @raise InputError: If the group is not valid.
        '''

    @call
    def update(self, group:Group):
        '''
        Update the group.

        @param group: Group
            The group to be updated.
        '''

    @call
    def delete(self, id:Group.Id) -> bool:
        '''
        Delete the group for the provided id.

        @param id: integer
            The id of the group to be deleted.

        @return: True if the delete is successful, false otherwise.
        '''

# --------------------------------------------------------------------

@service((Entity, GroupReference))
class IGroupReferenceService(IEntityService):
    '''
    Provides the service methods for the group reference.
    '''
