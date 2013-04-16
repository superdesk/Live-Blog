'''
Created on Feb 1, 2013

@package: service CDM
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the server configuration.
'''

from ..ally_http.server import assemblyServer, updateAssemblyServer
from .processor import assemblyGateway, server_provide_gateway, GATEWAY_EXTERNAL, \
    GATEWAY_INTERNAL
from ally.container import ioc
from ally.design.processor.handler import Handler
from ally.http.impl.processor.router_by_path import RoutingByPathHandler

# --------------------------------------------------------------------

@ioc.config
def server_pattern_gateway():
    '''
    The pattern used for matching the gateway paths in HTTP URL's indexed based on the server gateway type that is provided by
    the configuration 'server_provide_gateway'.
    !Attention if the gateway is used with external server then the domains must be matched one on one. As an example when used
        internal the gateway is on 'resources/my' but if use with external server it will always have to be 'resources/' exactly
        as the external server provides it.
    !Attention this configuration needs to be in concordance with 'server_pattern_resources' configuration whenever the gateway 
        is used internally.
    !Attention this configuration needs to be in concordance with 'root_uri_resources' configuration
    '''
    return {
            GATEWAY_EXTERNAL: '(.*)',
            GATEWAY_INTERNAL: '(^resources)\/my((?=/|(?=\\.)|$).*)',
            }

# --------------------------------------------------------------------

@ioc.entity
def gatewayRouter() -> Handler:
    b = RoutingByPathHandler()
    b.assembly = assemblyGateway()
    b.pattern = server_pattern_gateway()[server_provide_gateway()]
    return b

# --------------------------------------------------------------------

@ioc.before(updateAssemblyServer)
def updateAssemblyServerForGatewayExternal():
    if server_provide_gateway() == GATEWAY_EXTERNAL:
        assemblyServer().add(gatewayRouter())
