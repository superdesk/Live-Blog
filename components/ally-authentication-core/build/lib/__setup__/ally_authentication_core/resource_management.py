'''
Created on Nov 24, 2011

@package: ally authentication core
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the configurations for the authentication resource manager.
'''

from ..ally_core.resource_management import resourcesRegister, resourcesManager
from .assembler import assemblersAuthentication
from ally.container import ioc
from ally.core.impl.resources_management import ResourcesManager
from ally.core.spec.resources import IResourcesLocator, IResourcesRegister
from ally.support.core.util_resources import ResourcesRegisterDelegate

# --------------------------------------------------------------------
# Creating the resource manager

@ioc.entity
def resourcesManagerAuthentication():
    b = ResourcesManager(); yield b
    b.assemblers = assemblersAuthentication()

@ioc.entity
def resourcesLocatorAuthentication() -> IResourcesLocator:
    return resourcesManagerAuthentication()

# --------------------------------------------------------------------

@ioc.replace(resourcesRegister)
def resourcesRegister() -> IResourcesRegister:
    return ResourcesRegisterDelegate(resourcesManager(), resourcesManagerAuthentication())
