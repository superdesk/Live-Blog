'''
Created on Jan 9, 2014

@package: workflow
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

API specifications for work flow desk.
'''

from ally.api.config import service, query
from ally.api.criteria import AsLike
from ally.support.api.entity_named import IEntityService, Entity, QEntity
from workflow.api.domain_workflow import modelWorkFlow


# --------------------------------------------------------------------
@modelWorkFlow
class Desk(Entity):
    '''
    Provides the work flow desk model.
    '''
    Description = str

# --------------------------------------------------------------------

@query(Desk)
class QDesk(QEntity):
    '''
    Provides the query for desk model.
    '''
    description = AsLike
    
# --------------------------------------------------------------------

@service((Entity, Desk), (QEntity, QDesk))
class IDeskService(IEntityService):
    '''
    Provides the service methods for desks.
    '''
