'''
Created on Jan 14, 2013

@package: support acl
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

API specifications for exposed filter.
'''

from .domain_filter import modelFilter
import abc

# --------------------------------------------------------------------

@modelFilter
class IsAllowed:
    '''
    Provides the model that provides the allowed access.
    '''
    HasAccess = bool

# --------------------------------------------------------------------

# No query

# --------------------------------------------------------------------

class IAclFilter(metaclass=abc.ABCMeta):
    '''
    Provides the acl filter API. The acl filter has the duty to confirm that a provided authenticated
    identifier has access to another resource identifier. This API needs to be wrapped by a configured service
    in order to be able to expose the filtering as a service.
    '''
    
    @abc.abstractmethod
    def isAllowed(self, authenticated, resource):
        '''
        Checks if the resource identifier is allowed for the provided authenticated identifier.
        
        @param authenticated: object
            The authenticated identifier to be checked against.
        @param resource: object
            The resource identifier to be checked if it has access.
            
        @return: boolean
            True if the authenticated identifier is allowed to access the provided resource identifier.
        '''

