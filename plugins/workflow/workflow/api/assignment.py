'''
Created on Jan 27, 2014

@package: workflow
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mihai Gociu

API specifications for Assignment service.

'''

from ally.api.config import service, query, call
from ally.api.criteria import AsLike, AsLikeOrdered
from ally.api.option import SliceAndTotal # @UnusedImport
from ally.api.type import Iter
from ally.support.api.entity import IEntityCRUDPrototype, IEntityGetPrototype
from workflow.api.domain_workflow import modelWorkFlow
from workflow.api.nodes import Node


# --------------------------------------------------------------------
@modelWorkFlow(id='GUID')
class Assignment:
    '''
    Provides the assignment model.
    '''
    GUID = str
    Name = str
    Node = Node
    Description = str
    
# --------------------------------------------------------------------

@query(Assignment)
class QAssignment:
    '''
    Provides the query for assignment model.
    '''
    name = AsLikeOrdered
    description = AsLike
    
# --------------------------------------------------------------------

@service(('Entity', Assignment), ('QEntity', QAssignment))
class IAssignmentService(IEntityGetPrototype, IEntityCRUDPrototype):
    '''
    Provides the service methods for assignments.
    '''
    
    @call
    def getAssignments(self, node:Node.GUID=None, q:QAssignment=None, **options:SliceAndTotal) -> Iter(Assignment.GUID):
        ''' '''
        
 
