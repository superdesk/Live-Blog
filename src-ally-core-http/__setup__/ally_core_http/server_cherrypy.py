'''
Created on Nov 23, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Runs the cherry py web server.
'''

from . import serverVersion, serverRoot, serverPort
from .encoder_header import encodersHeader
from .processor import handlers
from ally import ioc
from ally.core.spec.server import Processors
from threading import Thread
from __setup__.ally_core_http import serverType

# --------------------------------------------------------------------

@ioc.config
def serverHost() -> str:
    '''The IP address to bind the server to'''
    return '127.0.0.1'

@ioc.config
def serverThreadPool() -> int:
    '''The thread pool size for the server'''
    return 10

@ioc.config
def serverContentFolder() -> str:
    '''The folder from where the server should provide static content files, attention this will be available only if
    there is also a server root'''
    return None

@ioc.config
def serverContentIndex() -> str: 
    '''The static folder index file'''
    return 'index.html'

@ioc.entity
def requestHandler():
    from ally.core.http.support.server_cherrypy import RequestHandler
    b = RequestHandler(); yield b
    b.processors = Processors(*handlers())
    b.encodersHeader = encodersHeader()
    b.serverVersion = serverVersion()

# --------------------------------------------------------------------
                             
@ioc.start
def runServer():
    if serverType() == 'cherrypy':
        import cherrypy
        from ally.core.http.support import server_cherrypy
        
        cherrypy.config.update({'engine.autoreload.on': False})
        handler = requestHandler()
        if serverRoot():
            class Root: pass
            root = Root()
            setattr(root, serverRoot(), handler)
            handler = root
            if serverContentFolder:
                handler._cp_config = {
                                      'tools.staticdir.on' : True,
                                      'tools.staticdir.dir' : serverContentFolder(),
                                      'tools.staticdir.index' : serverContentIndex(),
                                      }
                
        args = handler, serverHost(), serverPort(), serverThreadPool()
        Thread(target=server_cherrypy.run, args=args).start()
