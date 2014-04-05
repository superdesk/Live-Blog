'''
Created on Jan 23, 2014

@package: workflow
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mihai Gociu

Creates the Copy Tasting Workflow.

'''

import logging

from ally.container.ioc import injected
from ally.container.support import setup
from ally.design.processor.attribute import requires
from ally.design.processor.context import Context
from ally.design.processor.handler import Handler, HandlerProcessor
from workflow.api import nodes
from functools import partial
from workflow.core.impl.processor.desk import hashNode

# --------------------------------------------------------------------
log = logging.getLogger(__name__)

# --------------------------------------------------------------------

class Graph(Context):
    ''' Provides the graph for a desk.'''
    nodes = requires(dict)

class GraphWorkflow(Context):
    ''' Provides the graph for a desk.'''
    input = requires(Context)
    output = requires(Context)
    workflows = requires(set)

class NodeDesk(Context):
    ''' The node context.'''
    model = requires(nodes.Node)
    edges = requires(list)

class EdgeDesk(Context):
    model = requires(nodes.Edge)

# --------------------------------------------------------------------

@injected
@setup(Handler, name='copyTasting')
class CopyTastingHandler(HandlerProcessor):
    '''
    Implementation for the processor that creates the Copy Tasting Workflow.
    '''
    #schema to create the workflow
    schema = {'$Input': ['CopyTasting'],
                'CopyTasting': ['Spike', 'Interesting', '$Output'],
                'Spike': ['Interesting', '$Output'],
                'Interesting': ['Spike', '$Output']}
    
    def __init__(self):
        super().__init__()
    
    def process(self, chain, graph:Graph, graphWorkflow:GraphWorkflow, Node:NodeDesk, Edge:EdgeDesk, **keyargs):
        '''
        @see: HandlerProcessor.process
        '''
        assert isinstance(graph, Graph), 'Invalid graph %s' % graph
        assert isinstance(graphWorkflow, GraphWorkflow), 'Invalid workflow graph %s' % graphWorkflow

        if 'Copy Tasting' not in graphWorkflow.workflows: return
        graphWorkflow.workflows.discard('Copy Tasting')
        
        #used to create the workflow nodes
        createNode = partial(self.createNode, graph, graphWorkflow.input, Node, nodes.Node)
        #used to create workflow edges
        createEdge = lambda destination: Edge(model=nodes.Edge(destination, 'move'))
        
        # create the output node and the workflow
        graphWorkflow.output = createNode('Output')
        self.createWorkflow(self.schema, graphWorkflow.input, graphWorkflow.output, graph, createNode, createEdge)
        
        graphWorkflow.input = graphWorkflow.output
    
    def createWorkflow(self, schema, input, output, graph, createNode, createEdge):
        # create the nodes for the schema
        for nodeName in schema.keys():
            if nodeName not in ('$Input', '$Output'): createNode(nodeName)

        # auxiliary functions
        nodeId = lambda name: hashNode('%s.%s' % (input.model.Name, name))
        getNode = lambda name: graph.nodes.get(nodeId(name))
        
        #create the workflow based on the schema
        for nodeName in schema.keys():
            if nodeName == '$Input':
                if not input.edges: input.edges = []
                node = input
            else: node = getNode(nodeName)
            
            for destination in schema[nodeName]:
                if destination == '$Output': node.edges.append(createEdge(output.model.GUID))
                else: node.edges.append(createEdge(getNode(destination).model.GUID))
                    
    def createNode(self, graph, base, NodeCtx, NodeModel, name):
        assert isinstance(graph, Graph)
        assert isinstance(base, NodeDesk)
        
        nodeName = '%s.%s' % (base.model.Name, name)
        nodeId =  hashNode(nodeName)
        gnode = graph.nodes.get(nodeId)
        if gnode is None:
            gnode = NodeCtx(model=NodeModel(nodeId, nodeName), edges=[])
            graph.nodes[nodeId] = gnode
        return gnode
