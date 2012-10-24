'''
Created on Oct 23, 2012

@package: ally core http
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the wsgiref web server support.
'''

from wsgiref.simple_server import make_server
import logging

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

def run(requestHandler, host='127.0.0.1', port=80):
    server = make_server(host, port, requestHandler)
    
    try:
        print('=' * 50, 'Started HTTP REST API server...')
        server.serve_forever()
    except KeyboardInterrupt:
        print('=' * 50, '^C received, shutting down server')
        server.server_close()
    except:
        log.exception('=' * 50 + ' The server has stooped')
        try: server.server_close()
        except: pass
    
