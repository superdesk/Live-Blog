'''
Created on Nov 23, 2011

@package: ally core http
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Runs the production web server.
'''

from ..ally_core_http import server_type, server_version, server_host, \
    server_port
from ..ally_core_http.processor import pathAssemblies
from ally.container import ioc
from ally.core.http.server import server_production
from threading import Thread

# --------------------------------------------------------------------

@ioc.config
def processes_pool_size():
    '''
    The number of processes to use, if the value is "auto" then the number of processes will be the number of available CPUs
    on the machine.
    '''
    return 'auto'

@ioc.config
def processes_thread_size():
    '''
    The number of threads per processes to use.
    '''
    return 20

# --------------------------------------------------------------------

@ioc.start
def runServer():
    if server_type() == 'production':
        args = pathAssemblies(), server_version(), server_host(), server_port(), processes_pool_size(), \
        processes_thread_size()
        Thread(name='HTTP server thread', target=server_production.run, args=args).start()
