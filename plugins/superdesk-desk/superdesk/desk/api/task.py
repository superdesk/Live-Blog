'''
Created on April 2, 2013

@package: superdesk desk
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Martin Saturka

API specifications for desk task.
'''

from ally.api.config import service, call, query, LIMIT_DEFAULT, GET
from ally.api.criteria import AsLikeOrdered, AsDateTimeOrdered
from ally.api.type import Iter, Reference
from ally.support.api.entity import Entity, IEntityService, QEntity
from superdesk.api.domain_superdesk import modelDesk
from superdesk.user.api.user import User
from datetime import datetime
from ..api.desk import Desk
from ..api.task_status import TaskStatus

# --------------------------------------------------------------------

@modelDesk
class TaskPrototype(Entity):
    '''
    Provides the desk task prototype model.
    '''
    Status = TaskStatus
    Desk = Desk
    User = User
    Title = str
    Description = str
    StartDate = datetime
    DueDate = datetime
    UserImage = Reference

# --------------------------------------------------------------------

@modelDesk(replace=TaskPrototype)
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

@service((Entity, Task))
class ITaskService(IEntityService):
    '''
    Provides the service methods for the desk task.
    '''

    @call(method=GET)
    def getAll(self, deskId:Desk.Id=None, userId:User.Id=None, statusKey:TaskStatus.Key=None, thumbSize:str=None,
               offset:int=None, limit:int=LIMIT_DEFAULT, detailed:bool=True, q:QTask=None) -> Iter(Task):
        '''
        Provides all the available tasks.
        '''

    @call(method=GET, webName='Task')
    def getSubtasks(self, taskId:Task.Id, statusKey:TaskStatus.Key=None, thumbSize:str=None,
               offset:int=None, limit:int=LIMIT_DEFAULT, detailed:bool=True, q:QTask=None) -> Iter(Task):
        '''
        Provides the direct subtasks of a task.
        '''

    @call(method=GET, webName='Tree')
    def getSubtree(self, taskId:Task.Id, statusKey:TaskStatus.Key=None, thumbSize:str=None,
               offset:int=None, limit:int=LIMIT_DEFAULT, detailed:bool=True, q:QTask=None) -> Iter(Task):
        '''
        Provides the whole subtree available tasks.
        '''
