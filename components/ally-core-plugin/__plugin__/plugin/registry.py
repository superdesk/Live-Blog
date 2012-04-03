'''
Created on Jan 12, 2012

@package: ally core plugin
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the setup registry for the plugins.
'''

from ally.container import ioc
from ally.container.proxy import proxyWrapFor
from ally.core.spec.resources import ResourcesManager
from cdm.impl.local_filesystem import LocalFileSystemLinkCDM, HTTPDelivery
from cdm.spec import ICDM
from functools import partial
from os import path

# --------------------------------------------------------------------

def registerService(service, binders=None):
    '''
    A listener to register the service.
    
    @param service: object
        The service to be registered.
    @param binders: list[Callable]|tuple(Callable)
        The binders used for the registered services.
    '''
    proxy = proxyWrapFor(service)
    if binders:
        for binder in binders: binder(proxy)
    services().append(proxy)

def addService(*binders):
    '''
    Create listener to register the service with the provided binders.
    
    @param binders: arguments[Callable]
        The binders used for the registered services.
    '''
    return partial(registerService, binders=binders)

# --------------------------------------------------------------------
@ioc.config
def gui_server_url():
    ''' The HTTP server URL for javascript content - prefixed '''
    # http://en.wikipedia.org/wiki/Uniform_resource_identifier
    return 'content/'

@ioc.config
def gui_repository_path():
    ''' The repository absolute or relative (to the distribution folder) path '''
    return path.join('workspace', 'cdm')

# --------------------------------------------------------------------

@ioc.entity
def cdmGUI() -> ICDM:
    '''
    The content delivery manager (CDM) for the plugin's static resources
    '''
    delivery = HTTPDelivery()
    delivery.serverURI = gui_server_url()
    delivery.repositoryPath = gui_repository_path()
    cdm = LocalFileSystemLinkCDM()
    cdm.delivery = delivery
    return cdm

@ioc.entity
def resourcesManager() -> ResourcesManager:
    import ally_deploy_plugin
    return ally_deploy_plugin.resourcesManager

@ioc.entity
def services():
    '''
    The plugins services that will be registered automatically.
    '''
    return []

@ioc.start
def register():
    import ally_deploy_plugin
    ally_deploy_plugin.services = services()
