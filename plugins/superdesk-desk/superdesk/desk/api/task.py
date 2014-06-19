'''
Created on April 2, 2013

@package: superdesk desk
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Martin Saturka

API specifications for desk task.
'''

from ally.api.config import service, call, query, GET
from ally.api.criteria import AsLikeOrdered, AsDateTimeOrdered
from ally.api.type import Iter, Reference
from ally.support.api.entity_ided import Entity, IEntityService, QEntity
from superdesk.api.domain_superdesk import modelDesk
from superdesk.user.api.user import User
from datetime import datetime
from ..api.desk import Desk
from ..api.task_status import TaskStatus
from ..api.task_type import TaskType
from ally.api.option import SliceAndTotal

# --------------------------------------------------------------------

@modelDesk
class TaskPrototype(Entity):
    '''
    Provides the desk task prototype model.
    '''
    Desk = Desk
    User = User
    Title = str
    Description = str
    StartDate = datetime
    DueDate = datetime
    Status = TaskStatus
    Type = TaskType
    UserImage = Reference

# --------------------------------------------------------------------

@modelDesk
class Task(TaskPrototype):
    '''
    Provides the desk task node model.
    '''
    Parent = TaskPrototype

# --------------------------------------------------------------------

@query(Task)
class QTask(QEntity):
    '''
    Provides the query for desk task model.
    '''
    title = AsLikeOrdered
    description = AsLikeOrdered
    startDate = AsDateTimeOrdered
    dueDate = AsDateTimeOrdered

# --------------------------------------------------------------------

@service((Entity, Task), (QEntity, QTask))
class ITaskService(IEntityService):
    '''
    Provides the service methods for the desk task.
    '''

    @call(method=GET)
    def getAll(self, deskId:Desk.Id=None, userId:User.Id=None, statusKey:TaskStatus.Name=None,
               detailed:bool=True, q:QTask=None, **options:SliceAndTotal) -> Iter(Task.Id):
        '''
        Provides all the available tasks.
        '''

    @call(method=GET, webName='Task')
    def getSubtasks(self, taskId:Task.Id, statusKey:TaskStatus.Name=None,
               detailed:bool=True, q:QTask=None, **options:SliceAndTotal) -> Iter(Task.Id):
        '''
        Provides the direct subtasks of a task.
        '''

    @call(method=GET, webName='Tree')
    def getSubtree(self, taskId:Task.Id, statusKey:TaskStatus.Name=None,
               detailed:bool=True, q:QTask=None, **options:SliceAndTotal) -> Iter(Task.Id):
        '''
        Provides the whole subtree available tasks.
        '''
