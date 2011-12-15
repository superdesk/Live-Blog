'''
Created on Aug 18, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the configurations for the pyro server.
'''

import Pyro4
from ally.api.configure import serviceFor
from ally.api.operator import Service
from threading import Thread
from ally.util import simpleName

# --------------------------------------------------------------------

services = None
# To be injected before setup, provides the services to be used by the server.

# --------------------------------------------------------------------

class DaemonRun(Thread):
    
    def __init__(self, daemonPyro):
        self.daemonPyro = daemonPyro
        Thread.__init__(self)
        self.setDaemon(True)
    
    def run(self):
        self.daemonPyro.requestLoop()

    
def setup():
    try:
        import cPickle as pickle
    except ImportError:
        import pickle
    pickle.HIGHEST_PROTOCOL = 2
    # Need to set the protocol to 2 because we need it compatible with older python versions
    if not services: raise AssertionError('Set on "services" the services to be used')
    daemon = Pyro4.core.Daemon(port=50000)
    
    for service in services:
        api = serviceFor(service)
        assert isinstance(api, Service)
        uri = daemon.register(service, objectId=simpleName(api.serviceClass))
        print('Registered %r under URI: %s' % (simpleName(api.serviceClass), uri.asString()))
    
    DaemonRun(daemon).start()
