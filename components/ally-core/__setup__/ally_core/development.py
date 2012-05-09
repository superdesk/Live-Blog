'''
Created on Nov 24, 2011

@package: ally core
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the configurations for development tools.
'''

from .resource_management import resourcesRegister
from ally.container import ioc
from ally.core.impl.devel.memory_status import MemoryStatusPresenter

# --------------------------------------------------------------------
# Creating the development tools

@ioc.config
def application_mode() -> str:
    '''The application mode one of devel, prod'''
    return 'prod'


@ioc.entity
def memoryStatusPresenter():
    b = MemoryStatusPresenter()
    b.resourcesRegister = resourcesRegister()
    return b

@ioc.after(resourcesRegister)
def development():
    if application_mode() == 'devel':
        memoryStatusPresenter()
