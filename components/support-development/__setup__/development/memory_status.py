'''
Created on Nov 24, 2011

@package: ally core
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the configurations for development tools.
'''

from ..ally_core.resources import resourcesRoot
from ..development.service import publish_development
from ally.container import ioc
from development.request.impl.memory_status import MemoryStatusPresenter

# --------------------------------------------------------------------
# Creating the development tools

@ioc.entity
def memoryStatusPresenter():
    b = MemoryStatusPresenter()
    b.root = resourcesRoot()
    return b

@ioc.after(resourcesRoot)
def development():
    if publish_development(): memoryStatusPresenter()
