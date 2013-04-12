'''
Created on Jan 4, 2012

@package: ally core
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides utility methods based on the API specifications.
'''

from ally.api.config import GET, INSERT, UPDATE, DELETE
from ally.api.operator.container import Service, Call
from ally.api.operator.type import TypeModel, TypeModelProperty, TypeService
from ally.api.type import typeFor, Input
from ally.core.impl.invoker import InvokerRestructuring, InvokerCall
from ally.core.impl.node import NodePath, NodeProperty, MatchProperty
from ally.core.spec.resources import Match, Node, Path, ConverterPath, \
    IResourcesRegister, Invoker, PathExtended
from ally.support.util import immut
from collections import deque, Iterable

# --------------------------------------------------------------------

METHOD_NODE_ATTRIBUTE = immut({GET: 'get', INSERT: 'insert', UPDATE: 'update', DELETE: 'delete'})
# Mapping of method and node attribute where the invoker is kept for that method.

# --------------------------------------------------------------------

def pushMatch(matches, match):
    '''
    Adds the match to the matches list, returns True if the match(es) have been added successfully, False if no
    match was added.
    
    @param matches: list[Match]
        The matches to push the match.
    @param match: boolean|list[Match]|tuple(Match)|Match
        The match to push to the the matches list.
    @return: boolean
        True if the match(es) have been added successfully, False if no match was added.
    '''
    if match is not None and match is not False:
        if isinstance(match, (list, tuple)):
            matches.extend(match)
        elif isinstance(match, Match):
            matches.append(match)
        elif match is not True: raise Exception('Invalid match %s') % match
        return True
    return False

def pathForNode(node):
    '''
    Provides the path that lead to the provided node. The node needs to be in a tree node to have a valid path.
    
    @param node: Node
        The node to provide the matches for.
    @return: list[Match]
        The list of matches that lead to the node.
    '''
    assert isinstance(node, Node), 'Invalid node %s' % node
    k, matches = node, []
    while k is not None:
        pushMatch(matches, k.newMatch())
        k = k.parent
    matches.reverse()  # We need to reverse the matches since they have been made from the child up.
    return Path(matches, node)

# --------------------------------------------------------------------

def iterateNodes(node):
    '''
    Iterates all the nodes that can be obtained from the provided node.
    
    @param node: Node
        The root node to provide the paths from.
    @return: Iterator(Node)
        An iterator yielding all the nodes from the provided node.
    '''
    assert isinstance(node, Node), 'Invalid root node %s' % node
    nodes = deque()
    nodes.append(node)
    while nodes:
        node = nodes.popleft()
        yield node
        nodes.extend(node.children)
        
def iteratePaths(node):
    '''
    Iterates all the paths that can be obtained from the provided node.
    
    @param node: Node
        The root node to provide the paths from.
    @return: Iterator(Path)
        An iterator yielding all the paths from the provided node.
    '''
    for node in iterateNodes(node): yield pathForNode(node)

def findPath(node, paths, converterPath):
    '''
    Finds the resource node for the provided request path.
    
    @param node: Node
        The root node to search from.
    @param converterPath: ConverterPath
        The converter path used in handling the path elements.
    @param paths: deque[string]|Iterable[string]
        A deque of string path elements identifying a resource to be searched for, this list will be consumed 
        of every path element that was successfully identified.
    @return: Path
        The path leading to the node that provides the resource if the Path has no node it means that the paths
        have been recognized only to certain point.
    '''
    assert isinstance(node, Node), 'Invalid root node %s' % node
    assert isinstance(converterPath, ConverterPath), 'Invalid converter path %s' % converterPath
    if not isinstance(paths, deque):
        assert isinstance(paths, Iterable), 'Invalid iterable paths %s' % paths
        paths = deque(paths)
    assert isinstance(paths, deque), 'Invalid paths %s' % paths

    if len(paths) == 0: return Path([], node)

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

    if len(paths) == 0: return Path(matches, node)

    return Path(matches)

