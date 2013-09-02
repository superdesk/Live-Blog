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

AUTHENTICATED_NAME = 'authenticated_id'
# The name placed in the filter path to inject the authenticated user id into.
AUTHENTICATED_MARKER = '%%(%s)i' % AUTHENTICATED_NAME
# The marker placed in the filter path to inject the authenticated user id into.

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
