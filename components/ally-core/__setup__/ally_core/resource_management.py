'''
Created on Nov 24, 2011

@package: ally core
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the configurations for the resource manager.
'''

from .assembler import assemblers
from ally.container import ioc
from ally.core.impl.resources_management import ResourcesManager
from ally.core.spec.resources import IResourcesLocator, IResourcesRegister

# --------------------------------------------------------------------
# Creating the resource manager

@ioc.entity
def services(): return []

@ioc.entity
def resourcesLocator() -> IResourcesLocator:
    return resourcesRegister()

@ioc.entity
def resourcesRegister() -> IResourcesRegister:
    b = ResourcesManager(); yield b
    b.services = services()
    b.assemblers = assemblers()
