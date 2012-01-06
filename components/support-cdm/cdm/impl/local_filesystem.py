'''
Created on Jan 5, 2012

@package support - cdm
@copyright 2012 Sourcefabric o.p.s.
@license http: // www.gnu.org / licenses / gpl - 3.0.txt
@author: Mugur Rus

Contains the Content Delivery Manager implementation for local file system
'''

from cdm.spec import ICDM

# --------------------------------------------------------------------

class LocalFileSystemCDM(ICDM):
    '''
    @see ICDM (Content Delivery Manager interface)
    '''

    repositoryPath = str
    # The path where the content repository is placed

    def __init__(self):
        assert isinstance(self.repositoryPath, str), 'Invalid repository path %s' % self.repositoryPath

    def publishFromFile(self, path, filePath):
        '''
        @see ICDM.publishFromFile
        '''

    def publishContent(self, path, content):
        '''
        @see ICDM.publishContent
        '''

    def getURI(self, path, protocols):
        '''
        @see ICDM.getURI
        '''
