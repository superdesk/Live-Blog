'''
Created on Nov 23, 2011

@package: ally core http
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Runs the basic web server.
'''

from . import server_type, server_version, server_host, server_port
from .processor import pathAssemblies
from ally.container import ioc
from ally.core.http.server import server_basic
from ally.core.http.server.wsgi import RequestHandler
from threading import Thread

# --------------------------------------------------------------------

@ioc.entity
def requestHandlerWSGI():
    b = RequestHandler(); yield b
    b.pathAssemblies = pathAssemblies()
    b.serverVersion = server_version()

# --------------------------------------------------------------------

try: from ..ally_http_proxy_server.server import proxiedServers
except ImportError: pass  # The proxy server is not available
else:
    @ioc.before(proxiedServers)
    def placeToProxy():
        args = pathAssemblies(), server_version(), server_host()
        proxiedServers()['basic'] = lambda port: server_basic.run(*args, port=port)

@ioc.start
def runServer():
    if server_type() == 'basic':
        args = pathAssemblies(), server_version(), server_host(), server_port()
        Thread(name='HTTP server thread', target=server_basic.run, args=args).start()
