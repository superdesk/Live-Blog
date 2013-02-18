'''
Created on Sep 9, 2012

@package: superdesk security
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the specification classes for authentication.
'''

import abc

# --------------------------------------------------------------------

class ICleanupService(metaclass=abc.ABCMeta):
    '''
    Specification for cleanup service for authentications/sessions.
    '''

    @abc.abstractclassmethod
    def cleanExpired(self):
        '''
        Clean the expired authentications/sessions.
        '''

# --------------------------------------------------------------------

class IGatewaysFilter(metaclass=abc.ABCMeta):
    '''
    Specification for gateway filter. A gateway filter has the ability to manipulate the users gateways.
    The order in which the filters are executed is crucial since the first filter will provide the gateways for the second
    filter and so on.
    '''
    
    def filter(self, gateways, userId):
        '''
        Filter the provided gateways.
        
        @param gateways: Iterable(Gateway)
            The gateways to filter.
        @param userId: integer
            The user id that this gateways belongs to.
        @return: Iterable(Gateway)
            The filtered gateways.
        '''
