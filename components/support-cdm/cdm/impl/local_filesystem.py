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
from zipfile import ZipFile
from shutil import copyfile, copyfileobj, move, rmtree
from os.path import isdir, isfile, join, dirname, normpath, relpath
from io import StringIO
from tempfile import TemporaryDirectory
from ally.zip.util_zip import ZIPSEP, normOSPath, normZipPath, getZipFilePath
import logging

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

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
        self.repositoryPath = normOSPath(self.repositoryPath)

    def getRepositoryPath(self):
        '''
        @see IDelivery.getRepositoryPath
        '''
        return self.repositoryPath.rstrip(os.sep)

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
        if not isinstance(filePath, str) and hasattr(filePath, 'read'):
            return self._publishFromFileObj(path, filePath)
        assert isinstance(filePath, str), 'Invalid file path value %s' % filePath
        path, dstFilePath = self._validatePath(path)
        dstDir = dirname(dstFilePath)
        if not isdir(dstDir):
            os.makedirs(dstDir)
        if not isfile(filePath):
            # not a file, see if it's a entry in a zip file
            zipFilePath, inFilePath = getZipFilePath(filePath, self.delivery.getRepositoryPath())
            zipFile = ZipFile(zipFilePath)
            fileInfo = zipFile.getinfo(inFilePath)
            if fileInfo.filename.endswith(ZIPSEP):
                raise IOError('Trying to publish a file from a ZIP directory path: %s' % fileInfo.filename)
            if not self._isSyncFile(zipFilePath, dstFilePath):
                copyfileobj(zipFile.open(inFilePath), open(dstFilePath, 'w+b'))
                assert log.debug('Success publishing ZIP file %s (%s) to path %s', inFilePath, zipFilePath, path) or True
            return
        assert os.access(filePath, os.R_OK), 'Unable to read the file path %s' % filePath
        if not self._isSyncFile(filePath, dstFilePath):
            copyfile(filePath, dstFilePath)
            assert log.debug('Success publishing file %s to path %s', filePath, path) or True

    def publishFromDir(self, path, dirPath):
        '''
        @see ICDM.publishFromDir
        '''
        assert isinstance(path, str) and len(path) > 0, 'Invalid content path %s' % path
        assert isinstance(dirPath, str), 'Invalid directory path value %s' % dirPath
        path, fullPath = self._validatePath(path)
        if not isdir(dirPath):
            # not a directory, see if it's a entry in a zip file
            zipFilePath, inDirPath = getZipFilePath(dirPath, self.delivery.getRepositoryPath())
            zipFile = ZipFile(zipFilePath)
            if not inDirPath.endswith(ZIPSEP):
                inDirPath = inDirPath + ZIPSEP
            fileInfo = zipFile.getinfo(inDirPath)
            if not fileInfo.filename.endswith(ZIPSEP):
                raise IOError('Trying to publish a file from a ZIP directory path: %s' % fileInfo.filename)
            self._copyZipDir(zipFilePath, inDirPath, fullPath)
            assert log.debug('Success publishing ZIP dir %s (%s) to path %s', inDirPath, zipFilePath, path) or True
            return
        dirPath = normpath(dirPath)
        assert os.access(dirPath, os.R_OK), 'Unable to read the directory path %s' % dirPath
        for root, _dirs, files in os.walk(dirPath):
            relPath = relpath(root, dirPath)
            for file in files:
                publishPath = join(path, relPath.lstrip(os.sep), file)
                filePath = join(root, file)
                self.publishFromFile(publishPath, filePath)
            assert log.debug('Success publishing directory %s to path %s', dirPath, path) or True

    def publishContent(self, path, content):
        '''
        @see ICDM.publishContent
        '''
        assert isinstance(path, str), 'Invalid content path %s' % path
        assert isinstance(content, str), 'Invalid content string %s' % content
        path, dstFilePath = self._validatePath(path)
        dstDir = dirname(dstFilePath)
        if not isdir(dstDir):
            os.makedirs(dstDir)
        with open(dstFilePath, 'w') as dstFile:
            copyfileobj(StringIO(content), dstFile)
            assert log.debug('Success publishing content to path %s', path) or True

    def removePath(self, path):
        '''
        @see ICDM.removePath
        '''
        path, itemPath = self._validatePath(path)
        if isdir(itemPath):
            rmtree(itemPath)
        elif isfile(itemPath):
            os.remove(itemPath)
        else:
            raise PathNotFound(path)
        assert log.debug('Success removing path %s', path) or True

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
        self._validatePath(path)
        if protocol != 'http':
            raise UnsupportedProtocol(protocol)
        return self.delivery.getURI(path)

    def _publishFromFileObj(self, path, fileObj):
        '''
        Publish content from a file object

        @param path: string
                The path of the content item. This is a unique
                     identifier of the item.
        @param ioStream: io.IOBase
                The IO stream object
        '''
        assert isinstance(path, str), 'Invalid content path %s' % path
        assert hasattr(fileObj, 'read'), 'Invalid file object %s' % fileObj
        path, dstFilePath = self._validatePath(path)
        dstDir = dirname(dstFilePath)
        if not isdir(dstDir):
            os.makedirs(dstDir)
        with open(dstFilePath, 'w+b') as dstFile:
            copyfileobj(fileObj, dstFile)
            assert log.debug('Success publishing stream to path %s', path) or True

    def _getItemPath(self, path):
        return join(self.delivery.getRepositoryPath(), path.lstrip(os.sep))

    def _validatePath(self, path):
        path = normOSPath(path, True)
        fullPath = normOSPath(self._getItemPath(path), True)
        if not fullPath.startswith(self.delivery.getRepositoryPath()):
            raise PathNotFound('Path is outside the repository: %s' % path)
        return (path, fullPath)

    def _isSyncFile(self, srcFilePath, dstFilePath):
        '''
        Return true if the destination file exists and was newer than
        the source file.
        '''
        return (isfile(srcFilePath) or isdir(srcFilePath)) \
            and (isfile(dstFilePath) or isdir(dstFilePath)) \
            and os.stat(srcFilePath).st_mtime < os.stat(dstFilePath).st_mtime

    def _copyZipDir(self, zipFilePath, inDirPath, path):
        '''
        Copy a directory from a ZIP archive to a filesystem directory

        @param zipFilePath: string
            The path of the ZIP archive
        @param inDirPath: string
            The path to the file in the ZIP archive
        @param path: string
            Destination path where the ZIP directory is copied
        '''
        # make sure the ZIP file path is normalized and uses the OS separator
        zipFilePath = normOSPath(zipFilePath)
        # make sure the ZIP file path is normalized and uses the ZIP separator
        inDirPath = normZipPath(inDirPath)
        zipFile = ZipFile(zipFilePath)
        if isdir(path):
            if self._isSyncFile(zipFilePath, path):
                return
            rmtree(path)
        entries = [ent for ent in zipFile.namelist() if ent.startswith(inDirPath)]
        tmpDir = TemporaryDirectory()
        zipFile.extractall(tmpDir.name, entries)
        tmpDirPath = join(tmpDir.name, normOSPath(inDirPath))
        os.makedirs(path)
        for entry in os.listdir(tmpDirPath):
            move(join(tmpDirPath, entry), path)


