'''
Created on Jan 8, 2014

@package: workflow
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

API specifications for work flow node.
'''

from ally.api.config import service, query
from ally.api.criteria import AsLikeOrdered
from ally.support.api.entity import IEntityGetPrototype, IEntityQueryPrototype
from workflow.api.domain_workflow import modelWorkFlow


# --------------------------------------------------------------------
@modelWorkFlow(id='GUID')
class Node:
    '''
    Provides the work flow node model.
    '''
    GUID = str
    Name = str

# --------------------------------------------------------------------

@query(Node)
class QNode:
    '''
    Provides the query for node model.
    '''
    name = AsLikeOrdered
    
# --------------------------------------------------------------------

@service(('Entity', Node), ('QEntity', QNode))
class INodeService(IEntityGetPrototype, IEntityQueryPrototype):
    '''
    Provides the service methods for nodes.
    '''
