'''
Created on Jun 28, 2011

@package: ally core
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Module containing the implementation for the resources manager.
'''

from ally.api.operator.container import Service, Call
from ally.api.operator.type import TypeService, TypeModel, TypeModelProperty
from ally.api.type import Input, typeFor
from ally.container.ioc import injected
from ally.core.impl.invoker import InvokerCall
from ally.core.impl.node import NodePath, NodeProperty
from ally.core.spec.resources import Node, Path, ConverterPath, IAssembler, \
    IResourcesRegister, IResourcesLocator, PathExtended, InvokerInfo, Invoker
from ally.support.core.util_resources import pushMatch
from collections import deque, Iterable
import logging

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

@injected
class ResourcesManager(IResourcesRegister, IResourcesLocator):
    '''
    @see: IResourcesRegister, IResourcesLocator implementations.
    '''

    root = Node
    # The root node for the resource manager.
    assemblers = list
    # The list of assemblers to be used by this resources manager in order to register nodes.

    def __init__(self):
        assert isinstance(self.root, Node), 'Invalid root node %s' % self.root
        assert isinstance(self.assemblers, list), 'Invalid assemblers list %s' % self.assemblers

        self._hintsCall, self._hintsModel = {}, {}
        for asm in self.assemblers:
            assert isinstance(asm, IAssembler), 'Invalid assembler %s' % asm
            known = asm.knownCallHints()
            if known: self._hintsCall.update(known)
            known = asm.knownModelHints()
            if known: self._hintsModel.update(known)

    def register(self, implementation):
        '''
        @see: IResourcesRegister.register
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

                fnc = getattr(typeService.clazz, call.name).__code__
                try: name = fnc.__name__
                except AttributeError: name = call.name
                location = (fnc.co_filename, fnc.co_firstlineno, name)

                assert not unknown, \
                'Allowed call hints are:\n\t%s\nInvalid call hints %r at:\nFile "%s", line %i, in %s' % \
                (('\n\t'.join('"%s": %s' % item for item in self._hintsCall.items()), ', '.join(unknown)) + location)

                for inp in call.inputs:
                    assert isinstance(inp, Input), 'Invalid input %s' % inp
                    if isinstance(inp.type, (TypeModel, TypeModelProperty)):
                        unknown = set(inp.type.container.hints.keys()).difference(self._hintsModel.keys())

                        assert not unknown, \
                        'Allowed model hints are:\n\t%s\nInvalid model hints %r at for %s:\nFile "%s", line %i, in %s' % \
                        (('\n\t'.join('"%s": %s' % item for item in self._hintsModel.items()), ', '.join(unknown),
                          inp.type) + location)

            invokers.append(InvokerCall(implementation, call))

        for asm in self.assemblers:
            assert isinstance(asm, IAssembler)
            asm.assemble(self.root, invokers)
        for invoker in invokers:
            assert isinstance(invoker, Invoker)
            info = invoker.infoAPI or invoker.infoIMPL
            assert isinstance(info, InvokerInfo)
            log.warning('Could not resolve in the node structure the call at:\nFile "%s", line %i, in %s', \
                        info.file, info.line, info.name)

    def findPath(self, converterPath, paths):
        '''
        @see: IResourcesLocator.findPath
        '''
        assert isinstance(converterPath, ConverterPath), 'Invalid converter path %s' % converterPath
        if not isinstance(paths, deque):
            assert isinstance(paths, Iterable), 'Invalid iterable paths %s' % paths
            paths = deque(paths)
        assert isinstance(paths, deque), 'Invalid paths %s' % paths

        if len(paths) == 0: return Path(self, [], self.root)

        node = self.root
        matches = []
        found = pushMatch(matches, node.tryMatch(converterPath, paths))
        while found and len(paths) > 0:
            found = False
            for child in node.children:
                assert isinstance(child, Node)
                match = child.tryMatch(converterPath, paths)
                if pushMatch(matches, match):
                    node = child
                    found = True
                    break

        if len(paths) == 0: return Path(self, matches, node)

        return Path(self, matches)

    def findGetModel(self, fromPath, typeModel):
        '''
        @see: IResourcesLocator.findGetModel
        '''
        assert isinstance(fromPath, Path), 'Invalid from path %s' % fromPath
        assert isinstance(fromPath.node, Node), 'Invalid from path Node %s' % fromPath.node
        assert isinstance(typeModel, TypeModel), 'Invalid model type %s' % typeModel

        matchNodes = deque()
        for index in range(len(fromPath.matches), 0, -1):
            matchNodes.clear()
            path = self._findGetModel(typeModel, fromPath, fromPath.matches[index - 1].node, index, True, matchNodes,
                                      fromPath.matches[index].node if index < len(fromPath.matches) else None)
            if path: return path

    def findGetAllAccessible(self, fromPath=None):
        '''
        @see: IResourcesLocator.findGetAllAccessible
        '''
        if fromPath is None: node = self.root
        else:
            assert isinstance(fromPath, Path), 'Invalid from path %s' % fromPath
            node = fromPath.node
        assert isinstance(node, Node), 'Invalid node %s' % fromPath.node

        paths = []
        for child in node.children:
            assert isinstance(child, Node)
            if isinstance(child, NodePath):
                matches = []
                pushMatch(matches, child.newMatch())
                if fromPath is None: extended = Path(self, matches, child)
                else: extended = PathExtended(fromPath, matches, child)
                if child.get: paths.append(extended)
                paths.extend(self.findGetAllAccessible(extended))
        return paths

    # ----------------------------------------------------------------

    def _findGetModel(self, modelType, fromPath, node, index, inPath, matchNodes, exclude=None):
        '''
        Provides the recursive find of a get model based on the path.
        '''
        assert isinstance(modelType, TypeModel), 'Invalid model type %s' % modelType
        assert isinstance(fromPath, Path), 'Invalid from path %s' % fromPath
        assert isinstance(node, Node), 'Invalid node %s' % node
        assert isinstance(matchNodes, deque), 'Invalid match nodes %s' % matchNodes
        assert exclude is None or  isinstance(exclude, Node), 'Invalid exclude node %s' % exclude

        added = False
        if isinstance(node, NodePath):
            assert isinstance(node, NodePath)
            if not inPath:
                matchNodes.append(node)
                added = True

            if node.name == modelType.container.name:
                for nodeId in node.children:
                    if isinstance(nodeId, NodeProperty):
                        assert isinstance(nodeId, NodeProperty)
                        if nodeId.get is None: continue
                        assert isinstance(nodeId.get, Invoker)
                        if not nodeId.get.output.isOf(modelType): continue

                        for typ in nodeId.typesProperties:
                            assert isinstance(typ, TypeModelProperty)
                            if typ.parent != modelType: continue

                            matches = []
                            for matchNode in matchNodes: pushMatch(matches, matchNode.newMatch())
                            pushMatch(matches, nodeId.newMatch())
                            return PathExtended(fromPath, matches, nodeId, index)

        for child in node.children:
            if child == exclude: continue
            path = self._findGetModel(modelType, fromPath, child, index, False, matchNodes)
            if path: return path

        if added: matchNodes.pop()
