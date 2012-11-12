'''
Created on Nov 23, 2011

@package: ally core http
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Runs the production web server.
'''

from ..ally_core_http import server_type, server_host, server_port
from ally.container import ioc
from ally.container.ioc import ConfigError
from ally.core.http.server import server_proxy
from multiprocessing import cpu_count
from threading import Thread

# --------------------------------------------------------------------

@ioc.config
def proxied_server() -> str:
    '''
    The name of the server to use as the proxied server, this is usually the same names as the server type configuration,
    but only some servers can work as a proxied server. The default is "basic"
    '''
    return 'basic'

@ioc.config
def proxied_ports() -> list:
    '''
    The ports of proxied servers to use, if the value is "auto" then the number of proxied server will be the number of
    available CPUs on the machine, with the ports starting from the proxy port +1 for each proxy. Otherwise just provide
    the ports for the proxied servers.
    '''
    return ['auto']

# --------------------------------------------------------------------

@ioc.entity
def proxiedServers():
    '''
    A dictionary containing the known proxied servers.
    '''
    return {}

# --------------------------------------------------------------------

@ioc.start
def runServer():
    if server_type() == 'proxy':
        proxiedServer = proxiedServers().get(proxied_server())
        if proxiedServer is None: raise ConfigError('Invalid proxied server name \'%s\'' % proxied_server())
        proxiedPorts = proxied_ports()
        if len(proxiedPorts) == 0: raise ConfigError('At least one proxied server is required')
        if len(proxiedPorts) == 1 and proxiedPorts[0] == 'auto':
            proxiedPorts = [server_port() + k for k in range(1, cpu_count() + 1)]
        
        args = proxiedServer, proxiedPorts, server_host(), server_port()
        Thread(name='HTTP server thread', target=server_proxy.run, args=args).start()
