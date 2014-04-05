'''
Created on Jan 21, 2014

@package: workflow
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mihai Gociu

Implementation for Nodes service.
'''

from ally.container.ioc import injected
from ally.container.support import setup
from ally.api.option import SliceAndTotal  # @UnusedImport
from workflow.api.nodes import INodesService
from ally.design.processor.assembly import Assembly
from ally.design.processor.execution import FILL_ALL
from ally.container import wire
from ally.design.processor.attribute import requires
from ally.design.processor.context import Context
from workflow.api import nodes

# --------------------------------------------------------------------

class Graph(Context):
    ''' The graph context.'''
    nodes = requires(dict)

class Node(Context):
    model = requires(nodes.Node)
    edges = requires(list)

class Edge(Context):
    model = requires(nodes.Edge)

# --------------------------------------------------------------------                   
                    
@injected
@setup(INodesService, name='nodesService')
class NodesService(INodesService):
    '''
    Implementation for @see: INodesService
    '''
    assemblyGraph = Assembly;wire.entity('assemblyGraph')
    
    def __init__(self):
        assert isinstance(self.assemblyGraph, Assembly), 'Invalid assembly %s' % self.assemblyGraph
        self._processing = self.assemblyGraph.create(graph=Graph, Node=Node, Edge=Edge)
        self.graph = self.runDeskGraphProcess()
        assert isinstance(self.graph, Graph), 'Invalid Graph context %s' % self.graph
    
    def getNode(self, nodeGUID):
        ''' '''
        node = self.graph.nodes.get(nodeGUID, None)
        if node: return node.model
    
    def getNodes(self, **options):
        ''' '''
        return (node.model for node in self.graph.nodes.values())
    
    def getEdges(self, nodeGUID, **options):
        ''' '''
        node = self.graph.nodes.get(nodeGUID, None)
        return (edge.model for edge in node.edges)
        
    def runDeskGraphProcess(self):
        '''Method to build the Desk Graph structure.'''
        arg = self._processing.execute(FILL_ALL)
        return arg.graph
        
   
        
