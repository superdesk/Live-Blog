'''
Created on Nov 23, 2011

@package: ally core http
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Runs the cherry py web server.
'''

from ..ally_core_http import server_type, server_port, server_host
from ..ally_core_http.server_wsgiref import requestHandlerWSGI
from ally.container import ioc
from threading import Thread

# --------------------------------------------------------------------

@ioc.config
def server_name() -> str:
    '''The server name'''
    return 'localhost'

@ioc.config
def request_queue_size() -> int:
    '''The request queue size for the wsgi cherry py server'''
    return 500

# --------------------------------------------------------------------

try:
    from ally.core.http.server import server_cherrypy
    from ..ally_http_proxy_server.server import proxiedServers
except ImportError: pass  # The proxy server is not available
else:
    @ioc.before(proxiedServers)
    def placeToProxy():
        args = requestHandlerWSGI(), server_host()
        kargs = dict(requestQueueSize=request_queue_size(), serverName=server_name())
        proxiedServers()['cherrypy'] = lambda port: server_cherrypy.run(*args, port=port, **kargs)

@ioc.start
def runServer():
    if server_type() == 'cherrypy':
        args = requestHandlerWSGI(), server_host(), server_port(), request_queue_size(), server_name()
        Thread(target=server_cherrypy.run, args=args).start()
