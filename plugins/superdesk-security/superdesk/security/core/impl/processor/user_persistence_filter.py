'''
Created on Feb 26, 2013

@package: superdesk security
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Processor that handles the invoking filtering for persist methods.
'''

from acl.api.filter import IAclFilter
from acl.spec import Filter, Acl
from ally.api.operator.type import TypeProperty
from ally.container import wire
from ally.container.ioc import injected
from ally.container.support import setup
from ally.core.spec.resources import Invoker, Path
from ally.design.processor.assembly import Assembly
from ally.design.processor.attribute import requires, defines
from ally.design.processor.branch import Branch
from ally.design.processor.context import Context
from ally.design.processor.execution import Processing
from ally.design.processor.handler import Handler, HandlerBranching, \
    HandlerProcessor
from ally.http.spec.codes import HEADER_ERROR, FORBIDDEN_ACCESS, CodedHTTP
from ally.http.spec.headers import HeaderRaw, HeadersRequire
from collections import Iterable
from superdesk.user.api.user import User
import logging

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

AUTHENTICATED_USER = HeaderRaw('X-Authenticated-User')
# The header used for placing the authenticated user into.

# --------------------------------------------------------------------

class PermissionWithAuthenticated(Context):
    '''
    The permission context.
    '''
    # ---------------------------------------------------------------- Defined
    putHeaders = defines(dict, doc='''
    @rtype: dictionary{string: string}
    The put headers dictionary.
    ''')
    # ---------------------------------------------------------------- Required
    modelsAuthenticated = requires(set)

class SolicitationPutHeader(Context):
    '''
    The solicitation context.
    '''
    # ---------------------------------------------------------------- Required
    userId = requires(int)
    permissions = requires(Iterable)

# --------------------------------------------------------------------

@injected
@setup(Handler, name='userPersistenceForPermissions')
class UserPersistenceForPermissions(HandlerProcessor):
    '''
    Processor that places the authenticated put header on the persistence permissions.
    '''
    
    def process(self, chain, Permission:PermissionWithAuthenticated, solicitation:SolicitationPutHeader, **keyargs):
        '''
        @see: HandlerProcessor.process
        
        Populate the persistence permissions put headers.
        '''
        assert issubclass(Permission, PermissionWithAuthenticated), 'Invalid permission class %s' % Permission
        assert isinstance(solicitation, SolicitationPutHeader), 'Invalid solicitation %s' % solicitation
        assert isinstance(solicitation.userId, int), 'Invalid solicitation user id %s' % solicitation.userId
        assert isinstance(solicitation.permissions, Iterable), 'Invalid permissions %s' % solicitation.permissions
        
        solicitation.permissions = self.processPermissions(solicitation.permissions, str(solicitation.userId))
        
    # ----------------------------------------------------------------
    
    def processPermissions(self, permissions, userId):
        '''
        Process the permissions user authenticated put headers.
        '''
        assert isinstance(userId, str), 'Invalid user id %s' % userId
        for permission in permissions:
            assert isinstance(permission, PermissionWithAuthenticated), 'Invalid permission %s' % permission
            if permission.modelsAuthenticated is not None:
                assert isinstance(permission.modelsAuthenticated, set), \
                'Invalid model authenticated %s' % permission.modelsAuthenticated
                for propertyType in permission.modelsAuthenticated:
                    assert isinstance(propertyType, TypeProperty), 'Invalid property type %s' % propertyType
                    if propertyType.parent.clazz == User or issubclass(propertyType.parent.clazz, User):
                        if permission.putHeaders is None: permission.putHeaders = {}
                        AUTHENTICATED_USER.put(permission.putHeaders, userId)
                        break
            yield permission
    
# --------------------------------------------------------------------

class Request(HeadersRequire):
    '''
    The request context.
    '''
    # ---------------------------------------------------------------- Required
    path = requires(Path)
    invoker = requires(Invoker)
    arguments = requires(dict)

class Response(CodedHTTP):
    '''
    The response context.
    '''
    # ---------------------------------------------------------------- Defined
    text = defines(str)

class PermissionFilter(Context):
    '''
    The permission context.
    '''
    # ---------------------------------------------------------------- Required
    path = requires(Path)
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
class InvokingFilterHandler(HandlerBranching):
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
        HandlerBranching.__init__(self, Branch(self.assemblyPermissions).
                                  using(Permission=PermissionFilter, ModelFilter=ModelFilter, solicitation=SolicitationFilter))

    def process(self, chain, processing, request:Request, response:Response, **keyargs):
        '''
        @see: HandlerBranching.process
        
        Filter the invoking if is the case.
        '''
        assert isinstance(processing, Processing), 'Invalid processing %s' % processing
        assert isinstance(request, Request), 'Invalid request %s' % request
        assert isinstance(response, Response), 'Invalid response %s' % response
        if response.isSuccess is False: return  # Skip in case the response is in error
        
        authenticated = AUTHENTICATED_USER.fetch(request)
        if not authenticated: return  # Skip if no authenticated header is provided
        
        try: userId = int(authenticated)
        except ValueError:
            HEADER_ERROR.set(response)
            response.text = 'Invalid value for \'%s\'' % self.nameHeader
            return
        assert isinstance(request.path, Path), 'Invalid path %s' % request.path
        assert isinstance(request.invoker, Invoker), 'Invalid invoker %s' % request.invoker
        assert isinstance(request.arguments, dict), 'Invalid arguments %s' % request.arguments
        
        solFilter = processing.ctx.solicitation()
        assert isinstance(solFilter, SolicitationFilter)
        
        solFilter.userId = userId
        solFilter.method = request.invoker.method
        solFilter.types = self.acl.types
        
        solFilter = processing.executeWithAll(solicitation=solFilter, **keyargs).solicitation
        assert isinstance(solFilter, SolicitationFilter), 'Invalid solicitation %s' % solFilter
        if solFilter.permissions is None: return  # No permissions available
        
        permissions = []
        for permission in solFilter.permissions:
            assert isinstance(permission, PermissionFilter), 'Invalid permission %s' % permission
            if permission.path.node == request.path.node and permission.filtersModels:
                permissions.append(permission)
        if not permissions: return  # There is no permission to filter by so nothing to do
        assert len(permissions > 1), 'To many permissions:\n%s\n, for filtering' % '\n'.join(str(perm) for perm in permissions)
        permission = permissions[0]
        
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
                if not filterAcl.filter.isAllowed(userId, propertyObj): return FORBIDDEN_ACCESS.set(response)
