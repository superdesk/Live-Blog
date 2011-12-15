'''
Created on Nov 24, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the configurations for development tools.
'''

from ally.core.impl.devel.memory_status import MemoryStatusPresenter
from ally.core.impl.devel.tree_node import TreeNodePresenter
from ally import ioc

# --------------------------------------------------------------------
# Creating the development tools

@ioc.onlyIf(_applicationMode='devel', doc='The application mode: one of devel, prod')
@ioc.after
def treeNodePresenter(resourcesManager):
    b = TreeNodePresenter()
    b.resourcesManager = resourcesManager
    return b

@ioc.onlyIf(_applicationMode='devel')
@ioc.after
def memoryStatusPresenter(resourcesManager):
    b = MemoryStatusPresenter()
    b.resourcesManager = resourcesManager
    return b
