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
from collections import deque
from concurrent.futures.thread import ThreadPoolExecutor
from http.server import HTTPServer
from multiprocessing import cpu_count, Pipe, Process
from multiprocessing.reduction import reduce_handle, rebuild_handle
from sched import scheduler
from threading import Thread
import logging
import re
import socket
import time

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

class HTTPProductionServer(HTTPServer):
    '''
    @see: HTTPServer
    Provides multiprocess handling of requests.
    '''
    
    def __init__(self, serverAddress, RequestHandlerClass, *args, counts, threads, timeout):
        '''
        Constructs the multiprocess server.RequestHandlerClass
        '''
        assert isinstance(counts, int), 'Invalid processes pool size %s' % counts
        super().__init__(serverAddress, None)
        
        processes, pipes = [], []
        
        schedule = scheduler(time.time, time.sleep)
        def pingProcesses():
            for pipe in pipes: pipe.send(True)
            schedule.enter(timeout, 1, pingProcesses, ())
        schedule.enter(timeout, 1, pingProcesses, ())
        scheduleRunner = Thread(name='Ping processes thread', target=schedule.run)
        scheduleRunner.daemon = True
        scheduleRunner.start()
        
        for k in range(0, counts):
            receiver, sender = Pipe(False)
            
            args = RequestHandlerClass, receiver, threads, 2 * timeout
            process = Process(name='Process %s' % k, target=prepareServer, args=args)
            processes.append(process)
            pipes.append(sender)
            
            process.start()

        self.processes = processes
        self.pipes = deque(pipes)
        
    def process_request(self, request, address):
        '''
        @see: HTTPServer.process_request
        '''
        pipe = self.pipes[0]
        self.pipes.rotate()
        
        pipe.send((reduce_handle(request.fileno()), address))
        
    def server_close(self):
        '''
        @see: HTTPServer.server_close
        '''
        super().server_close()
        for pipe in self.pipes: pipe.send(None)
        for process in self.processes: process.join()
    
# --------------------------------------------------------------------

def prepareServer(RequestHandlerClass, pipe, threads, timeout):
    '''
    Prepare in a process the request handling.
    '''
    def process(request, address):
        RequestHandlerClass(request, address, None)
        try: request.shutdown(socket.SHUT_WR)
        except socket.error: pass  # some platforms may raise ENOTCONN here
        request.close()
    
    pool = ThreadPoolExecutor(threads)
    while True:
        if not pipe.poll(timeout): break
        else:
            data = pipe.recv()
            if data is None: break
            elif data is True: continue
            
            requestfd, address = data
            request = socket.fromfd(rebuild_handle(requestfd), socket.AF_INET, socket.SOCK_STREAM)
            
            pool.submit(process, request, address)
            
    pool.shutdown(False)

# --------------------------------------------------------------------

def run(pathAssemblies, server_version, host='0.0.0.0', port=80, processes='auto', threads=20, timeout=1):
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
        server = HTTPProductionServer((host, port), RequestHandler, counts=processes, threads=threads, timeout=timeout)
        print('=' * 50, 'Started HTTP REST API server...')
        server.serve_forever()
    except KeyboardInterrupt:
        print('=' * 50, '^C received, shutting down server')
        server.server_close()
    except:
        log.exception('=' * 50 + ' The server has stooped')
        try: server.server_close()
        except: pass
