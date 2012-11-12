'''
Created on Nov 23, 2011

@package: ally core http
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Runs the cherry py web server.
'''

from ..ally_core_http import server_type, server_port, server_host
from ..ally_core_http.server_basic import requestHandlerWSGI
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

ioc.doc(server_type, '''
    "cherrypy" - multiple threaded server, but slow because of python GIL issue
''')

# --------------------------------------------------------------------

@ioc.start
def runServer():
    if server_type() == 'cherrypy':
        from ally.core.http.server import server_cherrypy
        args = requestHandlerWSGI(), server_host(), server_port(), request_queue_size(), server_name()
        Thread(target=server_cherrypy.run, args=args).start()
