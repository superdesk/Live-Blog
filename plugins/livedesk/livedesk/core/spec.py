'''
Created on Feb 12, 2013

@package: superdesk livedesk
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Ioan v. Pocol

Provides the specification classes for .
'''

import abc

# --------------------------------------------------------------------

class IBlogCollaboratorGroupCleanupService(metaclass=abc.ABCMeta):
    '''
    The cleanup blog collaborator groups service specification.
    '''

    @abc.abstractclassmethod
    def cleanExpired(self):
        '''
        Clean the expired blog collaborator groups.
        '''
