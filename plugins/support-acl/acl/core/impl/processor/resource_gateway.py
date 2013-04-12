'''
Created on Feb 21, 2013

@package: support acl
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Processor that creates Gateway objects based on resource permissions.
'''

from acl.api.filter import IAclFilter
from acl.spec import Filter
from acl.support.core.util_resources import processPattern
from ally.api.config import GET, DELETE, INSERT, UPDATE
from ally.api.operator.type import TypeService
from ally.api.type import typeFor
from ally.container import wire
from ally.container.ioc import injected
from ally.container.support import setup
from ally.core.spec.resources import Node, Path, Invoker
from ally.design.processor.attribute import defines, requires, optional
from ally.design.processor.context import Context
from ally.design.processor.handler import HandlerProcessorProceed, Handler
from ally.http.spec.server import HTTP_GET, HTTP_DELETE, HTTP_POST, HTTP_PUT, \
    IEncoderPath
from ally.support.core.util_resources import findNodesFor, propertyTypesOf, \
    ReplacerWithMarkers, pathForNode
from collections import Callable, Iterable
from gateway.api.gateway import Gateway
from itertools import chain
import logging

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

TO_HTTP_METHOD = {GET: HTTP_GET, DELETE: HTTP_DELETE, INSERT: HTTP_POST, UPDATE: HTTP_PUT}
# The mapping from configuration methods to http methods.

# --------------------------------------------------------------------

class PermissionResource(Context):
    '''
    The permission context.
    '''
    # ---------------------------------------------------------------- Optional
    values = optional(dict)
    putHeaders = optional(dict)
    navigate = optional(str)
    # ---------------------------------------------------------------- Required
    method = requires(int)
    path = requires(Path)
    invoker = requires(Invoker)
    filters = requires(list)
    
class Solicitation(Context):
    '''
    The solicitation context.
    '''
    # ---------------------------------------------------------------- Required
    encoderPath = requires(IEncoderPath, doc='''
    @rtype: IEncoderPath
    The path encoder used for encoding resource paths and patterns that will be used in gateways.
    ''')
    permissions = requires(Iterable)
    provider = requires(Callable, doc='''
    @rtype: callable(TypeProperty) -> string|None
    Callable used for getting the authenticated value for the provided property type.
    ''')

class Reply(Context):
    '''
    The reply context.
    '''
    # ---------------------------------------------------------------- Defined
    gateways = defines(Iterable, doc='''
    @rtype: Iterable(Gateway)
    The resource permissions generated gateways.
    ''')

# --------------------------------------------------------------------

