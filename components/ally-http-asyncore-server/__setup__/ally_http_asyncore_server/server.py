'''
Created on Nov 23, 2011

@package: ally http
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Runs the asyncore py web server.
'''

from ..ally_http import server_type, server_version, server_host, server_port
from ..ally_http.server import assemblyServer
from ally.container import ioc
from ally.http.server import server_asyncore
from threading import Thread

# --------------------------------------------------------------------

SERVER_ASYNCORE = 'asyncore'
# The asyncore server name

# --------------------------------------------------------------------

@ioc.replace(server_type)
def server_type_asyncore():
    '''
    "%s" - server made based on asyncore package, fast (runs on a single CPU) and reliable.
    ''' % SERVER_ASYNCORE
    return SERVER_ASYNCORE

# --------------------------------------------------------------------

@ioc.entity
def serverAsyncoreRequestHandler(): return server_asyncore.RequestHandler

@ioc.entity
def serverAsyncore():
    b = server_asyncore.AsyncServer()
    b.serverVersion = server_version()
    b.serverHost = server_host()
    b.serverPort = server_port()
    b.requestHandlerFactory = serverAsyncoreRequestHandler()
    b.assembly = assemblyServer()
    return b

# --------------------------------------------------------------------

@ioc.start
def runServer():
    if server_type() == SERVER_ASYNCORE:
        Thread(name='HTTP server thread', target=server_asyncore.run, args=(serverAsyncore(),)).start()
