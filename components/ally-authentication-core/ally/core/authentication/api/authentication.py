'''
Created on July 3, 2012

@package: ally authentication
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mugur Rus

Provides authentication API.
'''

import abc

# --------------------------------------------------------------------

class IAuthenticate(metaclass=abc.ABCMeta):
    '''
    Authentication interface
    '''

    @abc.abstractmethod
    def getUserKey(self, userName):
        '''
        Returns the user secret key.

        @param userName: string
            The user login name for which to return the secret key.
        @return: string
            Returns the user key.
        @raise InputException: If the user login name is not valid.
        '''
