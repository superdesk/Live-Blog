'''
Created on Jan 8, 2014

@package: workflow
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

API specifications for work flow items.
'''


from ally.api.config import service, call
from ally.api.option import SliceAndTotal  # @UnusedImport
from ally.api.type import Iter
from ally.support.api.entity import IEntityNQPrototype
from workflow.api.domain_workflow import modelWorkFlow

from .node import Node


# --------------------------------------------------------------------
@modelWorkFlow(id='GUID')
class Item:
    '''
    Provides the work flow item model.
    '''
    GUID = str
    Description = str
    
# --------------------------------------------------------------------

@service(('Entity', Item))
class IItemService(IEntityNQPrototype):
    '''
    Provides the service methods for items.
    '''
    
    @call
    def getItemsForNode(self, nodeId:Node, **options:SliceAndTotal) -> Iter(Item.GUID):
        ''' Provides the items assigned to a node.'''

