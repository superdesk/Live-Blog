'''
Created on April 15, 2013

@package: superdesk desk
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Martin Saturka

Contains the SQL alchemy implementation for task link type API.
'''

from ..api.task_link_type import ITaskLinkTypeService
from ..meta.task_link_type import TaskLinkTypeMapped
from ally.container.ioc import injected
from ally.container.support import setup
from sql_alchemy.impl.keyed import EntityGetServiceAlchemy, \
    EntityFindServiceAlchemy

# --------------------------------------------------------------------

@injected
@setup(ITaskLinkTypeService, name='taskLinkTypeService')
class TaskLinkTypeServiceAlchemy(EntityGetServiceAlchemy, EntityFindServiceAlchemy, ITaskLinkTypeService):
    '''
    Implementation for @see: ITaskLinkTypeService
    '''

    def __init__(self):
        '''
        Construct the task link type service.
        '''
        EntityGetServiceAlchemy.__init__(self, TaskLinkTypeMapped)
