'''
Created on Jan 5, 2012

@package support - cdm
@copyright 2012 Sourcefabric o.p.s.
@license http: // www.gnu.org / licenses / gpl - 3.0.txt
@author: Mugur Rus

Contains the Content Delivery Manager implementation for local file system
'''

from cdm.spec import ICDM, UnsupportedProtocol, PathNotFound
from ally.container.ioc import injected

import abc
import os
from zipfile import ZipFile, is_zipfile
from shutil import copyfile, copyfileobj, move, rmtree
from os.path import isdir, isfile, join, dirname, normpath, relpath
from io import StringIO, IOBase, TextIOBase
from tempfile import TemporaryDirectory

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
    @ivar serverURI: string
        The server root URI for the static content
    @ivar repositoryPath: string
        The directory where the file repository is
    @see IDelivery
    '''

    serverURI = str
    # The server root URI for the static content

    repositoryPath = str
    # The directory where the file repository is

    def __init__(self):
        assert isinstance(self.serverURI, str), \
            'Invalid server URI value %s' % self.serverURI
        assert isinstance(self.repositoryPath, str), \
            'Invalid repository directory value %s' % self.repositoryPath
        assert isdir(self.repositoryPath) \
            and os.access(self.repositoryPath, os.W_OK), \
            'Unable to access the repository directory %s' % self.repositoryPath

    def getRepositoryPath(self):
        '''
        @see IDelivery.getRepositoryPath
        '''
        return self.repositoryPath.rstrip('/')

    def getURI(self, repoFilePath):
        '''
        @see IDelivery.getURI
        '''
        assert isinstance(repoFilePath, str), 'Invalid repository file path value %s' % repoFilePath
        return self.serverURI + repoFilePath


@injected
class LocalFileSystemCDM(ICDM):
    '''
    @ivar delivery: IDelivery
        The delivery protocol

    @see ICDM (Content Delivery Manager interface)
    '''

    delivery = IDelivery
    # The delivery protocol

    def __init__(self):
        assert isinstance(self.delivery, IDelivery), 'Invalid delivery protocol %s' % self.delivery

    def publishFromFile(self, path, filePath):
        '''
        @see ICDM.publishFromFile
        '''
        assert isinstance(path, str) and len(path) > 0, 'Invalid content path %s' % path
        assert isinstance(filePath, str), 'Invalid file path value %s' % filePath
        dstFilePath = self._getItemPath(path)
        dstDir = dirname(dstFilePath)
        if not isdir(dstDir):
            os.makedirs(dstDir)
        if not isfile(filePath):
            # not a file, see if it's a entry in a zip file
            try:
                zipFilePath, inFilePath = self._getZipFilePath(filePath)
                zipFile = ZipFile(zipFilePath)
                fileInfo = zipFile.getinfo(inFilePath)
                if fileInfo.filename.endswith(os.sep):
                    raise Exception()
                copyfileobj(zipFile.open(inFilePath), open(dstFilePath, 'w+b'))
                return
            except:
                raise Exception('Invalid file path value %s' % filePath)
        assert os.access(filePath, os.R_OK), 'Unable to read the file path %s' % filePath
        if isfile(dstFilePath):
            srcFileStat = os.stat(filePath)
            dstFileStat = os.stat(dstFilePath)
            if srcFileStat.st_mtime <= dstFileStat.st_mtime:
                return
        copyfile(filePath, dstFilePath)

    def publishFromDir(self, path, dirPath):
        '''
        @see ICDM.publishFromDir
        '''
        assert isinstance(path, str) and len(path) > 0, 'Invalid content path %s' % path
        assert isinstance(dirPath, str), 'Invalid directory path value %s' % dirPath
        if not isdir(dirPath):
            # not a directory, see if it's a entry in a zip file
            try:
                zipFilePath, inDirPath = self._getZipFilePath(dirPath)
                zipFile = ZipFile(zipFilePath)
                if not inDirPath.endswith(os.sep):
                    inDirPath = inDirPath + os.sep
                fileInfo = zipFile.getinfo(inDirPath)
                if not fileInfo.filename.endswith(os.sep):
                    raise Exception()
                self._copyZipDir(zipFilePath, inDirPath, self._getItemPath(path))
                return
            except:
                raise Exception('Invalid directory path value %s' % dirPath)
        dirPath = normpath(dirPath)
        assert os.access(dirPath, os.R_OK), 'Unable to read the directory path %s' % dirPath
        for root, _dirs, files in os.walk(dirPath):
            relPath = relpath(root, dirPath)
            for file in files:
                publishPath = join(path, relPath.lstrip('/'), file)
                filePath = join(root, file)
                self.publishFromFile(publishPath, filePath)

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
        if isinstance(ioStream, TextIOBase):
            dstFile = open(dstFilePath, 'w')
        else:
            dstFile = open(dstFilePath, 'w+b')
        copyfileobj(ioStream, dstFile)
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
        dstFile = open(dstFilePath, 'w')
        streamContent = StringIO(content)
        copyfileobj(streamContent, dstFile)
        dstFile.close()

    def removePath(self, path):
        '''
        @see ICDM.removePath
        '''
        itemPath = self._getItemPath(path)
        if isdir(itemPath):
            rmtree(itemPath)
        elif isfile(itemPath):
            os.remove(itemPath)
        else:
            raise PathNotFound(path)

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
        if protocol != 'http':
            raise UnsupportedProtocol(protocol)
        return self.delivery.getURI(path)

    def _getItemPath(self, path):
        return join(self.delivery.getRepositoryPath(), path.lstrip('/'))

    def _getZipFilePath(self, filePath):
        assert isinstance(filePath, str), 'Invalid file path %s' % filePath
        endSep = filePath.endswith(os.sep)
        filePath = normpath(filePath)
        if endSep:
            filePath = filePath + os.sep
        if is_zipfile(filePath):
            return (filePath, '')
        subPath = filePath
        while len(subPath) > 0:
            if is_zipfile(subPath):
                return (subPath, filePath[len(subPath):].lstrip('/'))
            subPath = dirname(subPath)
        raise Exception('Invalid ZIP path %s' % filePath)

    def _copyZipDir(self, zipFilePath, inDirPath, path):
        zipFile = ZipFile(zipFilePath)
        if isdir(path):
            zipFileStat = os.stat(zipFilePath)
            dstDirStat = os.stat(path)
            if zipFileStat.st_mtime <= dstDirStat.st_mtime:
                return
            rmtree(path)
        entries = [ent for ent in zipFile.namelist() if ent.startswith(inDirPath)]
        tmpDir = TemporaryDirectory()
        zipFile.extractall(tmpDir.name, entries)
        tmpDirPath = join(tmpDir.name, inDirPath)
        os.makedirs(path)
        for entry in os.listdir(tmpDirPath):
            move(join(tmpDirPath, entry), path)


@injected
class LocalFileSystemLinkCDM(LocalFileSystemCDM):
    '''
    @see ICDM (Content Delivery Manager interface)
    '''
    _linkExt = '.link'

    _zipLinkExt = '.ziplink'

    _deletedExt = '.deleted'

    def publishFromFile(self, path, filePath):
        '''
        @see ICDM.publishFromFile
        '''
        try:
            self._publishFromFile(path, filePath)
        except Exception:
            raise IOError('Invalid file path value %s' % filePath)

    def publishFromDir(self, path, dirPath):
        '''
        @see ICDM.publishFromDir
        '''
        try:
            self._publishFromFile(path, dirPath)
        except:
            raise IOError('Invalid file path value %s' % dirPath)

    def removePath(self, path):
        '''
        @see ICDM.removePath
        '''
        entryPath = self._getItemPath(path)
        linkPath = entryPath
        try:
            while len(linkPath.lstrip('/')) > 0:
                subPath = entryPath[len(linkPath):].lstrip('/')
                if isfile(linkPath + self._linkExt):
                    linkFile = linkPath + self._linkExt
                    self._removeLink(path, entryPath, linkFile, subPath)
                    break
                if isfile(linkPath + self._zipLinkExt):
                    ziplinkFile = linkPath + self._zipLinkExt
                    self._removeZiplink(path, entryPath, ziplinkFile, subPath)
                    break
                linkPath = dirname(linkPath)
            else:
                raise PathNotFound(path)
        except PathNotFound:
            raise
        except:
            raise PathNotFound(path)
        if len(subPath.strip('/')) == 0 and isdir(linkPath):
            rmtree(linkPath)

    def _removeLink(self, path, entryPath, linkFile, subPath):
        with open(linkFile) as f:
            linkedPath = f.readline().strip()
            if isdir(linkedPath):
                if isfile(join(linkedPath, subPath)) or isdir(join(linkedPath, subPath)):
                    if not isdir(dirname(entryPath)):
                        os.makedirs(dirname(entryPath))
                    with open(entryPath.rstrip('/') + self._deletedExt, 'w') as _d: pass
                    if isdir(entryPath):
                        rmtree(entryPath)
                else:
                    raise PathNotFound(path)
            else:
                if len(subPath) > 0:
                    raise PathNotFound(path)
                else:
                    os.remove(linkFile)

    def _removeZiplink(self, path, entryPath, ziplinkFile, subPath):
        with open(ziplinkFile) as f:
            zipFilePath = f.readline().strip()
            inFilePath = f.readline().strip()
            zipFile = ZipFile(zipFilePath)
            zipFile.getinfo(join(inFilePath, subPath))
            if not isdir(dirname(entryPath)):
                os.makedirs(dirname(entryPath))
            with open(entryPath.rstrip('/') + self._deletedExt, 'w') as _d: pass
            if isdir(entryPath):
                rmtree(entryPath)

    def _createLinkToZipFile(self, path, zipFilePath, inFilePath):
        repFilePath = self._getItemPath(path) + self._zipLinkExt
        fHandler = open(repFilePath, 'w')
        fHandler.write(zipFilePath + "\n")
        fHandler.write(inFilePath + "\n")
        fHandler.close()

    def _createLinkToFileOrDir(self, path, filePath):
        repFilePath = self._getItemPath(path) + self._linkExt
        fHandler = open(repFilePath, 'w')
        fHandler.write(filePath + "\n")
        fHandler.close()

    def _publishFromFile(self, path, filePath):
        assert isinstance(path, str) and len(path) > 0, 'Invalid content path %s' % path
        assert isinstance(filePath, str), 'Invalid file path value %s' % filePath
        dstDir = dirname(self._getItemPath(path))
        if not isdir(dstDir):
            os.makedirs(dstDir)
        if isfile(filePath) or isdir(filePath):
            filePath = normpath(filePath)
            assert os.access(filePath, os.R_OK), 'Unable to read file path %s' % filePath
            self._createLinkToFileOrDir(path, filePath)
            return
        # not a file, see if it's a entry in a zip file
        zipFilePath, inFilePath = self._getZipFilePath(filePath)
        assert isfile(zipFilePath) and os.access(zipFilePath, os.R_OK), \
            'Unable to read file path %s' % filePath
        zipFile = ZipFile(zipFilePath)
        zipFile.getinfo(inFilePath)
        self._createLinkToZipFile(path, zipFilePath, inFilePath)
