'''
Created on Jan 12, 2013

@package: superdesk security
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

The implementation for the authenticated security filter user service.
'''

from ally.container.support import setup
from superdesk.security.api.filter_authenticated import \
    IAuthenticatedFilterService

# --------------------------------------------------------------------

@setup(IAuthenticatedFilterService, name='authenticatedFilterService')
class AuthenticatedFilterService(IAuthenticatedFilterService):
    '''
    Provides the service that checks if the authenticated identifier is same with the resource identifier.
    '''
    
    def isAllowed(self, authenticated, resourceIdentifier):
        '''
        @see: IAuthenticatedFilterService.isAllowed
        '''
        return authenticated == resourceIdentifier
