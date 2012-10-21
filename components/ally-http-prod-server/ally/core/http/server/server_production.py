'''
Created on Jul 8, 2011

@package: ally core http
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the production web server based on the python build in http server that runs on multiple processors.
'''

from ally.core.http.server.server_basic import RequestHandler
from ally.core.http.spec.server import RequestHTTP, ResponseHTTP, \
    RequestContentHTTP, ResponseContentHTTP
from ally.design.processor import Assembly, ONLY_AVAILABLE, CREATE_REPORT
from http.server import HTTPServer
from multiprocessing import cpu_count, Pipe, Process
from multiprocessing.reduction import reduce_handle, rebuild_handle
from socketserver import ForkingMixIn
import logging
import re
import socket

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

class HTTPProductionServer1(ForkingMixIn, HTTPServer):
    '''
    @see: ForkingMixIn, HTTPServer
    Provides multiprocess handling of requests.
    '''
    
    def __init__(self, host, processes):
        '''
        Constructs the multiprocess server.
        '''
        assert isinstance(processes, int), 'Invalid processes pool size %s' % processes
        
        self.max_children = processes
        HTTPServer.__init__(self, host, RequestHandler)

class HTTPProductionServer(HTTPServer):
    '''
    @see: HTTPServer
    Provides multiprocess handling of requests.
    '''
    
    def __init__(self, *args, counts):
        '''
        Constructs the multiprocess server.
        '''
        assert isinstance(counts, int), 'Invalid processes pool size %s' % counts
        super().__init__(*args)
        
        processes, pipes = [], []
        for k in range(0, counts):
            parent, child = Pipe()
            process = Process(name='Process %s' % k, target=self.prepareServer, args=(child,))
            process.daemon = True
            processes.append(process)
            pipes.append(parent)
            
            process.start()
        self.processes = process
        self.pipes = pipes
        self.current = 0
        
    def process_request(self, request, address):
        '''
        @see: HTTPServer.process_request
        '''
        request = reduce_handle(request.fileno())
        self.pipes[self.current].send((request, address))
        self.current += 1
        if self.current >= len(self.pipes): self.current = 0
        
    def server_close(self):
        '''
        @see: HTTPServer.server_close
        '''
        super().server_close()
        for pipe in self.pipes: pipe.send(None)
        for process in self.processes: process.join()

    # ----------------------------------------------------------------

    def prepareServer(self, pipe):
        '''
        Prepare in a process the request handling.
        '''
        while True:
            data = pipe.recv()
            if data is None: break
            
            request, address = data
            request = rebuild_handle(request)
            request = socket.fromfd(request, socket.AF_INET, socket.SOCK_STREAM)
            try:
                self.finish_request(request, address)
                self.shutdown_request(request)
            except:
                self.handle_error(request, address)
                self.shutdown_request(request)

# --------------------------------------------------------------------

def run(pathAssemblies, server_version, host='', port=80, processes='auto'):
    '''
    Run the basic server.
    
    @param pathAssemblies: list[(regex, Assembly)]
        A list that contains tuples having on the first position a string pattern for matching a path, and as a value 
        the assembly to be used for creating the context for handling the request for the path.
    '''
    assert isinstance(pathAssemblies, list), 'Invalid path assemblies %s' % pathAssemblies
    RequestHandler.server_version = server_version
    RequestHandler.pathProcessing = []
    for pattern, assembly in pathAssemblies:
        assert isinstance(pattern, str), 'Invalid pattern %s' % pattern
        assert isinstance(assembly, Assembly), 'Invalid assembly %s' % assembly

        processing, report = assembly.create(ONLY_AVAILABLE, CREATE_REPORT,
                                             request=RequestHTTP, requestCnt=RequestContentHTTP,
                                             response=ResponseHTTP, responseCnt=ResponseContentHTTP)

        log.info('Assembly report for pattern \'%s\':\n%s', pattern, report)
        RequestHandler.pathProcessing.append((re.compile(pattern), processing))
    
    if processes == 'auto': processes = cpu_count()
    
    try:
        server = HTTPProductionServer((host, port), RequestHandler, counts=processes)
        print('=' * 50, 'Started HTTP REST API server...')
        server.serve_forever()
    except KeyboardInterrupt:
        print('=' * 50, '^C received, shutting down server')
        server.socket.close()
        return
    except:
        log.exception('=' * 50 + ' The server has stooped')
        try: server.socket.close()
        except: pass
