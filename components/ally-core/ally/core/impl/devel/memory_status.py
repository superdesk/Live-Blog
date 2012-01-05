'''
Created on Oct 11, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides a Node on the resource manager with an invoker that presents the memory status.
'''

from ally.api.type import Input, Integer, typeFor, String
from ally.container.ioc import injected
from ally.core.impl.invoker import InvokerFunction
from ally.core.impl.node import NodePath
from ally.core.spec.resources import ResourcesManager
from collections import OrderedDict
from inspect import isclass
from ally.support.util_sys import fullyQName
import gc
import sys

# --------------------------------------------------------------------

@injected
class MemoryStatusPresenter:
    '''
    Class providing the memory status presentation.
    '''
    
    resourcesManager = ResourcesManager
    # The resources manager used in getting the node structure.
    
    def __init__(self):
        assert isinstance(self.resourcesManager, ResourcesManager), \
        'Invalid resources manager %s' % self.resourcesManager
        node = NodePath(self.resourcesManager.getRoot(), True, 'MemoryStatus')
        node.get = InvokerFunction(None, self.present, [
                                                        Input('limit', typeFor(Integer)),
                                                        Input('include', typeFor(String)),
                                                        Input('exclude', typeFor(String)),
                                                        ], 0)

    def present(self, limit, include=None, exclude=None):
        '''
        Provides the dictionary structure presenting the memory.
        Attention this will also call the garbage collection.
        
        @return: dictionary
            The dictionary containing the memory status.
        '''
        if not limit: limit = 10
        gc.collect()
        total, referencess = self.getRefcounts(limit, include, exclude)
        return {'References': {'Total':total, 'Class':referencess}}

    def getRefcounts(self, limit, prefixInclude, prefixExclude):
        counts = {}
        total = 0
        for m in sys.modules.values():
            for sym in dir(m):
                o = getattr (m, sym)
                typ = type(o)
                if isclass(typ):
                    name = fullyQName(typ)
                    if name not in counts:
                        count = sys.getrefcount(o)
                        counts[name] = count
                        total += count
        # sort by refcount
        counts = [(name, count) for name, count in counts.items()]
        counts.sort(key=lambda pack: pack[1], reverse=True)
        d = OrderedDict()
        k = 0
        for className, count in counts:
            add = True
            if prefixInclude: add = className.startswith(prefixInclude)
            if prefixExclude: add = not className.startswith(prefixExclude)
            if add: d[className] = str(count)
            if k >= limit: break
            k += 1
        return str(total), d
