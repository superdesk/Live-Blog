'''
Created on Sep 9, 2012

@package: superdesk security
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the specification classes for authentication archives.
'''

import abc

# --------------------------------------------------------------------

class ICleanupService(metaclass=abc.ABCMeta):
    '''
    The cleanup service specification.
    '''

    @abc.abstractclassmethod
    def cleanExpired(self):
        '''
        Clean the expired authentications/sessions.
        '''
