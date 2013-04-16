'''
Created on Feb 7, 2013

@package: gateway service
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the gateway specification.
'''

from ally.support.util import immut
import abc
import re

# --------------------------------------------------------------------

class Gateway:
    '''
    Provides the gateway data.
    '''
    __slots__ = ('pattern', 'headers', 'methods', 'filters', 'errors', 'host', 'protocol', 'navigate', 'putHeaders')
    
    def __init__(self, obj):
        '''
        Construct the gateway based on the provided dictionary object.
        @see: gateway-http/gateway.http.gateway
        
        @param obj: dictionary{string: string|list[string]}
            The dictionary used for defining the gateway object, the object as is defined from response.
        '''
        assert isinstance(obj, dict), 'Invalid object %s' % obj
        
        pattern = obj.get('Pattern')
        if pattern:
            assert isinstance(pattern, str), 'Invalid pattern %s' % pattern
            self.pattern = re.compile(pattern)
        else: self.pattern = None
        
        headers = obj.get('Headers', immut()).get('Headers')
        if headers:
            assert isinstance(headers, list), 'Invalid headers %s' % headers
            if __debug__:
                for header in headers: assert isinstance(header, str), 'Invalid header value %s' % header
            self.headers = [re.compile(header) for header in headers]
        else: self.headers = None
        
        methods = obj.get('Methods', immut()).get('Methods')
        if methods:
            assert isinstance(methods, list), 'Invalid methods %s' % methods
            if __debug__:
                for method in methods: assert isinstance(method, str), 'Invalid method value %s' % method
            self.methods = set(method.upper() for method in methods)
        else: self.methods = None
            
        self.filters = obj.get('Filters', immut()).get('Filters')
        if __debug__ and self.filters:
            assert isinstance(self.filters, list), 'Invalid filters %s' % self.filters
            for item in self.filters: assert isinstance(item, str), 'Invalid filter value %s' % item
            
        errors = obj.get('Errors', immut()).get('Errors')
        if errors:
            assert isinstance(errors, list), 'Invalid errors %s' % errors
            self.errors = set()
            for error in errors:
                try: self.errors.add(int(error))
                except ValueError: raise ValueError('Invalid error value \'%s\'' % error)
        else: self.errors = None
                
        self.host = obj.get('Host')
        assert not self.host or isinstance(self.host, str), 'Invalid host %s' % self.host
        
        self.protocol = obj.get('Protocol')
        assert not self.protocol or isinstance(self.protocol, str), 'Invalid protocol %s' % self.protocol
        
        self.navigate = obj.get('Navigate')
        assert not self.navigate or isinstance(self.navigate, str), 'Invalid navigate %s' % self.navigate
        
        putHeaders = obj.get('PutHeaders', immut()).get('PutHeaders')
        if putHeaders:
            assert isinstance(putHeaders, list), 'Invalid put headers %s' % putHeaders
            if __debug__:
                for putHeader in putHeaders:
                    assert isinstance(putHeader, str), 'Invalid put header value %s' % putHeader
                    assert len(putHeader.split(':')), 'Invalid put header value %s' % putHeader
            self.putHeaders = [putHeader.split(':') for putHeader in putHeaders]
        else: self.putHeaders = None

class Match:
    '''
    The find match.
    '''
    __slots__ = ('gateway', 'groupsURI')
    
    def __init__(self, gateway, groupsURI):
        '''
        Construct the match.
        
        @param gateway: Gateway
            The gateway represented by the match.
        @param groupsURI: tuple(string)
            The groups that match the URI.
        '''
        assert isinstance(gateway, Gateway), 'Invalid gateway %s' % gateway
        assert isinstance(groupsURI, tuple), 'Invalid groups %s' % groupsURI
        self.gateway = gateway
        self.groupsURI = groupsURI

class IRepository(metaclass=abc.ABCMeta):
    '''
    The gateways repository.
    '''
    
    @abc.abstractmethod
    def find(self, method=None, headers=None, uri=None, error=None):
        '''
        Finds the gateway object filtered by the provided parameters.

        @param method: string|None
            The method to be matched for the gateway.
        @param headers: dictionary{String, string}|None
            The headers to be matched for the gateway.
        @param uri: string|None
            The URI that needs to match the gateway patterns.
        @param error: integer|None
            The error to be matched for the gateway. If an error is provided then only the matchings that resolve errors will
            be returned.
        @return: Match|None
            The found match, None if there is no gateway to respect the provided parameters.
        '''
    
    @abc.abstractmethod
    def allowsFor(self, headers=None, uri=None):
        '''
        Provides the allowed methods for the provided parameters.
        
        @param headers: dictionary{String, string}|None
            The headers to be matched for the gateway.
        @param uri: string|None
            The URI that needs to match the gateway patterns.
        @return: set(string)
            The list of allowed methods.
        '''
    
    @abc.abstractmethod
    def obtainCache(self, identifier):
        '''
        Obtains the cache dictionary for the provided identifier.
        
        @param identifier: object
            The identifier used for identifying the cache.
        @return: dictionary{...}
            The cache dictionary, if none available for the identifier then one will be created.
        '''
