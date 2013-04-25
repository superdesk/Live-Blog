'''
Created on April 23, 2013

@package: superdesk desk
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Martin Saturka

API specifications for desk task comment.
'''

from ally.api.config import service, call, query, LIMIT_DEFAULT, GET
from ally.api.criteria import AsLikeOrdered, AsDateTimeOrdered
from ally.api.type import Iter
from ally.support.api.entity import Entity, IEntityService, QEntity
from superdesk.api.domain_superdesk import modelDesk
from superdesk.user.api.user import User
from datetime import datetime
from ..api.task import Task

# --------------------------------------------------------------------

@modelDesk
class TaskComment(Entity):
    '''
    Provides the desk task comment model.
    '''
    Task = Task
    User = User
    Text = str
    CreatedOn = datetime
    UpdatedOn = datetime

# --------------------------------------------------------------------

@query(TaskComment)
class QTaskComment(QEntity):
    '''
    Provides the query for desk task comment model.
    '''
    text = AsLikeOrdered
    createdOn = AsDateTimeOrdered
    updatedOn = AsDateTimeOrdered

# --------------------------------------------------------------------

@service((Entity, TaskComment))
class ITaskCommentService(IEntityService):
    '''
    Provides the service methods for the desk task comment.
    '''

    @call(method=GET)
    def getAll(self, taskId:Task.Id, userId:User.Id=None,
               offset:int=None, limit:int=LIMIT_DEFAULT, detailed:bool=True, q:QTaskComment=None) -> Iter(TaskComment):
        '''
        Provides all the available task comments.
        '''

