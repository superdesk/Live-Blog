'''
Created on Jun 28, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Module containing the implementation for the resources manager.
'''

from ally.api.configure import serviceFor
from ally.api.operator import Service, Model
from ally.api.type import List, TypeClass
from ally.container.ioc import injected
from ally.core.impl.invoker import InvokerFunction, InvokerCall
from ally.core.impl.node import NodeRoot, NodePath, NodeModel, NodeProperty
from ally.core.spec.resources import Node, Path, ConverterPath, Assembler, \
    ResourcesManager, PathExtended
from ally.support.core.util_resources import pushMatch, findNodeModel
from inspect import isclass
import logging

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

@injected
class ResourcesManagerImpl(ResourcesManager):
    '''
    @see: ResourcesManager container implementation.
    '''
    
    assemblers = list
    # The list of assemblers to be used by this resources manager in order to register nodes.
    services = list
    # The list of services to be registered, the list contains the service instance.

    def __init__(self):
        assert isinstance(self.assemblers, list), 'Invalid assemblers list %s' % self.assemblers
        assert isinstance(self.services, list), 'Invalid services list %s' % self.services
        if __debug__:
            for asm in self.assemblers: assert isinstance(asm, Assembler), 'Invalid assembler %s' % asm
        self._root = NodeRoot(InvokerFunction(List(TypeClass(Path, False)), self.findGetAllAccessible, [], 0))
        self._rootPath = Path([], self._root)
        for service in self.services:
            try: self.register(serviceFor(service), service)
            except: raise Exception('Cannot register service instance %s' % service)
    
    def getRoot(self):
        '''
        @see: ResourcesManager.getRoot
        '''
        return self._root
    
    def register(self, service, implementation):
        #TODO: there is still stuff to do here, for instance the implementation is not mandatory
        # at this point.
        '''
        @see: ResourcesManager.register
        '''
        if isclass(service): service = serviceFor(service)
        assert isinstance(service, Service), 'Invalid service %s' % service
        assert implementation is not None, 'A implementation is required'
        log.info('Assembling node structure for service %s', service)
        invokers = [InvokerCall(service, implementation, call) for call in service.calls.values()]
        for asm in self.assemblers:
            assert isinstance(asm, Assembler)
            asm.assemble(self._root, invokers)
        for invoker in invokers:
            assert isinstance(invoker, InvokerCall)
            log.warning('The service %s call %s could not be resolved in the node structure', \
                        invoker.service, invoker.call)

    def findResourcePath(self, converterPath, paths):
        '''
        @see: ResourcesManager.findResourcePath
        '''
        assert isinstance(converterPath, ConverterPath), 'Invalid converter path %s' % converterPath
        assert isinstance(paths, list), 'Invalid paths %s' % paths
        if len(paths) == 0:
            return Path([], self._root)
        node = self._root
        matches = []
        found = pushMatch(matches, node.tryMatch(converterPath, paths))
        while found and len(paths) > 0:
            found = False
            for child in node.childrens():
                assert isinstance(child, Node)
                match = child.tryMatch(converterPath, paths)
                if pushMatch(matches, match):
                    node = child
                    found = True
                    break
        if len(paths) == 0:
            return Path(matches, node)
        return Path(matches)
    
    def findGetModel(self, fromPath, model):
        '''
        @see: ResourcesManager.findGetModel
        '''
        assert isinstance(fromPath, Path), 'Invalid from path %s' % fromPath
        assert isinstance(fromPath.node, Node), 'Invalid from path Node %s' % fromPath.node
        assert isinstance(model, Model), 'Invalid model %s' % model
        index = len(fromPath.matches) - 1
        while index >= 0:
            node = fromPath.matches[index].node
            assert isinstance(node, Node)
            if isinstance(node, NodeModel) and node.model == model:
                for nodeProperty in node.childrens():
                    if isinstance(nodeProperty, NodeProperty) and nodeProperty.get is not None:
                        matches = []
                        pushMatch(matches, nodeProperty.newMatch())
                        return PathExtended(fromPath, matches, nodeProperty, index + 1)
            for child in node.childrens():
                assert isinstance(child, Node)
                if isinstance(child, NodeModel) and child.model == model:
                    for nodeId in child.childrens():
                        if isinstance(nodeId, NodeProperty) and nodeId.get is not None:
                            matches = []
                            pushMatch(matches, child.newMatch())
                            pushMatch(matches, nodeId.newMatch())
                            return PathExtended(fromPath, matches, nodeId, index + 1)
            index -= 1
        return None
        
    def findGetAllAccessible(self, fromPath=None):
        '''
        @see: ResourcesManager.findGetAllAccessible
        '''
        if fromPath is None: fromPath = self._rootPath
        
        assert isinstance(fromPath, Path), 'Invalid from path %s' % fromPath
        assert isinstance(fromPath.node, Node), 'Invalid from path Node %s' % fromPath.node
        paths = []
        for child in fromPath.node.childrens():
            assert isinstance(child, Node)
            if isinstance(child, NodePath):
                matches = []
                pushMatch(matches, child.newMatch())
                extended = PathExtended(fromPath, matches, child)
                if child.get: paths.append(extended)
                paths.extend(self.findGetAllAccessible(extended))
        return paths
    
    def findGetAccessibleByModel(self, model, obj):
        '''
        @see: ResourcesManager.findGetAccessibleByModel
        '''
        assert isinstance(model, Model), 'Invalid model %s' % model
        paths = []
        # First we find the model node.
        node = findNodeModel(self._root, model)
        if node:
            # Search the NodeProperty's
            assert isinstance(node, NodeModel)
            matches = [self._root.newMatch()]
            if pushMatch(matches, node.newMatch()):
                for child in node.childrens():
                    if isinstance(child, NodeProperty):
                        matches = []
                        if not pushMatch(matches, self._root.newMatch()): continue
                        if not pushMatch(matches, node.newMatch()): continue
                        if not pushMatch(matches, child.newMatch()): continue
                        path = Path(matches, child)
                        path.update(obj, model)
                        paths.extend(self.findGetAllAccessible(path))
        return paths
