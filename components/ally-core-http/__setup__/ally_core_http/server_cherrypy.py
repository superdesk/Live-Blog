'''
Created on Nov 23, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Runs the cherry py web server.
'''

from . import server_type, server_version, server_root, server_port
from .encoder_header import encodersHeader
from .processor import handlers
from ally.container import ioc
from ally.core.spec.server import Processors
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

@ioc.config
def server_content_folder() -> str:
    '''The folder from where the server should provide static content files, attention this will be available only if
    there is also a server root'''
    return None

@ioc.config
def server_content_index() -> str: 
    '''The static folder index file'''
    return 'index.html'

@ioc.entity
def requestHandler():
    from ally.core.http.support.server_cherrypy import RequestHandler
    b = RequestHandler(); yield b
    b.processors = Processors(*handlers())
    b.encodersHeader = encodersHeader()
    b.serverVersion = server_version()

# --------------------------------------------------------------------
                             
@ioc.start
def runServer():
    if server_type() == 'cherrypy':
        import cherrypy
        from ally.core.http.support import server_cherrypy
        
        cherrypy.config.update({'engine.autoreload.on': False})
        handler = requestHandler()
        if server_root():
            class Root: pass
            root = Root()
            setattr(root, server_root(), handler)
            handler = root
            if server_content_folder():
                handler._cp_config = {
                                      'tools.staticdir.on' : True,
                                      'tools.staticdir.dir' : server_content_folder(),
                                      'tools.staticdir.index' : server_content_index(),
                                      }
                
        args = handler, server_host(), server_port(), server_thread_pool()
        Thread(target=server_cherrypy.run, args=args).start()
