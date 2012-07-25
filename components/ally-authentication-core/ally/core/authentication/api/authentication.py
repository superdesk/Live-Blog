'''
Created on July 3, 2012

@package: ally authentication
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mugur Rus

Provides authentication API.
'''

import abc
from functools import partial
from ally.api.config import model

# --------------------------------------------------------------------

DOMAIN = 'Authenticate/'
modelAuthenticate = partial(model, domain=DOMAIN)

# --------------------------------------------------------------------

@modelAuthenticate(id='Token')
class LoginToken:
    Token = str

@modelAuthenticate(id='UserName')
class User:
    UserName = str
    FirstName = str
    LastName = str
    Address = str
    EMail = str

@modelAuthenticate(id='Session')
class Session(User):
    Session = str
    Session = str

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
        @raise InputError: If the user login name is not valid.
        '''

    @abc.abstractmethod
    def getUserData(self, userName):
        '''
        Returns the user data.

        @param userName: string
            The user login name for which to return the user data.
        @return: User
            Returns the user key.
        @raise InputError: If the user login name is not valid.
        '''
