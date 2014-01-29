'''
Created on Jan 20, 2014

@package: livedesk
@copyright: 2014 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Ioan v. Pocol

Manage the version of the embed, return the current version and increment the revision version.
'''

from ally.api.config import service, call, model, UPDATE


@model
class Version:
    '''
    Provides the version details.
    '''
    Major = int
    Minor = int
    Revision = int

# --------------------------------------------------------------------

@service
class IVersionService:
    '''
    Provides the version service.
    '''

    @call
    def get(self) -> Version:
        '''
        Provides the version details.
        '''

    @call(method=UPDATE, webName='incrementRevision')
    def incrementRevision(self):
        '''
        Update the version by incrementing the revision value and then republish the version.js file.
        '''
        
    @call(method=UPDATE, webName='resetRevision')
    def resetRevision(self):
        '''
        Update the version by reseting the revision value and then republish the version.js file.    
        '''
