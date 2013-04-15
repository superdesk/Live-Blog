'''
Created on April 2, 2013

@package: superdesk desk
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Martin Saturka

API specifications for desk task.
'''

from ally.api.config import service, call, query, LIMIT_DEFAULT, UPDATE, GET, DELETE
from ally.api.criteria import AsLikeOrdered, AsEqual, AsDateTimeOrdered, AsBoolean
from ally.api.type import Iter
from ally.support.api.entity import Entity, IEntityService, QEntity
from superdesk.api.domain_superdesk import modelDesk
from superdesk.user.api.user import User
from datetime import datetime
from ..api.desk import Desk
from ..api.task_status import TaskStatus

# --------------------------------------------------------------------

@modelDesk
class Task(Entity):
    '''
    Provides the desk task model.
    '''
    # TODO: Martin: add Parent attribute that points to the parent task
    Desk = Desk
    User = User
    Title = str
    Description = str
    StartDate = datetime
    DueDate = datetime
    Status = TaskStatus

# --------------------------------------------------------------------

@query(Task)
class QTask(QEntity):
    '''
    Provides the query for desk task model.
    '''
    user = AsEqual  # TODO: Martin: the relational entities have no place in a query, only the direct properties of a model are mapped here.
    desk = AsEqual  # TODO: Martin: the relational entities have no place in a query, only the direct properties of a model are mapped here.
    title = AsLikeOrdered
    description = AsLikeOrdered
    startDate = AsDateTimeOrdered
    dueDate = AsDateTimeOrdered
    status = AsEqual  # TODO: Martin: the relational entities have no place in a query, only the direct properties of a model are mapped here.
    rootOnly = AsBoolean  # TODO: Martin: this is not a good approach, if you need specific related tasks you should map a service call for that.

# --------------------------------------------------------------------

@service((Entity, Task))
class ITaskService(IEntityService):
    '''
    Provides the service methods for the desk task.
    '''

    @call(method=GET)  # TODO: Martin: preferably the "statusLabel" should be named "statusKey"
    def getAll(self, statusLabel:TaskStatus.Key=None, offset:int=None, limit:int=LIMIT_DEFAULT, detailed:bool=True,
               q:QTask=None) -> Iter(Task):
        '''
        Provides all the available statuses.
        '''
        # TODO: Martin: the comment is wrong.

    @call(method=GET, webName='Back')  # TODO: Martin: the name should be "getAncestors" and weName should be "Ancestors" (why "Back"?)
    # TODO: Martin: why is called "ascending" should be a more relevant name like "nearestFirst"
    def listAncestors(self, taskId:Task.Id, ascending:bool=True) -> Iter(Task):
        '''
        Provides backlinks, i.e. ancestors, of a task.
        '''

    @call(method=GET, webName='Task')  # TODO: Martin: the name should be "getSubtasks"
    # TODO: Martin: the "orderBy" needs to be removed
    # TODO: Martin: we need to talk about "wholeSubtree"
    # TODO: Martin: preferably the "statusLabel" should be named "statusKey"
    def listSubtasks(self, taskId:Task.Id, statusLabel:TaskStatus.Key=None, wholeSubtree:bool=False, orderBy:str=None,
                     offset:int=None, limit:int=LIMIT_DEFAULT, detailed:bool=True, q:QTask=None) -> Iter(Task):
        '''
        Provides direct subtasks of a task.
        '''

    # TODO: Martin: this method does not make sense, when you want to move/attach a task you make an update with a different parent
    @call(method=UPDATE)
    def attachSubtree(self, taskId:Task.Id, subtaskId:Task.Id) -> bool:
        '''
        Joins two task trees.
        '''

    # TODO: Martin: this method does not make sense, when you want to detach a task you make an update with a null parent
    @call(method=DELETE)
    def detachSubtree(self, taskId:Task.Id, subtaskId:Task.Id) -> bool:
        '''
        Splits a task tree.
        '''
