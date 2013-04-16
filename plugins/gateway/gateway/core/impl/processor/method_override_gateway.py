'''
Created on Feb 21, 2013

@package: support acl
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Processor that adds default Gateway objects.
'''

from ally.container import wire
from ally.container.ioc import injected
from ally.container.support import setup
from ally.design.processor.attribute import defines
from ally.design.processor.context import Context
from ally.design.processor.handler import HandlerProcessorProceed, Handler
from ally.http.spec.server import HTTP_DELETE, HTTP_POST, HTTP_GET, HTTP_PUT
from ally.support.api.util_service import copy
from collections import Iterable
from gateway.api.gateway import Gateway

# --------------------------------------------------------------------

class Reply(Context):
    '''
    The reply context.
    '''
    # ---------------------------------------------------------------- Defined
    gateways = defines(Iterable, doc='''
    @rtype: Iterable(Gateway)
    The gateways to have the override method gateways populated.
    ''')

# --------------------------------------------------------------------

@injected
@setup(Handler, name='registerMethodOverride')
class RegisterMethodOverride(HandlerProcessorProceed):
    '''
    Provides the method override gateways, basically support for @see: MethodOverrideHandler.
    '''
    pattern_xmethod_override = 'X\-HTTP\-Method\-Override\\:[\s]*%s[\s]*(?i)'; wire.config('pattern_xmethod_override', doc='''
    The header pattern for the method override, needs to contain '%s' where the value will be placed.
    ''')
    methods_override = {
                        HTTP_DELETE: [HTTP_GET],
                        HTTP_PUT: [HTTP_POST],
                        }; wire.config('methods_override', doc='''
    A dictionary containing as a key the overrided method and as a value the methods that are overriden.
    ''')
    
    def __init__(self):
        '''
        Construct the populate method override filter.
        '''
        assert isinstance(self.pattern_xmethod_override, str), \
        'Invalid method override pattern %s' % self.pattern_xmethod_override
        assert isinstance(self.methods_override, dict), 'Invalid methods override %s' % self.methods_override
        super().__init__()
    
    def process(self, reply:Reply, **keyargs):
        '''
        @see: HandlerProcessorProceed.process
        
        Adds the default gateways.
        '''
        assert isinstance(reply, Reply), 'Invalid reply %s' % reply
        if reply.gateways is None: return
        
        reply.gateways = self.register(reply.gateways)
            
    # ----------------------------------------------------------------
            
    def register(self, gateways):
        '''
        Register the method override gateways based on the provided gateways.
        '''
        assert isinstance(gateways, Iterable), 'Invalid gateways %s' % gateways
        for gateway in gateways:
            assert isinstance(gateway, Gateway), 'Invalid gateway %s' % gateway
            yield gateway
            if not gateway.Methods: continue
            
            methods, overrides = set(), set()
            for method in gateway.Methods:
                override = self.methods_override.get(method)
                if override:
                    methods.add(method)
                    overrides.update(override)
            
            # If the override methods are already declared as methods we don't need to declare them anymore
            if methods.union(overrides).issubset(gateway.Methods): continue
                
            ogateway = Gateway()
            copy(gateway, ogateway, exclude=('Methods',))
            ogateway.Methods = list(overrides)
            if Gateway.Headers not in ogateway: ogateway.Headers = []
            for method in methods:
                ogateway.Headers.append(self.pattern_xmethod_override % method)
            yield ogateway
