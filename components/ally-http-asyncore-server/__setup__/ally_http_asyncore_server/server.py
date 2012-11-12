'''
Created on Nov 23, 2011

@package: ally core http
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Runs the asyncore py web server.
'''

from ..ally_core_http import server_type, server_version, server_host, \
    server_port
from ..ally_core_http.processor import pathAssemblies
from ally.container import ioc
from ally.core.http.server import server_asyncore
from threading import Thread

# --------------------------------------------------------------------

@ioc.replace(server_type)
def server_type_asyncore():
    '''
    "asyncore" - server made based on asyncore package, fast (runs on a single CPU) and reliable.
    '''
    return 'asyncore'

# --------------------------------------------------------------------

@ioc.start
def runServer():
    if server_type() == 'asyncore':
        args = pathAssemblies(), server_version(), server_host(), server_port()
        Thread(name='HTTP server thread', target=server_asyncore.run, args=args).start()
