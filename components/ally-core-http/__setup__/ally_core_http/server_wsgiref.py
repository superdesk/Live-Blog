'''
Created on Oct 23, 2012

@package: ally core http
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Runs the wsgiref web server.
'''

from . import server_type, server_version, server_host, server_port
from .processor import pathAssemblies
from ally.container import ioc
from ally.core.http.server import server_wsgiref
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
        args = requestHandlerWSGI(), server_host(), server_port()
        proxiedServers()['wsgiref'] = lambda port: server_wsgiref.run(*args, port=port)

@ioc.start
def runServer():
    if server_type() == 'wsgiref':
        args = requestHandlerWSGI(), server_host(), server_port()
        Thread(target=server_wsgiref.run, args=args).start()
