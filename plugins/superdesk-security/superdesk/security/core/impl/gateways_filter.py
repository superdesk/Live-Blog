'''
Created on Feb 18, 2013

@package: superdesk security
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Implementations for @see: IGatewaysFilter for general purposes.
'''

from ..spec import IGatewaysFilter
from ally.container.ioc import injected
from ally.http.spec.server import HTTP_GET, HTTP_POST, HTTP_DELETE, HTTP_PUT
from ally.support.api.util_service import copy
from collections import Iterable
from gateway.http.api.gateway import Gateway
from gateway.http.support.util_gateway import gatewayFrom
from itertools import chain

# --------------------------------------------------------------------

class RegisterDefaultGateways(IGatewaysFilter):
    '''
    Register default gateways into the users gateways.
    Basically this gateways will be available for any authenticated user.
    '''
    
    def __init__(self, configuration):
        '''
        Construct the default gateways register.
        
        @param configuration: list[dictionary{..}]
            The configuration to create gateways for.
        '''
        assert isinstance(configuration, list), 'Invalid gateways configuration %s' % configuration
        
        self._gateways = []
        for config in configuration: self._gateways.append(gatewayFrom(config))
        
    def filter(self, gateways, userId):
        '''
        @see: IGatewaysFilter.filter
        '''
        assert isinstance(gateways, Iterable), 'Invalid gateways %s' % gateways
        return chain(self._gateways, gateways)

@injected
class PopulateMethodOverride(IGatewaysFilter):
    '''
    Provides the method override gateways, basically support for @see: MethodOverrideHandler. This is done regardless of the
    user id.
    '''
    
    patternXMethodOverride = 'X\-HTTP\-Method\-Override\\:[\s]*%s[\s]*(?i)'
    # The header pattern for the method override, needs to contain '%s' where the value will be placed.
    methodsOverride = {
                       HTTP_DELETE: [HTTP_GET],
                       HTTP_PUT: [HTTP_POST],
                       }
    # A dictionary containing as a key the overrided method and as a value the methods that are overriden.
    
    def __init__(self):
        '''
        Construct the populate method override filter.
        '''
        assert isinstance(self.patternXMethodOverride, str), 'Invalid method override pattern %s' % self.patternXMethodOverride
        assert isinstance(self.methodsOverride, dict), 'Invalid methods override %s' % self.methodsOverride
        
    def filter(self, gateways, userId):
        '''
        @see: IGatewaysFilter.filter
        '''
        assert isinstance(gateways, Iterable), 'Invalid gateways %s' % gateways
        for gateway in gateways:
            assert isinstance(gateway, Gateway), 'Invalid gateway %s' % gateway
            yield gateway
            if not gateway.Methods: continue
            
            methods, overrides = set(), set()
            for method in gateway.Methods:
                override = self.methodsOverride.get(method)
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
                ogateway.Headers.append(self.patternXMethodOverride % method)
            yield ogateway
