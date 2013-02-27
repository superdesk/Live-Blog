'''
Created on Feb 26, 2013

@package: superdesk security
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Processor that handles the invoking filtering for persist methods.
'''

from acl.api.filter import IAclFilter
from acl.core.impl.processor.resource_model_filter import \
    PermissionWithModelFilters
from acl.spec import Filter, Acl
from ally.api.operator.type import TypeProperty
from ally.container import wire
from ally.container.ioc import injected
from ally.container.support import setup
from ally.core.spec.resources import Node, Invoker, Path
from ally.design.processor.assembly import Assembly
from ally.design.processor.attribute import requires, defines
from ally.design.processor.context import Context
from ally.design.processor.execution import Processing, Chain
from ally.design.processor.handler import Handler, HandlerBranchingProceed
from ally.design.processor.processor import Included, Using
from ally.http.spec.codes import HEADER_ERROR, FORBIDDEN_ACCESS
from ally.http.spec.server import IDecoderHeader
from collections import Iterable, Callable
from gateway.api.gateway import Gateway
from itertools import chain
from superdesk.user.api.user import User
import logging

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

class AuthenticatedUserConfigurations:
    '''
    Provides the common header configurations to be used for persist filtering.
    '''
    
    nameHeader = 'X-Authenticated-User'
    # The header name used for placing the authenticated user into.
    separatorHeader = ':'
    # The separator used between the header name and header value.
    
    def __init__(self):
        assert isinstance(self.nameHeader, str), 'Invalid header name %s' % self.nameHeader
        assert isinstance(self.separatorHeader, str), 'Invalid header separator %s' % self.separatorHeader

# --------------------------------------------------------------------

class PermissionWithAuthenticated(Context):
    '''
    The permission context.
    '''
    # ---------------------------------------------------------------- Required
    modelsAuthenticated = requires(set)

class SolicitationPutHeader(Context):
    '''
    The solicitation context.
    '''
    # ---------------------------------------------------------------- Required
    userId = requires(int)
    permissions = requires(Iterable)
    
class ReplyPutHeader(Context):
    '''
    The reply context.
    '''
    # ---------------------------------------------------------------- Defined
    gateways = defines(Iterable)
    
class SolicitationGateways(Context):
    '''
    The persistence gateways reply context.
    '''
    # ---------------------------------------------------------------- Defined
    permissions = defines(Iterable)
    provider = defines(Callable)
    
class ReplyGateways(Context):
    '''
    The persistence gateways reply context.
    '''
    # ---------------------------------------------------------------- Required
    gateways = requires(Iterable)

# --------------------------------------------------------------------

