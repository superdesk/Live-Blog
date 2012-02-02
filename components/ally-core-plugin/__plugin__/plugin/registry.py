'''
Created on Jan 12, 2012

@package Newscoop
@copyright 2011 Sourcefabric o.p.s.
@license http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the setup registry for the plugins.
'''

from ally.container import ioc
from ally.container.proxy import proxyWrapForImpl
from functools import partial
import logging
from ally.core.spec.resources import ResourcesManager
from cdm.spec import ICDM
from cdm.impl.local_filesystem import LocalFileSystemLinkCDM, HTTPDelivery

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

def registerService(service, binders = None):
    '''
    A listener to register the service.
    
    @param service: object
        The service to be registered.
    @param binders: list[Callable]|tuple(Callable)
        The binders used for the registered services.
    '''
    proxy = proxyWrapForImpl(service)
    if binders:
        for binder in binders: binder(proxy)
    services().append(proxy)

def addService(*binders):
    '''
    Create listener to register the service with the provided binders.
    
    @param binders: arguments[Callable]
        The binders used for the registered services.
    '''
    return partial(registerService, binders = binders)

# --------------------------------------------------------------------

@ioc.config
def gui_server_uri():
    ''' The HTTP server URI '''
    raise ioc.ConfigError('A server URI for the GUI files is required')

@ioc.config
def gui_repository_path():
    ''' The repository absolute path '''
    raise ioc.ConfigError('A repository path for the GUI files is required')

# --------------------------------------------------------------------

@ioc.entity
def cdmGUI() -> ICDM:
    '''
    The content delivery manager (CDM) for the plugin's static resources
    '''
    delivery = HTTPDelivery()
    delivery.serverURI = gui_server_uri()
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
    assert log.debug('Registered REST services:\n\t%s', '\n\t'.join(str(srv) for srv in services())) or True
    import ally_deploy_plugin
    ally_deploy_plugin.services = services()