def findGetModel(fromPath, typeModel):
    '''
    Finds the path for the first Node that provides a get for the name. The search is made based
    on the from path. First the from path Node and is children's are searched for the get method if 
    not found it will go to the Nodes parent and make the search there, so forth and so on.
    
    @param fromPath: Path
        The path to make the search based on.
    @param typeModel: TypeModel
        The type model to search the get for.
    @return: PathExtended|None
        The extended path pointing to the desired get method, attention some updates might be necessary on 
        the path to be available. None if the path could not be found.
    '''
    assert isinstance(fromPath, Path), 'Invalid from path %s' % fromPath
    assert isinstance(fromPath.node, Node), 'Invalid from path Node %s' % fromPath.node
    assert isinstance(typeModel, TypeModel), 'Invalid model type %s' % typeModel

    matchNodes = deque()
    for index in range(len(fromPath.matches), 0, -1):
        matchNodes.clear()
        path = _findGetModel(typeModel, fromPath, fromPath.matches[index - 1].node, index, True, matchNodes,
                             fromPath.matches[index].node if index < len(fromPath.matches) else None)
        if path: return path
    
def findGetAllAccessible(pathOrNode):
    '''
    Finds all GET paths that can be directly accessed without the need of any path update based on the
    provided from path, basically all paths that can be directly related to the provided path without any
    additional information.

    @param pathOrNode: Path|Node
        The path or node to make the search based on, if None will provide the available paths for the root.
    @return: list[Path]|list[PathExtended]
        A list of Path from the provided from path that are accessible, empty list if none found.
        If the input parameter is a path then the returned paths are extended paths of the provided path.
    '''
    if isinstance(pathOrNode, Path):
        assert isinstance(pathOrNode, Path)
        assert isinstance(pathOrNode.node, Node), 'Invalid path Node %s' % pathOrNode.node
        node, path = pathOrNode.node, pathOrNode
    else:
        assert isinstance(pathOrNode, Node), 'Invalid path or node %s' % pathOrNode
        node, path = pathOrNode, None
    assert isinstance(node, Node), 'Invalid node %s' % node
    
    paths = []
    for child in node.children:
        assert isinstance(child, Node)
        if isinstance(child, NodePath):
            matches = []
            pushMatch(matches, child.newMatch())
            if path is None: extended = Path(matches, child)
            else: extended = PathExtended(path, matches, child)
            if child.get: paths.append(extended)
            paths.extend(findGetAllAccessible(extended))
    return paths

def findNodesFor(node, typeService, name):
    '''
    Finds all the nodes in the root node for the provided service type and call name.
    
    @param node: Node
        The root node to start the find in.
    @param typeService: TypeService
        The service type to find the paths for.
    @param name: string
        The call name to find the paths for.
    @return: list[Node]
        The nodes of the service type and call name.
    ''' 
    assert isinstance(node, Node), 'Invalid node %s' % node
    assert isinstance(typeService, TypeService), 'Invalid type service %s' % typeService
    assert isinstance(name, str), 'Invalid call name %s' % name
    assert isinstance(typeService.service, Service)
    call = typeService.service.calls.get(name)
    assert isinstance(call, Call), 'Invalid call name \'%s\' for service %s' % (name, typeService)
    
    nodes, attr = [], METHOD_NODE_ATTRIBUTE[call.method]
    for node in iterateNodes(node):
        invoker = getattr(node, attr)
        if not invoker: continue
        invoker = invokerCallOf(invoker)
        if not invoker: continue
        assert isinstance(invoker, InvokerCall)
        assert isinstance(invoker.call, Call)
        if typeService == typeFor(invoker.implementation) and invoker.call.name == name: nodes.append(node)
    return nodes
    
# --------------------------------------------------------------------

def nodeLongName(node):
    '''
    Provides the fullest name that can be extracted for the provided node. This is done by appending all names of the
    parent nodes that are also path nodes.
    
    @param node: NodePath
        The node to provide the long name for.
    @return: string
        The node long name.
    '''
    assert isinstance(node, NodePath), 'Invalid node %s' % node
    names = []
    while node and isinstance(node, NodePath):
        names.append(node.name)
        node = node.parent
    names.reverse()  # We need to reverse since we started from the child to parent
    return ''.join(names)

def pathLongName(path):
    '''
    Provides the name of a Path @see: nodeLongName.
    
    @param path: Path
        The path to get the name for.
    @return: string
        The path long name.
    '''
    assert isinstance(path, Path), 'Invalid path %s' % path
    return nodeLongName(path.node)

# --------------------------------------------------------------------

def invokerCallOf(invoker):
    '''
    Provides the invoke call of the invoker if one is available.
    
    @param invoker: Invoker
        The invoker to provide the call for.
    @return: InvokerCall|None
        The call of the invoker or None if is not available.
    '''
    assert isinstance(invoker, Invoker), 'Invalid invoker %s' % invoker
    while isinstance(invoker, InvokerRestructuring):
        assert isinstance(invoker, InvokerRestructuring)
        invoker = invoker.invoker
    if isinstance(invoker, InvokerCall): return invoker

