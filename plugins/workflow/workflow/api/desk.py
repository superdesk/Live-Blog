'''
Created on Jan 9, 2014

@package: workflow
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mihai Gociu

API specifications for work flow desk.
'''

from ally.api.config import service, query, call, DELETE
from ally.api.criteria import AsLike
from ally.support.api.entity_named import IEntityService, Entity, QEntity
from workflow.api.domain_workflow import modelWorkFlow
from ally.api.option import SliceAndTotal  # @UnusedImport
from ally.api.type import Iter


# --------------------------------------------------------------------
@modelWorkFlow
class Desk(Entity):
    '''
    Provides the work flow desk model.
    '''
    Name = str
    Description = str

# --------------------------------------------------------------------

@query(Desk)
class QDesk(QEntity):
    '''
    Provides the query for desk model.
    '''
    name = AsLike
    description = AsLike
    
# --------------------------------------------------------------------

@service((Entity, Desk), (QEntity, QDesk))
class IDeskService(IEntityService):
    '''
    Provides the service methods for desks.
    '''
    
    @call
    def getDestinations(self, name:Desk.Name, q:QDesk=None, **options:SliceAndTotal) -> Iter(Desk.Name):
        ''' '''
    
    @call
    def addDestination(self, fromDesk:Desk.Name, toDesk:Desk.Name) -> bool:
        ''' '''
        
    @call(method=DELETE)
    def remDestination(self, fromDesk:Desk.Name, toDesk:Desk.Name) -> bool:
        ''' '''
