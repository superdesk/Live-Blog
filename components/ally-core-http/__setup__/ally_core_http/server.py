'''
Created on Feb 1, 2013

@package: ally core http
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the server configuration.
'''

from ..ally_http.server import updateAssemblyServer, assemblyServer
from .processor import assemblyResources
from .processor_error import assemblyErrorDelivery
from ally.container import ioc
from ally.design.processor.handler import Handler
from ally.http.impl.processor.router_by_path import RoutingByPathHandler

# --------------------------------------------------------------------

@ioc.config
def server_provide_resources() -> bool:
    ''' Flag indicating that this server should provide REST resources'''
    return True

@ioc.config
def server_provide_errors() -> bool:
    ''' Flag indicating that this server should provide separate REST errors, mainly used for gateway'''
    return True

@ioc.config
def server_pattern_resources():
    '''
    The pattern used for matching the REST resources paths in HTTP URL's
    !Attention this configuration needs to be in concordance with 'root_uri_resources' configuration
    '''
    return '^resources(?:/|(?=\\.)|$)(.*)'

@ioc.config
def server_pattern_errors():
    '''
    The pattern used for matching the errors paths in HTTP URL's
    '''
    return '^error(?:/|(?=\\.)|$)(.*)'

# --------------------------------------------------------------------

@ioc.entity
def resourcesRouter() -> Handler:
    b = RoutingByPathHandler()
    b.assembly = assemblyResources()
    b.pattern = server_pattern_resources()
    return b

@ioc.entity
def errorsRouter() -> Handler:
    b = RoutingByPathHandler()
    b.assembly = assemblyErrorDelivery()
    b.pattern = server_pattern_errors()
    return b

# --------------------------------------------------------------------

@ioc.before(updateAssemblyServer)
def updateAssemblyServerForResources():
    if server_provide_resources(): assemblyServer().add(resourcesRouter())

@ioc.after(updateAssemblyServerForResources)
def updateAssemblyServerForError():
    if server_provide_errors(): assemblyServer().add(errorsRouter())
