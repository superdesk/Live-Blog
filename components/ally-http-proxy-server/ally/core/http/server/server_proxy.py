'''
Created on Jul 8, 2011

@package: ally core http
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the production web server based on the python build in http server that runs on multiple processors.
'''

from asyncore import dispatcher
from collections import deque
from multiprocessing import Pipe, Process
from sched import scheduler
from threading import Thread
import asyncore
import logging
import socket
import time

# --------------------------------------------------------------------

log = logging.getLogger(__name__)
    
# --------------------------------------------------------------------

class ProxyServer(dispatcher):
    '''
    The proxy server that waits for the incoming connections.
    '''

    def __init__(self, address, proxies):
        '''
        Construct the proxy sever.
        '''
        dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.proxies = deque(proxies)
        self.address = address
        self.bind(address)
        self.listen(5)
    
    def handle_accept(self):
        ProxyReceiver(self, self.proxies[0], *self.accept())
        self.proxies.rotate()

class ProxyReceiver(dispatcher):
    '''
    Receives data from the proxy.
    '''
    bufferSize = 4096
    
    def __init__(self, server, address, connection, fromAddress):
        '''
        '''
        dispatcher.__init__ (self, connection)
        self.server = server
        self.address = address
        self.sender = ProxySender(self, address)
    
    def handle_read(self):
        try: data = self.recv(self.bufferSize)
        except socket.error:
            self.handle_error()
            return
        self.sender.send(data)
        
    def handle_close (self):
        self.sender.close()
        self.close()

class ProxySender(dispatcher):
    '''
    Sends data to the proxied server.
    '''
    bufferSize = 4096

    def __init__(self, receiver, address):
        '''
        '''
        dispatcher.__init__(self)
        self.receiver = receiver
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect(address)
    
    def handle_read(self):
        try: data = self.recv(self.bufferSize)
        except socket.error:
            self.handle_error()
            return
        self.receiver.send(data)
        
    def handle_close (self):
        self.receiver.close()
        self.close()

# -----------------------------------------------------------------

def prepareServer(server, port, pipe, timeout):
    '''
    Prepare the process in a processor.
    '''
    serverThread = Thread(name='Server thread for port %s' % port, target=server, args=(port,))
    serverThread.daemon = True
    serverThread.start()
    while True:  # Waiting notifications for determining when the proxied server should stop.
        if not pipe.poll(timeout): break
        else: pipe.recv()

# --------------------------------------------------------------------

def run(proxiedServer, proxiedPorts, host='0.0.0.0', port=80, timeout=1):
    '''
    Run the proxy server.
    
    @param proxiedServer: callable(integer)
        A callable that spawns a server for the provided port.
    @param proxiedPorts: list[integer]
        The list of ports to use for the spawned proxies.
    '''
    processes, pipes = [], []
        
    schedule = scheduler(time.time, time.sleep)
    def pingProcesses():
        for pipe in pipes: pipe.send(True)
        schedule.enter(timeout, 1, pingProcesses, ())
    schedule.enter(timeout, 1, pingProcesses, ())
    scheduleRunner = Thread(name='Ping processes thread', target=schedule.run)
    scheduleRunner.daemon = True
    scheduleRunner.start()
    
    for proxiedPort in proxiedPorts:
        receiver, sender = Pipe(False)
        
        args = proxiedServer, proxiedPort, receiver, 2 * timeout
        process = Process(name='Process server on port %s' % proxiedPort, target=prepareServer, args=args)
        processes.append(process)
        pipes.append(sender)
        
        process.start()
    
    ProxyServer((host, port), [(host, proxiedPort) for proxiedPort in proxiedPorts])
    
    try:
        print('=' * 50, 'Started HTTP PROXY server...')
        asyncore.loop()
    except KeyboardInterrupt: print('=' * 50, '^C received, shutting down server')
    except: log.exception('=' * 50 + ' The server has stooped')
