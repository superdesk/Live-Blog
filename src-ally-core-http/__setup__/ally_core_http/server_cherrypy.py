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

# --------------------------------------------------------------------

serverHost = ioc.config(lambda:'127.0.0.1', 'The IP address to bind the server to')

serverThreadPool = ioc.config(lambda:10, 'The thread pool size for the server')

serverContentFolder = ioc.config(lambda:None, 'The folder from where the server should provide static content files, '
                                 'attention this will be available only if there is also a server root')

serverContentIndex = ioc.config(lambda:'index.html', 'The static folder index file')

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
    import cherrypy
    from ally.core.http.support import server_cherrypy
    
    cherrypy.config.update({'engine.autoreload.on': False})
    if serverRoot():
        class Root: pass
        root = Root()
        setattr(root, serverRoot(), requestHandler)
        requestHandler = root
        if serverContentFolder:
            requestHandler._cp_config = {
                                         'tools.staticdir.on' : True,
                                         'tools.staticdir.dir' : serverContentFolder(),
                                         'tools.staticdir.index' : serverContentIndex(),
                                         }
            
    args = requestHandler, serverHost(), serverPort(), serverThreadPool()
    Thread(target=server_cherrypy.run, args=args).start()
