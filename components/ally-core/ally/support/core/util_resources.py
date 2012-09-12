'''
Created on Jan 4, 2012

@package: ally core
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides utility methods based on the API specifications.
'''

from ally.core.impl.node import NodePath
from ally.core.spec.resources import Match, Node, Path, ConverterPath, \
    IResourcesRegister

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
