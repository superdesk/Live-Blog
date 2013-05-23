'''
Created on Jan 12, 2013

@package: superdesk security
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

The filter used to check if the authenticated identifier is allowed for the resource identifier.
'''

from acl.api.domain_filter import aliasFilter
from acl.api.filter import IsAllowed, IAclFilter
from ally.api.config import service, call, GET
from superdesk.user.api.user import User

# --------------------------------------------------------------------

@aliasFilter
class Authenticated(User):
    '''
    User authenticated model.
    '''

@aliasFilter
class IsAuthenticated(IsAllowed):
    '''
    User authenticated model.
    '''
    
# --------------------------------------------------------------------

@service
class IAuthenticatedFilterService(IAclFilter):
    '''
    Provides the service that checks if the authenticated identifier is same with the resource identifier.
    '''
    
    @call(method=GET)
    def isAllowed(self, authenticated:Authenticated.Id, resourceIdentifier:User.Id) -> IsAuthenticated.HasAccess:
        '''
        @see: IAclFilter.isAllowed
        '''
