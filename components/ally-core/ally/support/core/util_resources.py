'''
Created on Jan 4, 2012

@package: ally core
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides utility methods based on the specifications.
'''

from ally.core.impl.node import NodeModel, NodePath
from ally.core.spec.resources import Match, Node, Path, ConverterPath
from ally.api.operator.container import Model

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
        elif match is not True:
            raise AssertionError('Invalid match %s') % match
        return True
    return False

def matchesForNode(node):
    '''
    Provides all the matches that lead to the provided node. The node needs to be in a tree node to have valid matches
    for it, this matches can be used to construct a Path.
    
    @param node: Node
        The node to provide the matches for.
    @return: list[Match]
        The list of matches that lead to the node.
    '''
    assert isinstance(node, Node), 'Invalid node %s' % node
    matches = []
    while node is not None:
        pushMatch(matches, node.newMatch())
        node = node.parent
    matches.reverse() # We need to reverse the matches since they have been made from the child up.
    return matches

def toPaths(matches, converterPath):
    '''
    Converts the matches into paths elements.
    
    @param matches: list[Match|string]|tuple(Match|string)
        The list of matches or string that represent the path.
    @param converterPath: ConverterPath
        The converter path to use in constructing the paths elements.
    @return: list[string]
        A list of strings representing the paths elements, or None if the path elements cannot be obtained.
    @raise AssertionError:
        If the path cannot be represented, check first the 'isValid' method.
    '''
    assert isinstance(matches, (list, tuple)), 'Invalid matches %s' % matches
    assert isinstance(converterPath, ConverterPath), 'Invalid converter path %s' % converterPath
    paths = []
    for k in range(0, len(matches)):
        match = matches[k]
        if isinstance(match, Match):
            assert isinstance(match, Match)
            path = match.toPath(converterPath, k == 0, k == len(matches) - 1)
            if path is not None:
                if isinstance(path, list):
                    paths.extend(path)
                paths.append(path)
        elif isinstance(match, str):  paths.append(match)
        else: raise AssertionError('Invalid match %s' % match)
    return paths

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
    names.reverse() # We need to reverse since we started from the child to parent
    return ''.join(names)

def findNodeModel(root, model):
    '''
    Finds the node model in the provided node, None if there is no such node model.
    
    @param root: Node
        The root node to search the node model in.
    @param model: Model
        The model to search.
    @return: NodeModel|None
        The found node model or None if there is no node for the provided model in the root node.
    '''
    assert isinstance(root, Node), 'Invalid root node %s' % root
    assert isinstance(model, Model), 'Invalid model %s' % model
    for child in root.childrens():
        if isinstance(child, NodeModel) and child.model == model: return child

def pathForNode(node):
    '''
    Provides the path that leads to the provided node. The node needs to be in a tree node to have a valid path
    for it.
    
    @param node: Node
        The node to provide the matches for.
    @return: Path
        The path that leads to the node.
    '''
    return Path(matchesForNode(node), node)