def propertyTypesOf(pathOrNode, invoker):
    '''
    Provides the list of property types that are associated with the provided path and invoker.
    Basically it extracts the property types that belong to the invoker and they appear into the path.
    
    @param pathOrNode: Path|Node
        The path or node to provide the property types for.
    @param invoker: Invoker
        The invoker to have the property types associated with the path.
    @return: list[TypePropertyModel]
        The list of model property types that are associated with the invoker.
    '''
    if isinstance(pathOrNode, Node): path = pathForNode(pathOrNode)
    else: path = pathOrNode
    assert isinstance(path, Path), 'Invalid path %s' % path
    assert isinstance(invoker, Invoker), 'Invalid invoker %s' % invoker
    types = []
    for match in path.matches:
        if isinstance(match, MatchProperty):
            assert isinstance(match, MatchProperty)
            assert isinstance(match.node, NodeProperty)
            for inp in invoker.inputs:
                assert isinstance(inp, Input), 'Invalid input %s' % inp
                if isinstance(inp.type, TypeModelProperty) and inp.type in match.node.typesProperties:
                    types.append(inp.type)
                    break
    return types

# --------------------------------------------------------------------

class ResourcesRegisterDelegate(IResourcesRegister):
    '''
    A resource register that delegates all the registering to a collection of other resources registers. Basically 
    allows the same register to be propagated to more then one register. 
    '''

    def __init__(self, main, *others):
        '''
        Constructs the delegate based on the main resource register.
        
        @param main: IResourcesRegister
            The main resources register, the difference between this and the others is that the root node of the main
            register will be the root of this delegate.
        @param others: arguments
            The other registers to delegate to.
        '''
        assert isinstance(main, IResourcesRegister), 'Invalid main register %s' % main
        if __debug__:
            for register in others: assert isinstance(register, IResourcesRegister), 'Invalid register %s' % main

        self.main = main
        self.others = others

    def register(self, implementation):
        '''
        @see: IResourcesRegister.register
        '''
        self.main.register(implementation)
        for register in self.others: register.register(implementation)

class ReplacerMarkCount:
    '''
    Provides the callable support for replacing the invalid matches with markers that are based on a counter, so every
    invalid match will be counted and be replaced with the counter.
    '''
    __slots__ = ('_start', '_index', '_pattern', 'replaced')
    
    def __init__(self, start=1, pattern='{%s}'):
        '''
        Construct the mark replacer.
        
        @param start: integer
            The value from which to start the markers.
        @param pattern: string
            The pattern to be used for constructing the invalid match path.
        '''
        assert isinstance(start, int), 'Invalid start %s' % start
        assert isinstance(pattern, str), 'Invalid pattern %s' % pattern
        self._start = start
        self._index = start
        self._pattern = pattern
        self.replaced = {}
        
    def reset(self):
        '''
        Resets all data.
        '''
        self._index = self._start
        self.replaced.clear()
        
    def __call__(self, match, converterPath):
        assert isinstance(match, Match), 'Invalid match %s' % match
        path = self._pattern % self._index
        self.replaced[path] = match
        self._index += 1
        return path

class ReplacerWithMarkers:
    '''
    Provides the replacer based on property types dictionary with markers.
    '''
    __slots__ = ('_count', '_markers')
    
    def __init__(self):
        '''
        Construct the type based replacer.
        '''
        self._count = 0
        self._markers = ()
        
    def register(self, markers):
        '''
        Register a replacing process. Attention the replacer has to be properly consumed before a new registration.
        
        @param markers: list[string]|tuple(string)
            The markers list, needs to have one entry for each invalid match in the proper order.
        @return: self
            The filter for chaining purposes.
        '''
        assert isinstance(markers, (list, tuple)), 'Invalid markers %s' % markers
        assert len(self._markers) == self._count, 'The markers %s are not consumed' % (self._markers[self._count:],)
        self._markers = markers
        self._count = 0
        return self
    
    def __call__(self, match, converterPath):
        '''
        Process the markers for invalid matches.
        '''
        assert len(self._markers) > self._count, 'No more markers for match %s' % match
        mark = self._markers[self._count]
        self._count += 1
        return mark

# --------------------------------------------------------------------

def _findGetModel(modelType, fromPath, node, index, inPath, matchNodes, exclude=None):
    '''
    FOR INTERNAL USE ONLY!
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
        path = _findGetModel(modelType, fromPath, child, index, False, matchNodes)
        if path: return path

    if added: matchNodes.pop()
