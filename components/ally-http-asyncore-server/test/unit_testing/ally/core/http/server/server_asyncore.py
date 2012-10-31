'''
Created on Aug 24, 2011

@package: ally core http
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides unit testing for the asyncore server.
'''
from socket import socket

# Required in order to register the package extender whenever the unit test is run.
if True:
    import package_extender
    package_extender.PACKAGE_EXTENDER.setForUnitTest(True)

# --------------------------------------------------------------------

from ally.core.http.server.server_asyncore import RequestHandler, AsyncServer
import unittest

# --------------------------------------------------------------------

class TestAsyncoreServer(unittest.TestCase):

    def testRequest(self):
        server = AsyncServer(('localhost', 8080), RequestHandler)
        RequestHandler.pathProcessing = []
        rh = RequestHandler(server, socket(), ('localhost', 8080))
        
        
        datas = [b'GET /content/media_archive/thumbnail/original/DSC_0004.JPG HTTP/1.1\r\nHost: localhost:8080\r\n',
                 b'Connection: keep-alive\r\nCache-Control: max-age=0\r\nPragma: no-cache\r\nUser-Agent: Mozilla/5.0 ',
                 b'(X11; Linux x86_64) AppleWebKit/536.11 (KHTML, like Gecko) Ubuntu/12.04 Chromium/20.0.1132.47 Chrome',
                 b'/20.0.1132.47 Safari/536.11\r\nAccept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                 b'\r\nAccept-Encoding: gzip,deflate,sdch\r\nAccept-Language: en-US,en;q=0.8\r\nAccept-Charset: ISO-',
                 b'8859-1,utf-8;q=0.7,*;q=0.3\r\n\r\n']
        
        for data in datas: rh._handleReadData(data)

# --------------------------------------------------------------------

if __name__ == '__main__': unittest.main()

      
