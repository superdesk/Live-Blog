'''
Created on May 29, 2013

@package: superdesk desk
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Martin Saturka

Provides task-file links API support.
'''

from ..api.task import Task
from ally.api.config import service
from ally.support.api.entity import Entity
from support.api.file_link import IFileLinkService

# --------------------------------------------------------------------

@service((Entity, Task))
class ITaskFileService(IFileLinkService):
    '''
    Provides the task file service.
    '''
