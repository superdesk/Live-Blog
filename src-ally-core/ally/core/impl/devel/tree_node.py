'''
Created on Aug 26, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides a Node on the resource manager with an invoker that presents the node tree of the resource manager.
'''

from ally.ioc import injected
from ally.core.spec.resources import ResourcesManager, Node
from collections import OrderedDict
from ally.core.impl.node import NodePath, NodeModel, NodeProperty
from ally.core.impl.invoker import InvokerFunction

# --------------------------------------------------------------------

@injected
class TreeNodePresenter:
    '''
    Class providing the tree node presentation.
    '''
    
    resourcesManager = ResourcesManager
    # The resources manager used in getting the node structure.
    
    def __init__(self):
        assert isinstance(self.resourcesManager, ResourcesManager), \
        'Invalid resources manager %s' % self.resourcesManager
        node = NodePath(self.resourcesManager.getRoot(), True, 'TreeNode')
        node.get = InvokerFunction(None, self.present, [], 0)

    def present(self):
        '''
        Provides the dictionary structure presenting the nodes.
        
        @return: dictionary
            The dictionary containing the node structure.
        '''
        return {'Node':self._present(self.resourcesManager.getRoot())}
        
    def _present(self, node):
        assert isinstance(node, Node)
        ns = OrderedDict()
        
        nodeValue = ''
        if isinstance(node, NodeModel):
            nodeValue = node.model.name
        elif isinstance(node, NodeProperty):
            nodeValue = '%s:%s' % (node.typeProperty.model.name, node.typeProperty.property)
        elif isinstance(node, NodePath):
            nodeValue = node.name
        
        ns[node.__class__.__name__] = nodeValue
        invk = []
        if node.get: invk.append('Get(%s)' % node.get.name)
        if node.insert: invk.append('Insert(%s)' % node.insert.name)
        if node.update: invk.append('Update(%s)' % node.update.name)
        if node.delete: invk.append('Delete(%s)' % node.delete.name)
        ns['Invokers'] = ','.join(invk)
        
        childrens = []
        ns['Childrens'] = childrens
        for child in node.childrens():
            childrens.append({'Node':self._present(child)})
                
        return ns
