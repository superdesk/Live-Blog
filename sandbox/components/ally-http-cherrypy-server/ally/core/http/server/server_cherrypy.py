'''
Created on Nov 23, 2011

@package: ally core http
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the cherry py web server support.
'''

from cherrypy.wsgiserver import wsgiserver3
import logging

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

def run(requestHandler, host='127.0.0.1', port=80, requestQueueSize=500, serverName='localhost'):
    server = wsgiserver3.CherryPyWSGIServer((host, port), requestHandler, request_queue_size=requestQueueSize,
                                            server_name=serverName)
    try:
        print('=' * 50, 'Started HTTP REST API server...')
        server.start()
    except KeyboardInterrupt:
        print('=' * 50, '^C received, shutting down server')
        server.stop()
    except:
        log.exception('=' * 50 + ' The server has stooped')
        try: server.stop()
        except: pass
    
