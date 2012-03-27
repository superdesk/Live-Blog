'''
Created on Jun 28, 2011

@package: ally core
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Module containing the implementation for the resources manager.
'''

from ally.api.operator.container import Service, Call, Model
from ally.api.operator.type import TypeService
from ally.api.type import List, Type, Input, typeFor
from ally.container.ioc import injected
from ally.core.impl.invoker import InvokerFunction, InvokerCall
from ally.core.impl.node import NodeRoot, NodePath, NodeModel, NodeProperty
from ally.core.spec.resources import Node, Path, ConverterPath, Assembler, \
    ResourcesManager, PathExtended
from ally.exception import DevelError
from ally.support.core.util_resources import pushMatch, findNodeModel
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

        self._hintsCall, self._hintsModel = {}, {}
        for asm in self.assemblers:
            assert isinstance(asm, Assembler), 'Invalid assembler %s' % asm
            known = asm.knownCallHints()
            if known: self._hintsCall.update(known)
            known = asm.knownModelHints()
            if known: self._hintsModel.update(known)

        self._root = NodeRoot(InvokerFunction(List(Type(Path)), self.findGetAllAccessible, []))
        self._rootPath = Path([], self._root)

        for service in self.services:
            try: self.register(service)
            except: raise DevelError('Cannot register service instance %s' % service)

    def getRoot(self):
        '''
        @see: ResourcesManager.getRoot
        '''
        return self._root

    def register(self, implementation):
        '''
        @see: ResourcesManager.register
        '''
        assert implementation is not None, 'A implementation is required'
        typeService = typeFor(implementation)
        assert isinstance(typeService, TypeService), 'Invalid service implementation %s' % implementation
        service = typeService.service
        assert isinstance(service, Service), 'Invalid service %s' % service

        log.info('Assembling node structure for service %s', service)
        invokers = []
        for call in service.calls:
            assert isinstance(call, Call), 'Invalid call %s' % call
            if __debug__:
                unknown = set(call.hints.keys()).difference(self._hintsCall.keys())
                assert not unknown, 'Invalid call hints %r for %s in service %s, the allowed call hints are:\n\t%s' % \
                (', '.join(unknown), call, service, '\n\t'.join('"%s": %s' % item for item in self._hintsCall.items()))

                for inp in call.inputs:
                    assert isinstance(inp, Input), 'Invalid input %s' % inp
                    try: model = inp.type.model
                    except AttributeError: pass
                    else:
                        unknown = set(model.hints.keys()).difference(self._hintsModel.keys())
                        assert not unknown, 'Invalid model hints %r for %s in %s, %s, the allowed model hints are:'\
                        '\n\t%s' % (', '.join(unknown), model, call, service, '\n\t'.join('"%s": %s' % item
                                                                                    for item in self._hintsModel.items()))

            invokers.append(InvokerCall(implementation, call))
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
            if isinstance(node, NodePath):
                nodeProperty = self._findGetNode(node, model)
                if nodeProperty:
                    matches = []
                    pushMatch(matches, nodeProperty.newMatch())
                    path = PathExtended(fromPath, matches, nodeProperty, index + 1)
                    return path
            for child in node.childrens():
                if isinstance(child, NodePath):
                    nodeId = self._findGetNode(child, model)
                    if nodeId:
                        matches = []
                        pushMatch(matches, child.newMatch())
                        pushMatch(matches, nodeId.newMatch())
                        path = PathExtended(fromPath, matches, nodeId, index + 1)
                        return path
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

    def findGetAccessibleByModel(self, model, modelObject=None):
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
                        paths.extend(self.findGetAllAccessible(path))

        if modelObject:
            for path in paths: path.update(modelObject, model)
        return paths

    # ----------------------------------------------------------------

    def _findGetNode(self, node, model):
        '''
        Utility method to extract the get property node.
        '''
        assert isinstance(node, NodePath)
        assert isinstance(model, Model)
        if node.name == model.name:
            for nodeId in node.childrens():
                if isinstance(nodeId, NodeProperty):
                    assert isinstance(nodeId, NodeProperty)
                    if nodeId.get is not None and nodeId.type.container == model: return nodeId