@injected
@setup(Handler, name='gatewaysPersistenceFromPermissions')
class GatewaysPersistenceFromPermissions(HandlerBranchingProceed, AuthenticatedUserConfigurations):
    '''
    Processor that places the authenticated put header on the persistence gateways.
    '''
    
    assemblyGatewaysFromPermissions = Assembly; wire.entity('assemblyGatewaysFromPermissions')
    # The assembly used for creating the gateways from resource permissions.
    
    def __init__(self):
        assert isinstance(self.assemblyGatewaysFromPermissions, Assembly), \
        'Invalid assembly %s' % self.assemblyGatewaysFromPermissions
        super().__init__(Included(self.assemblyGatewaysFromPermissions).
                         using(solicitation=SolicitationGateways, reply=ReplyGateways))
        AuthenticatedUserConfigurations.__init__(self)
    
    def process(self, processing, Permission:PermissionWithAuthenticated, solicitation:SolicitationPutHeader,
                reply:ReplyPutHeader, **keyargs):
        '''
        @see: HandlerBranchingProceed.process
        
        Populate the persistence gateways.
        '''
        assert isinstance(processing, Processing), 'Invalid processing %s' % processing
        assert issubclass(Permission, PermissionWithAuthenticated), 'Invalid permission class %s' % Permission
        assert isinstance(solicitation, SolicitationPutHeader), 'Invalid solicitation %s' % solicitation
        assert isinstance(reply, ReplyPutHeader), 'Invalid reply %s' % reply
        
        authenticated, unprocessed = [], []
        for permission in solicitation.permissions:
            assert isinstance(permission, PermissionWithAuthenticated), 'Invalid permission %s' % permission
            if PermissionWithAuthenticated.modelsAuthenticated not in permission:
                # If there are no model filters then no need to process
                unprocessed.append(permission)
                continue
        
            assert isinstance(permission.modelsAuthenticated, set), \
            'Invalid model authenticated %s' % permission.modelsAuthenticated
            for propertyType in permission.modelsAuthenticated:
                assert isinstance(propertyType, TypeProperty), 'Invalid property type %s' % propertyType
                if propertyType.parent.clazz == User or issubclass(propertyType.parent.clazz, User):
                    authenticated.append(permission)
                    break
        
        solicitation.permissions = unprocessed
        if not authenticated: return  # No authenticated permissions to put the header to
        
        solGateways = processing.ctx.solicitation()
        assert isinstance(solGateways, SolicitationGateways)
        
        solGateways.permissions = authenticated
        solGateways.provider = solicitation.provider
        
        chainGateways = Chain(processing)
        chainGateways.process(**processing.fillIn(Permission=Permission, solicitation=solGateways, **keyargs)).doAll()
        replyGateways = chainGateways.arg.reply
        assert isinstance(replyGateways, ReplyGateways), 'Invalid reply %s' % replyGateways
        if ReplyGateways.gateways not in replyGateways: return  # No gateways generated
        
        assert isinstance(solicitation.userId, int), 'Invalid solicitation user id %s' % solicitation.userId
        headers = [self.separatorHeader.join((self.nameHeader, str(solicitation.userId)))]
   
        gateways = list(replyGateways.gateways)
        for gateway in gateways:
            assert isinstance(gateway, Gateway), 'Invalid gateway %s' % gateway
            if Gateway.PutHeaders not in gateway: gateway.PutHeaders = list(headers)
            else: gateway.PutHeaders.extend(headers)
        
        if ReplyPutHeader.gateways in reply:
            reply.gateways = chain(reply.gateways, gateways)
        else:
            reply.gateways = gateways

# --------------------------------------------------------------------

class Request(Context):
    '''
    The request context.
    '''
    # ---------------------------------------------------------------- Required
    decoderHeader = requires(IDecoderHeader)
    path = requires(Path)
    invoker = requires(Invoker)
    arguments = requires(dict)

class Response(Context):
    '''
    The response context.
    '''
    # ---------------------------------------------------------------- Defined
    code = defines(str)
    status = defines(int)
    isSuccess = defines(bool)
    text = defines(str)

class PermissionFilter(Context):
    '''
    The permission context.
    '''
    # ---------------------------------------------------------------- Required
    filtersModels = requires(list)

class ModelFilter(Context):
    '''
    The model filter context.
    '''
    # ---------------------------------------------------------------- Required
    inputName = requires(str)
    propertyName = requires(str)
    filters = requires(list)
    
class SolicitationFilter(Context):
    '''
    The solicitation context.
    '''
    # ---------------------------------------------------------------- Defined
    userId = defines(int, doc='''
    @rtype: integer
    The id of the user to create gateways for.
    ''')
    node = defines(Node, doc='''
    @rtype: Node
    The node to get the permissions for.
    ''')
    method = defines(int, doc='''
    @rtype: integer
    The method to get the permissions for.
    ''')
    types = defines(Iterable, doc='''
    @rtype: Iterable(TypeAcl)
    The ACL types to get the permissions for.
    ''')
    # ---------------------------------------------------------------- Required
    permissions = requires(Iterable)
    
# --------------------------------------------------------------------

