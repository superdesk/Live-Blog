'''
Created on Nov 23, 2011

@package: ally core http
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Runs the cherry py web server.
'''

from . import server_type, server_version, server_port
from .processor import pathAssemblies
from ally.container import ioc
from threading import Thread

# --------------------------------------------------------------------

@ioc.config
def server_host() -> str:
    '''The IP address to bind the server to'''
    return '127.0.0.1'

@ioc.config
def server_thread_pool() -> int:
    '''The thread pool size for the server'''
    return 10

@ioc.entity
def requestHandler():
    from ally.core.http.server.server_cherrypy import RequestHandler
    b = RequestHandler(); yield b
    b.pathAssemblies = pathAssemblies()
    b.serverVersion = server_version()

# --------------------------------------------------------------------

@ioc.start
def runServer():
    if server_type() == 'cherrypy':
        from ally.core.http.server import server_cherrypy

        args = requestHandler(), server_host(), server_port(), server_thread_pool()
        Thread(target=server_cherrypy.run, args=args).start()
