'''
Created on April 15, 2013

@package: superdesk desk
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Martin Saturka

API specifications for desk task link.
'''

from ally.api.config import service, call, query, LIMIT_DEFAULT, GET
from ally.api.criteria import AsLikeOrdered
from ally.api.type import Iter
from ally.support.api.entity import Entity, IEntityService, QEntity
from superdesk.api.domain_superdesk import modelDesk
from ..api.task import Task
from ..api.task_link_type import TaskLinkType

# --------------------------------------------------------------------

@modelDesk
class TaskLink(Entity):
    '''
    Provides the desk task model.
    '''
    Head = Task
    Tail = Task
    Type = TaskLinkType
    Description = str

# --------------------------------------------------------------------

@query(TaskLink)
class QTaskLink(QEntity):
    '''
    Provides the query for desk task model.
    '''
    description = AsLikeOrdered

# --------------------------------------------------------------------

@service((Entity, TaskLink))
class ITaskLinkService(IEntityService):
    '''
    Provides the service methods for the desk task links.
    '''

    @call(method=GET)
    def getAll(self, typeKey:TaskLinkType.Key=None, offset:int=None, limit:int=LIMIT_DEFAULT, detailed:bool=True,
               q:QTaskLink=None) -> Iter(TaskLink):
        '''
        Provides all the available task links.
        '''

    @call(method=GET, webName='Head')
    def getHead(self, headId:Task.Id, typeKey:TaskLinkType.Key=None, offset:int=None, limit:int=LIMIT_DEFAULT, detailed:bool=True,
               q:QTaskLink=None) -> Iter(TaskLink):
        '''
        Provides all task links with specified the head side.
        '''

    @call(method=GET, webName='Tail')
    def getTail(self, tailId:Task.Id, typeKey:TaskLinkType.Key=None, offset:int=None, limit:int=LIMIT_DEFAULT, detailed:bool=True,
               q:QTaskLink=None) -> Iter(TaskLink):
        '''
        Provides all task links with specified the tail side.
        '''

    @call(method=GET)
    def getSide(self, sideId:Task.Id, typeKey:TaskLinkType.Key=None, offset:int=None, limit:int=LIMIT_DEFAULT, detailed:bool=True,
               q:QTaskLink=None) -> Iter(TaskLink):
        '''
        Provides all task links with specified any side.
        '''
