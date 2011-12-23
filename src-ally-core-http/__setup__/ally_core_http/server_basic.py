'''
Created on Nov 23, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Runs the basic web server.
'''

from ally import ioc
from ally.core.spec.server import Processors
from ally.core.http.support import server_basic
from threading import Thread

# --------------------------------------------------------------------

@ioc.onlyIf(_serverType='basic', doc='The type of the server to use')
@ioc.start
def runServer(handlers, encodersHeader,
              _serverPort:'The port on which the server will run'=80,
              _serverRoot:'The root URL for the rest server ex: rest/resources'='resources',
              _serverVersion:'The server version number'='AllyREST/0.1'):
    server_basic.RequestHandler.processors = Processors(*handlers)
    server_basic.RequestHandler.encodersHeader = encodersHeader
    if _serverRoot: server_basic.RequestHandler.urlRoot = '/' + _serverRoot
    server_basic.RequestHandler.server_version = _serverVersion
    
    Thread(target=server_basic.run, args=(server_basic.RequestHandler, _serverPort)).start()
