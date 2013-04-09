'''
Created on April 8, 2013

@package: superdesk desk
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Martin Saturka

Contains the SQL alchemy implementation for task status API.
'''

from ..api.task_status import ITaskStatusService
from ..meta.task_status import TaskStatusMapped
from ally.container.ioc import injected
from ally.container.support import setup
from sql_alchemy.impl.keyed import EntityGetServiceAlchemy, \
    EntityFindServiceAlchemy

# --------------------------------------------------------------------

@injected
@setup(ITaskStatusService, name='taskStatusService')
class TaskStatusServiceAlchemy(EntityGetServiceAlchemy, EntityFindServiceAlchemy, ITaskStatusService):
    '''
    Implementation for @see: ITaskStatusService
    '''

    def __init__(self):
        '''
        Construct the task status service.
        '''
        EntityGetServiceAlchemy.__init__(self, TaskStatusMapped)
