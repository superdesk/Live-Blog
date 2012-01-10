'''
Created on Jan 5, 2012

@package support - cdm
@copyright 2012 Sourcefabric o.p.s.
@license http: // www.gnu.org / licenses / gpl - 3.0.txt
@author: Mugur Rus

Contains the Content Delivery Manager implementation for local file system
'''

from cdm.spec import ICDM, UnsupportedProtocol
from ally.container.ioc import injected

import abc
import os
import shutil
from os.path import isdir, isfile, join, dirname
from urllib.parse import ParseResult
from io import StringIO, IOBase

# --------------------------------------------------------------------

class IDelivery(metaclass = abc.ABCMeta):
    '''
    Delivery protocol interface
    '''

    @abc.abstractmethod
    def getRepositoryPath(self):
        '''
        Returns the absolute path of the file repository.

        @return: The file repository path
        @rtype: string
        '''

    @abc.abstractmethod
    def getURI(self, repoFilePath):
        '''
        Returns the URI of a certain content identified by the repository path.

        @param repoFilePath: string
                The path of the content item. This is a unique
                     identifier of the item.
        @return: The URI of the content
        @rtype: string
        '''


@injected
class HTTPDelivery(IDelivery):
    '''
    @see IDelivery
    '''

    serverName = str
    # The HTTP server name

    documentRoot = str
    # The HTTP server document root directory path

    port = int
    # The HTTP server listening port

    repositorySubdir = str
    # The sub-directory of the document root where the file repository is

    def __init__(self):
        assert isinstance(self.serverName, str), 'Invalid server name value %s' % self.serverName
        assert isinstance(self.documentRoot, str) and isdir(self.documentRoot), \
            'Invalid document root directory %s' % self.documentRoot
        assert isinstance(self.port, int) and self.port > 0 and self.port <= 65535, \
            'Invalid port value %s' % self.port
        assert isinstance(self.repositorySubdir, str), \
            'Invalid repository sub-directory value %s' % self.documentRoot
        assert isdir(self.getRepositoryPath()) \
            and os.access(self.getRepositoryPath(), os.W_OK), \
            'Unable to access the repository directory %s' % self.documentRoot

    def getRepositoryPath(self):
        '''
        @see IDelivery.getRepositoryPath
        '''
        return join(self.documentRoot, self.repositorySubdir).rstrip('/')

    def getURI(self, repoFilePath):
        '''
        @see IDelivery.getURI
        '''
        assert isinstance(repoFilePath, str), 'Invalid repository file path value %s' % repoFilePath
        netloc = self.serverName
        if self.port is not None and self.port != 80:
            netloc = netloc + ':' + str(self.port)
        if len(self.repositorySubdir) > 0:
            path = self.repositorySubdir.lstrip('/')
        else:
            path = ''
        path = path + '/' + repoFilePath.lstrip('/')
        uriObj = ParseResult(scheme = 'http', netloc = netloc, path = path,
            params = '', query = '', fragment = '')
        return uriObj.geturl()


@injected
class LocalFileSystemCDM(ICDM):
    '''
    @see ICDM (Content Delivery Manager interface)
    '''

    delivery = IDelivery
    # The delivery protocol

    def __init__(self):
        pass

    def _getItemPath(self, path):
        return join(self.delivery.getRepositoryPath(), path.lstrip('/'))

    def publishFromFile(self, path, filePath):
        '''
        @see ICDM.publishFromFile
        '''
        assert isinstance(path, str) and len(path) > 0, 'Invalid content path %s' % path
        assert isinstance(filePath, str), 'Invalid file path value %s' % filePath
        assert isfile(filePath) and os.access(filePath, os.R_OK), \
            'Unable to read file path %s' % filePath
        dstFilePath = self._getItemPath(path)
        if isfile(dstFilePath):
            srcFileStat = os.stat(filePath)
            dstFileStat = os.stat(dstFilePath)
            if (srcFileStat.st_mtime <= dstFileStat.st_mtime):
                return
        dstDir = dirname(dstFilePath)
        if not isdir(dstDir):
            os.makedirs(dstDir)
        shutil.copyfile(filePath, dstFilePath)

    def publishFromStream(self, path, ioStream):
        '''
        @see ICDM.publishFromStream
        '''
        assert isinstance(path, str), 'Invalid content path %s' % path
        assert isinstance(ioStream, IOBase), 'Invalid content string %s' % ioStream
        dstFilePath = self._getItemPath(path)
        dstDir = dirname(dstFilePath)
        if not isdir(dstDir):
            os.makedirs(dstDir)
        dstFile = open(dstFilePath, 'w+')
        shutil.copyfileobj(ioStream, dstFile)
        dstFile.close()

    def publishContent(self, path, content):
        '''
        @see ICDM.publishContent
        '''
        assert isinstance(path, str), 'Invalid content path %s' % path
        assert isinstance(content, str), 'Invalid content string %s' % content
        dstFilePath = self._getItemPath(path)
        dstDir = dirname(dstFilePath)
        if not isdir(dstDir):
            os.makedirs(dstDir)
        dstFile = open(dstFilePath, 'w+')
        streamContent = StringIO(content)
        shutil.copyfileobj(streamContent, dstFile)
        dstFile.close()

    def getSupportedProtocols(self):
        '''
        @see ICDM.getSupportedProtocols
        '''
        return ('http',)

    def getURI(self, path, protocol = 'http'):
        '''
        @see ICDM.getURI
        '''
        assert isinstance(path, str), 'Invalid content path %s' % path
        assert isinstance(protocol, str), 'Invalid protocol %s' % protocol
        if (protocol != 'http'):
            raise UnsupportedProtocol(protocol)
        return self.delivery.getURI(path)
