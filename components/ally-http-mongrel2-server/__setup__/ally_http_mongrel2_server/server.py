'''
Created on Nov 23, 2011

@package: ally core http
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Runs the Mongrel2 web server.
'''

from ..ally_core_http import server_host, server_port, server_type, server_version
from ..ally_core_http.processor import pathAssemblies
from ally.container import ioc, support
from threading import Thread

# --------------------------------------------------------------------

@ioc.config     
def workspace_path():
    '''The workspace path where the uploads can be located'''
    return 'workspace'

@ioc.config
def send_ident():
    '''The send ident to use in communication with Mongrel2, if not specified one will be created'''
    return None

@ioc.config
def send_spec():
    '''
    The send address to use in communication with Mongrel2, something like:
    "tcp://127.0.0.1:9997" - for using sockets that allow communication between computers
    "ipc:///tmp/request1" - for using in processes that allow communication on the same computer processes
    '''
    return 'ipc:///tmp/request'

@ioc.config
def recv_ident():
    '''The receive ident to use in communication with Mongrel2, if not specified one will be created'''
    return ''

@ioc.config
def recv_spec():
    '''The receive address to use in communication with Mongrel2, see more details at "address_request" configuration'''
    return 'ipc:///tmp/response'

ioc.doc(server_type, '''
    "mongrel2" - mongrel2 server integration, Attention!!! this is not a full server the content will be delivered
                 by Mongrel2 server, so when you set this option please check the README.txt in the component sources
''')
ioc.doc(server_host, '''
    !!!Attention, if the mongrel2 server is selected this option is not used anymore, to change this option you need
    to alter the Mongrel2 configurations.
''')
ioc.doc(server_port, '''
    !!!Attention, if the mongrel2 server is selected this option is not used anymore, to change this option you need
    to alter the Mongrel2 configurations.
''')

try: from ..cdm.processor import server_provide_content
except ImportError: pass  # No CDM processor to stop from delivering content.
else:
    ioc.doc(server_provide_content, '''
    !!!Attention, if the mongrel2 server is selected this option will always be "false"
    ''')
    
    @ioc.before(server_provide_content, auto=False)
    def server_provide_content_force():
        if server_type() == 'mongrel2': support.force(server_provide_content, False)

# --------------------------------------------------------------------

@ioc.entity
def requestHandler():
    from ally.core.http.server.server_mongrel2 import RequestHandler
    b = RequestHandler(); yield b
    b.pathAssemblies = pathAssemblies()
    b.serverVersion = server_version()

# --------------------------------------------------------------------

@ioc.start
def runServer():
    if server_type() == 'mongrel2':
        from ally.core.http.server import server_mongrel2
        args = (workspace_path(), requestHandler(), send_ident(), send_spec(), recv_ident(), recv_spec())
        Thread(target=server_mongrel2.run, args=args).start()
