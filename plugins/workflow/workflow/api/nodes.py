'''
Created on Jan 21, 2014

@package: workflow
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mihai Gociu

API specifications for Nodes service.
'''

from ally.api.config import service, call
from ally.api.option import SliceAndTotal  # @UnusedImport
from ally.api.type import Iter
from workflow.api.domain_workflow import modelWorkFlow

# --------------------------------------------------------------------

@modelWorkFlow(id='GUID')
class Node:
    '''
    Provides the node model.
    '''
    GUID = str
    Name = str
    
    def __init__(self, GUID=None, Name=None):
        ''' Construct the node with the provided name.'''
        if GUID is not None: self.GUID = GUID
        if Name is not None: self.Name = Name
        
@modelWorkFlow
class Edge:
    '''
    Provides the edge model.
    '''
    Destination = Node
    Default = str
    
    def __init__(self, Destination=None, Default=None):
        ''' Construct the edge with the provided data.'''
        if Destination is not None: self.Destination = Destination
        if Default is not None: self.Default = Default
    
# --------------------------------------------------------------------

@service
class INodesService:
    '''
    '''
    
    @call
    def getNode(self, nodeGUID:Node.GUID) -> Node:
        ''' '''
        
    @call
    def getNodes(self, **options:SliceAndTotal) -> Iter(Node):
        '''Will return all nodes in the Graph'''
        
    @call
    def getEdges(self, nodeGUID:Node.GUID, **options:SliceAndTotal) -> Iter(Edge):
        ''' '''
    
    
    
    
