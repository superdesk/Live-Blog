'''
Created on Nov 23, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Runs the basic web server.
'''

from ..ally_core_http import serverType, serverRoot, serverVersion, serverPort
from ..ally_core_http.processor import handlers
from .encoder_header import encodersHeader
from ally.container import ioc
from ally.core.http.support import server_basic
from ally.core.spec.server import Processors
from threading import Thread

# --------------------------------------------------------------------

@ioc.start
def runServer():
    if serverType() == 'basic':
        server_basic.RequestHandler.processors = Processors(*handlers())
        server_basic.RequestHandler.encodersHeader = encodersHeader()
        if serverRoot(): server_basic.RequestHandler.urlRoot = '/' + serverRoot()
        server_basic.RequestHandler.server_version = serverVersion()
    
        Thread(target=server_basic.run, args=(server_basic.RequestHandler, serverPort())).start()