@injected
@setup(Handler, name='gatewaysFromPermissions')
class GatewaysFromPermissions(HandlerProcessorProceed):
    '''
    Provides the handler that creates gateways based on resource permissions.
    '''
    
    resourcesRoot = Node; wire.entity('resourcesRoot')
    # The root node to find the filters in.
    separatorHeader = ':'
    # The separator used between the header name and header value.

    def __init__(self):
        assert isinstance(self.resourcesRoot, Node), 'Invalid root node %s' % self.resourcesRoot
        assert isinstance(self.separatorHeader, str), 'Invalid header separator %s' % self.separatorHeader
        super().__init__()
        
        self._cacheFilters = {}
        self.resourcesRoot.addStructureListener(self)

    def process(self, Permission:PermissionResource, solicitation:Solicitation, reply:Reply, **keyargs):
        '''
        @see: HandlerProcessorProceed.process
        
        Construct the gateways for permissions.
        '''
        assert issubclass(Permission, PermissionResource), 'Invalid permission class %s' % Permission
        assert isinstance(solicitation, Solicitation), 'Invalid solicitation %s' % solicitation
        assert isinstance(reply, Reply), 'Invalid reply %s' % reply
        assert isinstance(solicitation.encoderPath, IEncoderPath), 'Invalid encoder path %s' % solicitation.encoderPath
        assert isinstance(solicitation.permissions, Iterable), 'Invalid permissions %s' % solicitation.permissions
        assert callable(solicitation.provider), 'Invalid provider %s' % solicitation.provider
        
        gateways = self.processGateways(solicitation.permissions, solicitation.provider, solicitation.encoderPath)
        if reply.gateways is not None: reply.gateways = chain(reply.gateways, gateways)
        else: reply.gateways = gateways
        
    # ----------------------------------------------------------------
        
    def onChildAdded(self, node, child):
        '''
        @see: INodeChildListener.onChildAdded
        '''
        self._cacheFilters.clear()
    
    def onInvokerChange(self, node, old, new):
        '''
        @see: INodeInvokerListener.onInvokerChange
        '''
        self._cacheFilters.clear()
        
    # ----------------------------------------------------------------
    
    def processGateways(self, permissions, provider, encoder):
        '''
        Process the gateways for the provided permissions.
        
        @param permissions: Iterable(PermissionResource)
            The permissions to create the gateways for.
        @param provider: callable
            The callable used in solving the authenticated values.
        @param encoder: IEncoderPath
            The encoder path to be used for the gateways resource paths and patterns.
        @return: list[Gateway]
            The created gateways objects.
        '''
        assert isinstance(permissions, Iterable), 'Invalid permissions %s' % permissions
        assert isinstance(encoder, IEncoderPath), 'Invalid encoder path %s' % encoder
        
        gateways, gatewaysByPattern = [], {}
        for permission in permissions:
            assert isinstance(permission, PermissionResource), 'Invalid permission resource %s' % permission
            
            if PermissionResource.values in permission: values = permission.values
            else: values = None
            
            pattern, types = processPattern(permission.path, permission.invoker, encoder, values)
            filters = self.processFilters(types, permission.filters, provider, encoder)
            
            if PermissionResource.putHeaders in permission and permission.putHeaders is not None:
                putHeaders = [self.separatorHeader.join(item) for item in permission.putHeaders.items()]
            else: putHeaders = None
            
            if PermissionResource.navigate in permission: navigate = permission.navigate
            else: navigate = None
            
            gateway = gatewaysByPattern.get(pattern)
            if gateway and gateway.Filters == filters and gateway.PutHeaders == putHeaders and gateway.Navigate == navigate:
                gateway.Methods.append(TO_HTTP_METHOD[permission.method])
            else:
                gateway = Gateway()
                gateway.Methods = [TO_HTTP_METHOD[permission.method]]
                gateway.Pattern = pattern
                if filters: gateway.Filters = filters
                if putHeaders: gateway.PutHeaders = putHeaders
                if navigate: gateway.Navigate = navigate
                
                gatewaysByPattern[pattern] = gateway
                gateways.append(gateway)
        return gateways

    def processFilters(self, types, filters, provider, encoder):
        '''
        Process the filters into path filters.
        
        @param types: list[TypeProperty]
            The type properties that have groups in the gateway pattern, they must be in the proper order that they are
            captured.
        @param filters: Iterable(Filter)
            The filters to process.
        @param provider: callable
            The callable used in solving the authenticated values.
        @param encoder: IEncoderPath
            The encoder path to be used for the gateways resource paths and patterns.
        @return: dictionary{TypeProperty, tuple(string, dictionary{TypeProperty: string}}
            A dictionary containing {resource type, (marked path, {authenticated type: marker}}
        '''
        assert isinstance(types, list), 'Invalid types %s' % types
        assert isinstance(filters, Iterable), 'Invalid filters %s' % filter
        assert isinstance(encoder, IEncoderPath), 'Invalid encoder path %s' % encoder
        
        paths = None
        for rfilter in filters:
            assert isinstance(rfilter, Filter), 'Invalid filter %s' % rfilter
            occurence = types.count(rfilter.resource)
            if occurence > 1:
                log.error('Ambiguous resource filter type \'%s\', has to many occurrences in path types: %s', rfilter.resource,
                          ','.join(str(typ) for typ in types) if types else 'no types')
                continue
            elif occurence == 0:
                assert log.debug('Invalid resource filter type \'%s\', is not present in the path types: %s', rfilter.resource,
                                 ','.join(str(typ) for typ in types) if types else 'no types') or True
                continue
            
            path = self.processFilter(rfilter, provider, '{%s}' % (types.index(rfilter.resource) + 1), encoder)
            if path is not None:
                if paths is None: paths = [path]
                else: paths.append(path)
                
        return paths
    
    def processFilter(self, rfilter, provider, marker, encoder):
        '''
        Process the provided filter.
        
        @param rfilter: Filter
            The resource filter to process.
        @param provider: callable
            The callable used in solving the authenticated values.
        @param marker: string
            The resource marker to place in the filter path, this marker is used to identify the group in the gateway pattern.
        @param encoder: IEncoderPath
            The encoder path to be used for the gateways resource paths and patterns.
        @return: string|None
            The marked filter path, None if the filter is invalid.
        '''
        assert isinstance(rfilter, Filter), 'Invalid filter %s' % rfilter
        assert isinstance(rfilter.filter, IAclFilter), 'Invalid filter %s of %s' % (rfilter.filter, rfilter)
        typeService = typeFor(rfilter.filter)
        assert isinstance(typeService, TypeService), 'Invalid filter %s, is not a REST service' % rfilter.filter
        assert callable(provider), 'Invalid authenticated provider %s' % provider
        assert isinstance(marker, str), 'Invalid marker %s' % marker
        assert isinstance(encoder, IEncoderPath), 'Invalid encoder path %s' % encoder
        
        path = self._cacheFilters.get(typeService)
        if not path:
            nodes = findNodesFor(self.resourcesRoot, typeService, 'isAllowed')
            if not nodes:
                log.error('The filter service %s cannot be located in the resources tree', typeService)
                return
            if len(nodes) > 1:
                log.error('To many nodes for service %s in the resources tree, don\'t know which one to use', typeService)
                return
            
            node = nodes[0]
            assert isinstance(node, Node)
            path = pathForNode(node)
            
            if __debug__:
                # Just checking that the properties are ok
                propertyTypes = propertyTypesOf(path, node.get)
                assert len(propertyTypes) == 2, 'Invalid path %s for filter' % path
                indexAuth = propertyTypes.index(rfilter.authenticated)
                assert indexAuth >= 0, 'Invalid authenticated %s for path %s' % (rfilter.authenticated, path)
                indexRsc = propertyTypes.index(rfilter.resource)
                assert indexRsc >= 0, 'Invalid resource %s for path %s' % (rfilter.resource, path)
                assert indexAuth < indexRsc, 'Invalid path %s, improper order for types' % path
    
        assert isinstance(path, Path), 'Invalid path %s' % path
        valueAuth = provider(rfilter.authenticated)
        if valueAuth is None:
            log.error('The filter service %s has not authenticated value for %s', typeService, rfilter.authenticated)
            return
        
        return encoder.encode(path, invalid=ReplacerWithMarkers().register((valueAuth, marker)), quoted=False)
