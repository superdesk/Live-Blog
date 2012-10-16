'''
Created on Jan 5, 2012

@package support - cdm
@copyright 2012 Sourcefabric o.p.s.
@license http: // www.gnu.org / licenses / gpl - 3.0.txt
@author: Mugur Rus

Contains the Content Delivery Manager implementation for local file system
'''

from ally.container.ioc import injected
from ally.zip.util_zip import ZIPSEP, normOSPath, normZipPath, getZipFilePath, validateInZipPath
from cdm.spec import ICDM, UnsupportedProtocol, PathNotFound
from datetime import datetime
from os.path import isdir, isfile, join, dirname, normpath, relpath, abspath
from shutil import copyfile, copyfileobj, move, rmtree
from tempfile import TemporaryDirectory
from zipfile import ZipFile
import abc
import json
import logging
import os


# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

class IDelivery(metaclass=abc.ABCMeta):
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
            The path of the content item. This is a unique identifier of the item.
        @return: string
            The URI of the content
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
        assert isinstance(self.serverURI, str), 'Invalid server URI value %s' % self.serverURI
        assert isinstance(self.repositoryPath, str), 'Invalid repository directory value %s' % self.repositoryPath
        self.repositoryPath = normOSPath(self.repositoryPath)
        if not os.path.exists(self.repositoryPath): os.makedirs(self.repositoryPath)
        assert isdir(self.repositoryPath) and os.access(self.repositoryPath, os.W_OK), \
        'Unable to access the repository directory %s' % self.repositoryPath

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
    Local file system implementation for the @see: ICDM (Content Delivery Manager interface)
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
            if not inDirPath.endswith(ZIPSEP): inDirPath = inDirPath + ZIPSEP
            self._copyZipDir(zipFilePath, inDirPath, fullPath)
            assert log.debug('Success publishing ZIP dir %s (%s) to path %s', inDirPath, zipFilePath, path) or True
            return
        dirPath = normpath(dirPath)
        assert os.access(dirPath, os.R_OK), 'Unable to read the directory path %s' % dirPath
        for root, _dirs, files in os.walk(dirPath):
            relPath = relpath(root, dirPath)
            for file in files:
                publishPath = join(normOSPath(path), relPath.lstrip(os.sep), file)
                filePath = join(root, file)
                self.publishFromFile(publishPath, filePath)
            assert log.debug('Success publishing directory %s to path %s', dirPath, path) or True

    def publishContent(self, path, content):
        '''
        @see ICDM.publishContent
        '''
        assert isinstance(path, str), 'Invalid content path %s' % path
        #assert isinstance(content, ) or , 'Invalid binary content for path %s' % path
        path, dstFilePath = self._validatePath(path)
        dstDir = dirname(dstFilePath)
        if not isdir(dstDir):
            os.makedirs(dstDir)
        with open(dstFilePath, 'w+b') as dstFile:
            copyfileobj(content, dstFile)
            assert log.debug('Success publishing content to path %s', path) or True


    def republish(self, oldPath, newPath):
        '''
        @see ICDM.republish
        '''
        oldPath, oldFullPath = self._validatePath(oldPath)
        if isdir(oldFullPath):
            raise PathNotFound(oldPath)
        newPath, newFullPath = self._validatePath(newPath)
        if isdir(newFullPath) or isfile(newFullPath):
            raise ValueError('New path %s is already in use' % newPath)
        dstDir = dirname(newFullPath)
        if not isdir(dstDir):
            os.makedirs(dstDir)
        move(oldFullPath, newFullPath)

    def remove(self, path):
        '''
        @see ICDM.remove
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

    def getURI(self, path, protocol='http'):
        '''
        @see ICDM.getURI
        '''
        assert isinstance(path, str), 'Invalid content path %s' % path
        assert isinstance(protocol, str), 'Invalid protocol %s' % protocol
        if protocol == 'http':
            return self.delivery.getURI(path)
        if protocol == 'file':
            return abspath(self._getItemPath(path))
        raise UnsupportedProtocol(protocol)

    def getTimestamp(self, path):
        '''
        @see ICDM.getTimestamp
        '''
        assert isinstance(path, str), 'Invalid content path %s' % path
        path, itemPath = self._validatePath(path)
        if not isdir(itemPath) and not isfile(itemPath):
            raise PathNotFound(path)
        return datetime.fromtimestamp(os.stat(itemPath).st_mtime)

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
        return join(self.delivery.getRepositoryPath(), normOSPath(path.lstrip(os.sep), True))

    def _validatePath(self, path):
        path = normZipPath(path)
        fullPath = normOSPath(self._getItemPath(path), True)
        if not fullPath.startswith(self.delivery.getRepositoryPath()):
            raise PathNotFound(path)
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
        if not isinstance(filePath, str) and hasattr(filePath, 'read'):
            return self._publishFromFileObj(path, filePath)
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

    def republish(self, oldPath, newPath):
        '''
        @see ICDM.republish
        '''
        raise NotImplementedError('Republish operation not available')

    def remove(self, path):
        '''
        @see ICDM.remove
        '''
        path, entryPath = self._validatePath(path)
        if isfile(entryPath.rstrip(os.sep)):
            return os.remove(entryPath)

        linkPath = entryPath
        repPathLen = len(self.delivery.getRepositoryPath())
        while len(linkPath.lstrip(os.sep)) > repPathLen:
            linkFile = linkPath + self._linkExt
            if isfile(linkFile):
                subPath = entryPath[len(linkPath):].lstrip(os.sep)
                with open(linkFile) as f:
                    links = json.load(f)
                    count = 0
                    for link in links:
                        if link[0] == self._fsHeader and self._isValidFSLink(link, subPath):
                            self._removeFSLink(link, path, entryPath, subPath); count += 1
                            break
                        elif link[0] == self._zipHeader and self._isValidZIPLink(link, subPath):
                            self._removeZiplink(link, path, entryPath, subPath); count += 1
                            break
                    if count == 0:
                        raise PathNotFound(path)
                break
            nextLinkPath = dirname(linkPath)
            if nextLinkPath == linkPath: break
            linkPath = nextLinkPath
        else:
            raise PathNotFound(path)
        if len(subPath.strip(os.sep)) == 0 and isdir(linkPath):
            rmtree(linkPath)

    def getURI(self, path, protocol='http'):
        '''
        @see ICDM.getURI
        '''
        assert isinstance(path, str), 'Invalid content path %s' % path
        assert isinstance(protocol, str), 'Invalid protocol %s' % protocol
        if protocol == 'http':
            return super().getURI(path)
        elif protocol == 'file':
            path, dstFilePath = self._validatePath(path)
            return abspath(dstFilePath)
        raise UnsupportedProtocol(protocol)

    def getTimestamp(self, path):
        '''
        @see ICDM.getTimestamp
        '''
        assert isinstance(path, str), 'Invalid content path %s' % path
        path, entryPath = self._validatePath(path)
        if isdir(entryPath) or isfile(entryPath):
            return datetime.fromtimestamp(os.stat(entryPath).st_mtime)

        linkPath = entryPath
        repPathLen = len(self.delivery.getRepositoryPath())
        while len(linkPath.lstrip(os.sep)) > repPathLen:
            linkFile = linkPath + self._linkExt
            if isfile(linkFile):
                subPath = entryPath[len(linkPath):].lstrip(os.sep)
                with open(linkFile) as f:
                    links = json.load(f)
                    for link in links:
                        if link[0] == self._fsHeader and self._isValidFSLink(link, subPath):
                            fullPath = join(link[1], subPath) if subPath else link[1]
                            return datetime.fromtimestamp(os.stat(fullPath).st_mtime)
                        elif link[0] == self._zipHeader and self._isValidZIPLink(link, subPath):
                            return datetime.fromtimestamp(os.stat(link[1]).st_mtime)
                    raise PathNotFound(path)
            nextLinkPath = dirname(linkPath)
            if nextLinkPath == linkPath: break
            linkPath = nextLinkPath
        else:
            raise PathNotFound(path)

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

    def _isValidFSLink(self, link, subPath):
        '''
        Returns true if the file identified by subpath exists in
        the given link to a file / directory, false otherwise.

        @param link: list
            Link description in JSON format.
        @param subPath: string
            The path inside the linked directory (if needed)
        '''
        filePath = join(link[1], subPath) if subPath else link[1]
        return (not subPath or isdir(link[1])) and (isfile(filePath) or isdir(filePath))

    def _isValidZIPLink(self, link, subPath):
        '''
        Returns true if the file identified by subpath exists in
        the given link to a ZIP archive, false otherwise.

        @param link: list
            Link description in JSON format.
        @param subPath: string
            The path inside the linked directory (if needed)
        '''
        zipFilePath = normOSPath(link[1])
        inFilePath = normOSPath(link[2], True)
        zipFile = ZipFile(zipFilePath)
        inZipFile = normZipPath(join(inFilePath, subPath)) if subPath else normZipPath(inFilePath)
        return inZipFile in zipFile.NameToInfo

    def _removeFSLink(self, link, path, entryPath, subPath):
        '''
        Removes a link to a file or directory on the file system.

        @param link: list
            Link description in JSON format.
        @param path: string
            The repository path to remove.
        @param entryPath: string
            The full path for which to create the deletion mark.
        @param subPath: string
            The path inside the linked directory (if needed)
        '''
        if isdir(link[1]):
            filePath = join(link[1], subPath)
            if isfile(filePath) or isdir(filePath):
                self._createDelMark(entryPath)
            else:
                raise PathNotFound(path)
        elif subPath:
            raise PathNotFound(path)

    def _removeZiplink(self, link, path, entryPath, subPath):
        '''
        Removes a link to a file or directory in a ZIP archive.

        @param link: list
            Link description in JSON format.
        @param path: string
            The repository path to remove.
        @param entryPath: string
            The full path for which to create the deletion mark.
        @param subPath: string
            The path inside the linked ZIP archive.
        '''
        zipFilePath = normOSPath(link[1])
        inFilePath = normOSPath(link[2], True)
        zipFile = ZipFile(zipFilePath)
        inZipFile = normZipPath(join(inFilePath, subPath))
        if not inZipFile in zipFile.NameToInfo:
            raise PathNotFound(path)
        self._createDelMark(entryPath)

    def _createLinkToZipFile(self, path, zipFilePath, inFilePath):
        repFilePath = self._getItemPath(path) + self._linkExt
        if isfile(repFilePath):
            with open(repFilePath, 'r') as f: links = json.load(f)
        else: links = []
        inFilePath = normZipPath(inFilePath)
        for k, entry in enumerate(links):
            if entry and entry[0] == self._zipHeader:
                if entry[1] == zipFilePath and entry[2] == inFilePath:
                    if k > 0: links.insert(0, links.pop(k))
                    break
        else: links.insert(0, (self._zipHeader, zipFilePath, inFilePath))

        with open(repFilePath, 'w') as f: json.dump(links, f)

    def _createLinkToFileOrDir(self, path, filePath):
        repFilePath = self._getItemPath(path) + self._linkExt
        if isfile(repFilePath):
            with open(repFilePath, 'r') as f: links = json.load(f)
        else: links = []
        for k, entry in enumerate(links):
            if entry and entry[0] == self._fsHeader:
                if entry[1] == filePath:
                    if k > 0: links.insert(0, links.pop(k))
                    break
        else: links.insert(0, (self._fsHeader, filePath))

        with open(repFilePath, 'w') as f: json.dump(links, f)

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
        validateInZipPath(zipFile, inFilePath)
        self._createLinkToZipFile(path, zipFilePath, inFilePath)
