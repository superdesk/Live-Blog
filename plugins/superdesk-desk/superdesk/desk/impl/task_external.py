'''
Created on June 18, 2013

@package: superdesk desk
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Martin Saturka

Contains the SQL alchemy implementation for task external link API.
'''

from ..api.task_external import ITaskExternalLinkService, QTaskExternalLink
from ..meta.task_external import TaskExternalLinkMapped
from ..meta.task import TaskMapped
from ally.container.ioc import injected
from ally.container.support import setup
from ally.support.sqlalchemy.util_service import buildQuery, buildLimits
from sql_alchemy.impl.entity import EntityServiceAlchemy
from ally.api.extension import IterPart
from ally.api.criteria import AsLike

# --------------------------------------------------------------------

ALL_NAMES = (TaskExternalLinkMapped.Title, TaskExternalLinkMapped.URL, TaskExternalLinkMapped.Description)

@injected
@setup(ITaskExternalLinkService, name='taskExternalLinkService')
class TaskExternalLinkServiceAlchemy(EntityServiceAlchemy, ITaskExternalLinkService):
    '''
    Implementation for @see: ITaskExternalLinkService
    '''

    def __init__(self):
        '''
        Construct the desk task external link service.
        '''
        EntityServiceAlchemy.__init__(self, TaskExternalLinkMapped, QTaskExternalLink)

    def getAll(self, taskId=None, offset=None, limit=None, detailed=False, q=None):
        '''
        @see: ITaskExternalLinkService.getAll
        '''
        sql = self.session().query(TaskExternalLinkMapped)
        if taskId:
            sql = sql.join(TaskMapped).filter(TaskMapped.Id == taskId)
        if q:
            assert isinstance(q, QTaskExternalLink), 'Invalid task external link query %s' % q
            sql = buildQuery(sql, q, TaskExternalLinkMapped)

            if QTaskExternalLink.all in q:
                filter = None
                if AsLike.like in q.all:
                    for col in ALL_NAMES:
                        filter = col.like(q.all.like) if filter is None else filter | col.like(q.all.like)
                elif AsLike.ilike in q.all:
                    for col in ALL_NAMES:
                        filter = col.ilike(q.all.ilike) if filter is None else filter | col.ilike(q.all.ilike)
                sql = sql.filter(filter)

        sqlLimit = buildLimits(sql, offset, limit)
        if detailed: return IterPart(sqlLimit.all(), sql.count(), offset, limit)
        return sqlLimit.all()
