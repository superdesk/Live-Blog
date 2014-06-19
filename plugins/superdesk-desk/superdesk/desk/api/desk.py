'''
Created on April 2, 2013

@package: superdesk desk
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Martin Saturka

API specifications for desk and desk user.
'''

from ally.api.config import service, call, query, DELETE, UPDATE, GET
from ally.api.criteria import AsLikeOrdered
from ally.api.type import Iter
from ally.support.api.entity_ided import Entity, IEntityService, QEntity
from superdesk.api.domain_superdesk import modelDesk
from superdesk.user.api.user import User, QUser
from superdesk.desk.api.task_type import TaskType

# --------------------------------------------------------------------

@modelDesk
class Desk(Entity):
    '''
    Provides the desk model.
    '''
    Name = str
    Description = str

# --------------------------------------------------------------------

@query(Desk)
class QDesk(QEntity):
    '''
    Provides the query for desk model.
    '''
    name = AsLikeOrdered
    description = AsLikeOrdered

# --------------------------------------------------------------------

@service((Entity, Desk), (QEntity, QDesk))
class IDeskService(IEntityService):
    '''
    Provides the service methods for the desk.
    '''

    @call(method=GET)
    def getUsers(self, deskId:Desk.Id, detailed:bool=True,
                  q:QUser=None) -> Iter(User.Id):
        '''
        Provides all users of a desk.
        '''

    @call(method=GET, webName="Unassigned")
    def getUnassignedUsers(self, deskId:Desk.Id, detailed:bool=True,
                           q:QUser=None) -> Iter(User.Id):
        '''
        Returns a list of users that are not assigned to the given desk.
        '''

    @call(method=UPDATE)
    def attachUser(self, deskId:Desk.Id, userId:User.Id):
        '''
        Puts a user into a desk.
        '''

    @call(method=DELETE)
    def detachUser(self, deskId:Desk.Id, userId:User.Id) -> bool:
        '''
        Unsets a user from a desk.
        '''

    @call(method=GET)
    def getTaskTypes(self, deskId:Desk.Id, detailed:bool=True) -> Iter(TaskType.Name):
        '''
        Provides all task types of a desk.
        '''
        
    @call(method=GET, webName="Unassigned")
    def getUnassignedTaskTypes(self, deskId:Desk.Id, detailed:bool=True) -> Iter(TaskType.Name):
        '''
        Returns a list of task types that are not assigned to the given desk.
        '''
        
    @call(method=UPDATE)
    def attachTaskType(self, deskId:Desk.Id, taskTypeKey:TaskType.Name):
        '''
        Attach a task type to a desk.
        '''

    @call(method=DELETE)
    def detachTaskType(self, deskId:Desk.Id, taskTypeKey:TaskType.Name) -> bool:
        '''
        Detach a task type from a desk.
        '''
