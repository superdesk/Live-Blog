'''
Created on June 18, 2013

@package: superdesk desk
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Martin Saturka

API specifications for task external link.
'''

from ally.api.config import service, call, query, LIMIT_DEFAULT, GET
from ally.api.criteria import AsLikeOrdered, AsLike
from ally.api.type import Iter
from ally.support.api.entity import Entity, IEntityService, QEntity
from superdesk.api.domain_superdesk import modelDesk
from ..api.task import Task

# --------------------------------------------------------------------

@modelDesk
class TaskExternalLink(Entity):
    '''
    Provides the task external link model.
    '''
    Task = Task
    Title = str
    URL = str
    Description = str

# --------------------------------------------------------------------

@query(TaskExternalLink)
class QTaskExternalLink(QEntity):
    '''
    Provides the query for task external link model.
    '''
    title = AsLikeOrdered
    url = AsLikeOrdered
    description = AsLikeOrdered
    all = AsLike

# --------------------------------------------------------------------

@service((Entity, TaskExternalLink), (QEntity, QTaskExternalLink))
class ITaskExternalLinkService(IEntityService):
    '''
    Provides the service methods for the task external links.
    '''

    @call(method=GET)
    def getAll(self, taskId:Task.Id=None, offset:int=None, limit:int=LIMIT_DEFAULT, detailed:bool=True,
               q:QTaskExternalLink=None) -> Iter(TaskExternalLink):
        '''
        Provides all the available task external links.
        '''
