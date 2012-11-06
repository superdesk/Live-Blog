'''
Created on Nov 23, 2011

@package: ally core http
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Runs the Mongrel2 web server.
'''

from ..ally_core_http import server_type, server_version
from ..ally_core_http.processor import pathAssemblies
from ally.container import ioc, support
from threading import Thread

# --------------------------------------------------------------------

ioc.doc(server_type, '''
    "mongrel2" - mongrel2 server integration, Attention!!! this is not a full server the content will be delivered
                 by Mongrel2 server, so when you set this option please check the README.txt in the component sources
''')

try: from ..cdm.processor import server_provide_content
except ImportError: pass  # No CDM processor to stop from delivering content.
else:
    ioc.doc(server_provide_content, '''
    !!!Attention, if the mongrel2 server is selected this option will always be "false"
    ''')
    
    @ioc.before(server_provide_content, False)
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
        args = (requestHandler(),)
        Thread(target=server_mongrel2.run, args=args).start()
