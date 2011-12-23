'''
Created on Nov 23, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Runs the cherry py web server.
'''

from ally import ioc
from ally.core.spec.server import Processors
from threading import Thread

# --------------------------------------------------------------------

@ioc.onlyIf(_serverType='cherrypy')
def requestHandler(handlers, encodersHeader, _serverVersion):
    from ally.core.http.support.server_cherrypy import RequestHandler
    b = RequestHandler(); yield b
    b.processors = Processors(*handlers)
    b.encodersHeader = encodersHeader
    b.serverVersion = _serverVersion

# --------------------------------------------------------------------

@ioc.onlyIf(_serverType='cherrypy')
@ioc.start
def runServer(requestHandler,
              _serverPort, _serverRoot,
              _serverHost:'The IP address to bind the server to'='127.0.0.1',
              _serverThreadPool:'The thread pool size for the server'=10,
              _serverContentFolder:'The folder from where the server should provide static content files, attention'
              'this will be available only if there is also a server root'=None,
              _serverContentIndex:'The static folder index file'='index.html'):
    
    import cherrypy
    from ally.core.http.support import server_cherrypy
    
    cherrypy.config.update({'engine.autoreload.on': False})
    if _serverRoot:
        class Root: pass
        root = Root()
        setattr(root, _serverRoot, requestHandler)
        requestHandler = root
        if _serverContentFolder:
            requestHandler._cp_config = {
                                         'tools.staticdir.on' : True,
                                         'tools.staticdir.dir' : _serverContentFolder,
                                         'tools.staticdir.index' : _serverContentIndex,
                                         }
            
    args = requestHandler, _serverHost, _serverPort, _serverThreadPool
    Thread(target=server_cherrypy.run, args=args).start()
