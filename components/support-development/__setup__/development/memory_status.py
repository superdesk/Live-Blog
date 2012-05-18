'''
Created on Nov 24, 2011

@package: ally core
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the configurations for development tools.
'''

from ..ally_core.resource_management import resourcesRegister
from ..development.service import publish_development
from ally.container import ioc
from development.request.impl.memory_status import MemoryStatusPresenter

# --------------------------------------------------------------------
# Creating the development tools

@ioc.entity
def memoryStatusPresenter():
    b = MemoryStatusPresenter()
    b.resourcesRegister = resourcesRegister()
    return b

@ioc.after(resourcesRegister)
def development():
    if publish_development() == 'devel':
        memoryStatusPresenter()
