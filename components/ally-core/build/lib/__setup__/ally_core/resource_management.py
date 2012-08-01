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
from ally.exception import DevelError

# --------------------------------------------------------------------
# Creating the resource manager

@ioc.entity
def services(): return []

@ioc.entity
def resourcesManager():
    b = ResourcesManager(); yield b
    b.assemblers = assemblers()

@ioc.entity
def resourcesLocator() -> IResourcesLocator:
    return resourcesManager()

@ioc.entity
def resourcesRegister() -> IResourcesRegister:
    return resourcesManager()

# --------------------------------------------------------------------

@ioc.start
def registerServices():
    register = resourcesRegister()
    for service in services():
        try: register.register(service)
        except: raise DevelError('Cannot register service instance %s' % service)