@injected
class LocalFileSystemLinkCDM(LocalFileSystemCDM):
    '''
    @see ICDM (Content Delivery Manager interface)
    '''
    _linkExt = '.link'

    _zipHeader = 'ZIP'

    _fsHeader = 'FS'

    _deletedExt = '.deleted'

    def publishFromFile(self, path, filePath):
        '''
        @see ICDM.publishFromFile
        '''
        path, _fullPath = self._validatePath(path)
        self._publishFromFile(path, filePath)

    def publishFromDir(self, path, dirPath):
        '''
        @see ICDM.publishFromDir
        '''
        assert isinstance(path, str), 'Invalid path %s' % path
        assert isinstance(dirPath, str), 'Invalid directory path %s' % dirPath
        path, _fullPath = self._validatePath(path)
        dirPath = dirPath.strip()
        self._publishFromFile(path, dirPath if dirPath.endswith(ZIPSEP) else dirPath + ZIPSEP)

    def removePath(self, path):
        '''
        @see ICDM.removePath
        '''
        path, entryPath = self._validatePath(path)
        linkPath = entryPath
        repPathLen = len(self.delivery.getRepositoryPath())
        while len(linkPath.lstrip(os.sep)) > repPathLen:
            linkFile = linkPath + self._linkExt
            if isfile(linkFile):
                if (linkPath == entryPath.rstrip(os.sep)):
                    os.remove(linkPath)
                    break
                subPath = entryPath[len(linkPath):].lstrip(os.sep)
                with open(linkFile) as f:
                    linkType = f.readline().strip()
                    if linkType == self._fsHeader:
                        self._removeFSLink(f, path, entryPath, subPath)
                    elif linkType == self._zipHeader:
                        self._removeZiplink(f, path, entryPath, subPath)
                    else:
                        raise Exception('Invalid link type found: %s in %s', linkType, entryPath)
                break
            nextLinkPath = dirname(linkPath)
            if nextLinkPath == linkPath: break
            linkPath = nextLinkPath
        else:
            raise PathNotFound(path)
        if len(subPath.strip(os.sep)) == 0 and isdir(linkPath):
            rmtree(linkPath)

    def _createDelMark(self, path):
        '''
        Creates a mark file for a deleted path inside a linked directory
        or ZIP file.

        @param path: string
            The path for which to create the delete mark.
        '''
        if not isdir(dirname(path)):
            os.makedirs(dirname(path))
        with open(path.rstrip(os.sep) + self._deletedExt, 'w') as _d: pass
        if isdir(path):
            rmtree(path)

    def _removeFSLink(self, fHandler, path, entryPath, subPath):
        '''
        Removes a link to a file or directory on the file system.

        @param fHandler: file handler
            Handler to the link file.
        @param path: string
            The repository path to remove.
        @param entryPath: string
            The full path for which to create the deletion mark.
        @param subPath: string
            The path inside the linked directory (if needed)
        '''
        linkedPath = fHandler.readline().strip()
        if isdir(linkedPath):
            if isfile(join(linkedPath, subPath)) or isdir(join(linkedPath, subPath)):
                self._createDelMark(entryPath)
            else:
                raise PathNotFound(path)
        elif subPath:
            raise PathNotFound(path)

    def _removeZiplink(self, fHandler, path, entryPath, subPath):
        '''
        Removes a link to a file or directory in a ZIP archive.

        @param fHandler: file handler
            Handler to the link file.
        @param path: string
            The repository path to remove.
        @param entryPath: string
            The full path for which to create the deletion mark.
        @param subPath: string
            The path inside the linked ZIP archive.
        '''
        zipFilePath = normOSPath(fHandler.readline().strip())
        inFilePath = normOSPath(fHandler.readline().strip(), True)
        zipFile = ZipFile(zipFilePath)
        inZipFile = normZipPath(join(inFilePath, subPath))
        if not inZipFile in zipFile.NameToInfo:
            raise PathNotFound(path)
        self._createDelMark(entryPath)

    def _createLinkToZipFile(self, path, zipFilePath, inFilePath):
        repFilePath = self._getItemPath(path) + self._linkExt
        fHandler = open(repFilePath, 'w')
        fHandler.write(self._zipHeader + "\n")
        fHandler.write(zipFilePath + "\n")
        fHandler.write(normZipPath(inFilePath) + "\n")
        fHandler.close()

    def _createLinkToFileOrDir(self, path, filePath):
        repFilePath = self._getItemPath(path) + self._linkExt
        fHandler = open(repFilePath, 'w')
        fHandler.write(self._fsHeader + "\n")
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
        zipFilePath, inFilePath = getZipFilePath(filePath, self.delivery.getRepositoryPath())
        assert isfile(zipFilePath) and os.access(zipFilePath, os.R_OK), \
            'Unable to read file path %s' % filePath
        zipFile = ZipFile(zipFilePath)
        zipFile.getinfo(inFilePath)
        self._createLinkToZipFile(path, zipFilePath, inFilePath)
