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
from threading import Thread

# --------------------------------------------------------------------

@ioc.entity
def requestHandler():
    from ally.core.http.server.server_wsgi import RequestHandler
    b = RequestHandler(); yield b
    b.pathAssemblies = pathAssemblies()
    b.serverVersion = server_version()

# --------------------------------------------------------------------

@ioc.start
def runServer():
    if server_type() == 'wsgiref':
        args = requestHandler(), server_host(), server_port()
        Thread(target=server_wsgiref.run, args=args).start()
