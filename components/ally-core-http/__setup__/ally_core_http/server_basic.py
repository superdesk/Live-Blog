'''
Created on Nov 23, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Runs the basic web server.
'''

from . import server_type, server_version, server_port
from ..ally_core.processor import resourcesHandlers, contentHandlers
from .encoder_header import encodersHeader
from ally.container import ioc
from ally.core.http.support import server_basic
from ally.core.spec.server import Processors
from threading import Thread
import re

# --------------------------------------------------------------------

@ioc.start
def runServer():
    if server_type() == 'basic':
        server_basic.RequestHandler.requestPaths = []
        server_basic.RequestHandler.requestPaths.append((re.compile('^resources/'), Processors(*resourcesHandlers())))
        server_basic.RequestHandler.requestPaths.append((re.compile('^content/'), Processors(*contentHandlers())))
        server_basic.RequestHandler.encodersHeader = encodersHeader()
        server_basic.RequestHandler.server_version = server_version()

        Thread(target = server_basic.run, args = (server_basic.RequestHandler, server_port())).start()