@injected
@setup(Handler, name='invokingFilter')
class InvokingFilterHandler(HandlerBranchingProceed, AuthenticatedUserConfigurations):
    '''
    Processor that provides the model filtering.
    '''
    
    acl = Acl; wire.entity('acl')
    # The acl repository.
    assemblyPermissions = Assembly; wire.entity('assemblyPermissions')
    # The assembly used for getting the filter permissions.
    
    def __init__(self):
        assert isinstance(self.acl, Acl), 'Invalid acl repository %s' % self.acl
        assert isinstance(self.assemblyPermissions, Assembly), 'Invalid assembly %s' % self.assemblyPermissions
        HandlerBranchingProceed.__init__(self, Using(self.assemblyPermissions, Permission=PermissionFilter,
                                                     ModelFilter=ModelFilter, solicitation=SolicitationFilter))
        AuthenticatedUserConfigurations.__init__(self)

    def process(self, processing, request:Request, response:Response, **keyargs):
        '''
        @see: HandlerBranchingProceed.process
        
        Filter the invoking if is the case.
        '''
        assert isinstance(processing, Processing), 'Invalid processing %s' % processing
        assert isinstance(request, Request), 'Invalid request %s' % request
        assert isinstance(response, Response), 'Invalid response %s' % response
        if response.isSuccess is False: return  # Skip in case the response is in error
        
        assert isinstance(request.decoderHeader, IDecoderHeader), 'Invalid header decoder %s' % request.decoderHeader
        authenticated = request.decoderHeader.retrieve(self.nameHeader)
        if not authenticated: return  # Skip if no authenticated header is provided
        
        try: userId = int(authenticated)
        except ValueError:
            response.code, response.status, response.isSuccess = HEADER_ERROR
            response.text = 'Invalid value for \'%s\'' % self.nameHeader
            return
        assert isinstance(request.path, Path), 'Invalid path %s' % request.path
        assert isinstance(request.invoker, Invoker), 'Invalid invoker %s' % request.invoker
        assert isinstance(request.arguments, dict), 'Invalid arguments %s' % request.arguments
        
        solFilter = processing.ctx.solicitation()
        assert isinstance(solFilter, SolicitationFilter)
        
        solFilter.userId = userId
        solFilter.node = request.path.node
        solFilter.method = request.invoker.method
        solFilter.types = self.acl.types
        
        chainFilter = Chain(processing)
        chainFilter.process(**processing.fillIn(solicitation=solFilter, **keyargs)).doAll()
        solFilter = chainFilter.arg.solicitation
        assert isinstance(solFilter, SolicitationFilter), 'Invalid solicitation %s' % solFilter
        if SolicitationFilter.permissions not in solFilter: return  # No permissions available
        
        permissions = iter(solFilter.permissions)
        try: permission = next(permissions)
        except StopIteration: return  # There is no permission to filter by so nothing to do
        assert isinstance(permission, PermissionWithModelFilters), 'Invalid permission %s' % permission
        if __debug__:
            permissions = list(permissions)
            assert not permissions, 'To many permissions:\n%s\n, obtained beside:\n%s\n, for filtering' % \
            ('\n'.join(str(perm) for perm in permissions), permission)
        
        if PermissionWithModelFilters.filtersModels not in permission: return  # There is no model filters o nothing to do
        
        assert isinstance(permission.filtersModels, list), 'Invalid model filters %s' % permission.filtersModels
        for modelFilter in permission.filtersModels:
            assert isinstance(modelFilter, ModelFilter), 'Invalid model filter %s' % modelFilter
            assert isinstance(modelFilter.filters, list), 'Invalid filters %s' % modelFilter.filters
            modelObj = request.arguments.get(modelFilter.inputName)
            if modelObj is None: continue  # No model present to filter
            propertyObj = getattr(modelObj, modelFilter.propertyName)
            if propertyObj is None: continue  # No property value present to filter
            
            for filterAcl in modelFilter.filters:
                assert isinstance(filterAcl, Filter), 'Invalid filter %s' % filterAcl
                assert isinstance(filterAcl.filter, IAclFilter), 'Invalid filter service %s' % filterAcl.filter
                assert isinstance(filterAcl.authenticated, TypeProperty), 'Invalid authenticated %s' % filterAcl.authenticated
                clazz = filterAcl.authenticated.parent.clazz
                if clazz != User and not issubclass(clazz, User): continue  # Not a user authenticated type
                if not filterAcl.filter.isAllowed(userId, propertyObj):
                    response.code, response.status, response.isSuccess = FORBIDDEN_ACCESS
                    return
