'''
Created on Sep 9, 2012

@package: ally authentication
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the service for authentication support.
'''

import abc

# --------------------------------------------------------------------

class IAuthenticationSupport(metaclass=abc.ABCMeta):
    '''
    The authentication support service.
    '''

    @abc.abstractclassmethod
    def authenticate(self, identifier, attributes, arguments):
        '''
        Process the authentication.
        
        @param identifier: string
            The authentication identifier.
        @param attributes: dictionary{string, string}
            The attributes that are used with the provided identifier.
        @param arguments: dictionary{Type:object}
            The dictionary containing the arguments values. The key is represented by the Type that needs an
            authenticated value.
        @return: boolean
            True if the authentication process has been successful.
        '''
