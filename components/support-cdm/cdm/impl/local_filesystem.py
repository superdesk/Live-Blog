'''
Created on Jan 5, 2012

@package support - cdm
@copyright 2012 Sourcefabric o.p.s.
@license http: // www.gnu.org / licenses / gpl - 3.0.txt
@author: Mugur Rus

Contains the Content Delivery Manager implementation for local file system
'''

from cdm.spec import ICDM

import abc
import os
from os.path import isdir, isfile, join

# --------------------------------------------------------------------

class IDelivery(metaclass = abc.ABCMeta):
    '''
    Delivery protocol interface
    '''

    @abc.abstractmethod
    def getURI(self, repoFilePath):
        '''
        Returns the URI for a given repository file path in the context of
        this delivery protocol.
        '''


class HTTPDelivery(IDelivery):
    '''
    @see IDelivery
    '''

    documentRoot = str
    # The HTTP server document root directory path

    port = int
    # The HTTP server listening port

    repositorySubdir = str
    # The sub-directory of the document root where the file repository is

    def __init__(self):
        assert isinstance(self.documentRoot, str), 'Invalid document root value %s' % self.documentRoot
        assert isdir(self.documentRoot) and os.access(self.documentRoot, os.W_OK), \
            'Unable to access the document root directory %s' % self.documentRoot
        assert isinstance(self.port, int)
        assert isinstance(self.repositorySubdir, str), 'Invalid repository sub-directory value %s' % self.documentRoot
        if len(self.repositorySubdir) > 0:
            repositoryPath = join(self.documentRoot, self.repositorySubdir)
            assert isdir(repositoryPath) and os.access(repositoryPath, os.W_OK), \
                'Unable to access the repository directory %s' % self.documentRoot

    def getURI(self, repoFilePath):
        assert isinstance(repoFilePath, str), 'Invalid repository file path value %s' % repoFilePath


class LocalFileSystemCDM(ICDM):
    '''
    @see ICDM (Content Delivery Manager interface)
    '''

    repositoryPath = str
    # The path where the content repository is placed

    def __init__(self):
        assert isinstance(self.repositoryPath, str), 'Invalid repository path %s' % self.repositoryPath
        assert isdir(self.repositoryPath) and os.access(self.repositoryPath, os.W_OK), \
            'Unable to access repository directory %s' % self.repositoryPath

    def publishFromFile(self, path, filePath):
        '''
        @see ICDM.publishFromFile
        '''
        assert isinstance(path, str), 'Invalid content path %s' % path
        assert isinstance(filePath, str), 'Invalid file path value %s' % path
        assert isfile(filePath) and os.access(filePath, os.R_OK), \
            'Unable to read file path %s' % filePath

    def publishContent(self, path, content):
        '''
        @see ICDM.publishContent
        '''
        assert isinstance(path, str), 'Invalid content path %s' % path
        assert isinstance(content, str), 'Invalid content string %s' % path

    def getURI(self, path, protocols = ('http', 'https')):
        '''
        @see ICDM.getURI
        '''
        assert isinstance(path, str), 'Invalid content path %s' % path
        assert isinstance(protocols, tuple), 'Invalid protocols %s' % path
