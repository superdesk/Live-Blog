'''
Created on Jan 17, 2012

@package: ally utilities
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides utility functions for handling I/O operations.
'''

from ally.zip.util_zip import normOSPath, getZipFilePath, ZIPSEP
from collections import Iterable
from datetime import datetime
from genericpath import isdir, exists
from os import stat, makedirs
from os.path import isfile, normpath, join, dirname
from shutil import copy
from zipfile import ZipFile, ZipInfo
import abc
import os
import shutil

# --------------------------------------------------------------------

class IInputStream(metaclass=abc.ABCMeta):
    '''
    The specification for an input stream.
    '''
    __slots__ = ()

    @abc.abstractclassmethod
    def read(self, nbytes=None):
        '''
        To read a file's contents, call f.read(size), which reads some quantity of data and returns it as a string.
        @param nbytes: integer
            Is an optional numeric argument. When size is omitted or negative, the entire contents of the file will be
            read and returned; it's your problem if the file is twice as large as your machine's memory.
            Otherwise, at most size bytes are read and returned. If the end of the file has been reached, f.read()
            will return an empty string ('').
        @return: bytes
            The content.
        '''

    @classmethod
    def __subclasshook__(cls, C):
        if cls is IInputStream:
            if any('read' in B.__dict__ for B in C.__mro__): return True
        return NotImplemented

class IOutputStream(metaclass=abc.ABCMeta):
    '''
    The specification for an output stream.
    '''
    __slots__ = ()

    @abc.abstractclassmethod
    def write(self, bytes):
        '''
        Write the bytes or bytearray object, b and return the number of bytes written. When in non-blocking mode,
        a BlockingIOError is raised if the buffer needs to be written out but the raw stream blocks.
        
        @param bytes: bytearray
            The bytes to write.
        '''

    @classmethod
    def __subclasshook__(cls, C):
        if cls is IOutputStream:
            if any('write' in B.__dict__ for B in C.__mro__): return True
        return NotImplemented

class IClosable(metaclass=abc.ABCMeta):
    '''
    Used for the streams that provide a close method.
    '''
    __slots__ = ()

    @abc.abstractclassmethod
    def close(self):
        '''
        Close the stream and block any other operations to the stream.
        '''

    @classmethod
    def __subclasshook__(cls, C):
        if cls is IClosable:
            if any('close' in B.__dict__ for B in C.__mro__): return True
        return NotImplemented

# --------------------------------------------------------------------

class replaceInFile:
    '''
    Provides the file read replacing.
    '''

    __slots__ = ['_fileObj', '_replacements', '_maxKey', '_leftOver']

    def __init__(self, fileObj, replacements):
        '''
        Creates a proxy for the provided file object that will replace in the provided file content based on the data
        provided in the replacements map.
        
        @param fileObj: a file like object with a 'read' method
            The file object to wrap and have the content changed.
        @param replacements: dictionary{string|bytes, string|bytes}
            A dictionary containing as a key the data that needs to be changed and as a value the data to change with.
        @return: Proxy
            The proxy created for the file that will handle the data replacing.
        '''
        assert fileObj, 'A file object is required %s' % fileObj
        assert isinstance(fileObj, IInputStream), 'Invalid file object %s does not have a read method' % fileObj
        assert isinstance(replacements, dict), 'Invalid replacements %s' % replacements
        if __debug__:
            for key, value in replacements.items():
                assert isinstance(key, (str, bytes)), 'Invalid key %s' % key
                assert isinstance(value, (str, bytes)), 'Invalid value %s' % value
        self._fileObj = fileObj
        self._replacements = replacements

        self._maxKey = len(max(replacements.keys(), key=lambda v: len(v)))
        self._leftOver = None

    def read(self, count=None):
        '''
        Perform the data read. 
        '''
        data = self._fileObj.read(count)

        if not data:
            if self._leftOver:
                data = self._leftOver
                self._leftOver = None
            else: return data

        toIndex = None
        if self._leftOver:
            toIndex = len(data)
            data = self._leftOver + data
        else:
            extra = self._fileObj.read(self._maxKey - 1)
            if extra:
                toIndex = len(data)
                data = data + extra

        for key, value in self._replacements.items(): data = data.replace(key, value)

        if toIndex:
            self._leftOver = data[toIndex:]
            data = data[:toIndex]

        return data

    def __getattr__(self, name): return getattr(self._fileObj, name)

def pipe(srcFileObj, dstFileObj, bufferSize=1024):
    '''
    Copy the content from a source file to a destination file

    @param srcFileObj: a file like object with a 'read' method
        The file object to copy from
    @param dstFileObj: a file like object with a 'write' method
        The file object to copy to
    @param bufferSize: integer
        The buffer size used for copying data chunks.
    '''
    assert isinstance(srcFileObj, IInputStream), 'Invalid source file object %s' % srcFileObj
    assert isinstance(dstFileObj, IOutputStream), 'Invalid destination file object %s' % dstFileObj
    assert isinstance(bufferSize, int), 'Invalid buffer size %s' % bufferSize
    while True:
        buffer = srcFileObj.read(bufferSize)
        if not buffer: break
        dstFileObj.write(buffer)

def readGenerator(fileObj, bufferSize=1024):
    '''
    Provides a generator that read data from the provided file object.
    
    @param fileObj: a file like object with a 'read' method
        The file object to have the generator read data from.
    @param bufferSize: integer
        The buffer size used for returning data chunks.
    '''
    assert isinstance(fileObj, IInputStream), 'Invalid file object %s' % fileObj
    assert isinstance(fileObj, IClosable), 'Invalid file object %s' % fileObj
    assert isinstance(bufferSize, int), 'Invalid buffer size %s' % bufferSize

    with fileObj:
        while True:
            buffer = fileObj.read(bufferSize)
            if not buffer:
                fileObj.close()
                break
            yield buffer

def writeGenerator(generator, fileObj):
    '''
    Provides a generator that read data from the provided file object.
    
    @param generator: Iterable
        The generator to get the content to be writen.
    @param fileObj: a file like object with a 'write' method
        The file object to have the generator write data from.
    '''
    assert isinstance(generator, Iterable), 'Invalid generator %s' % generator
    assert isinstance(fileObj, IOutputStream), 'Invalid file object %s' % fileObj
    assert isinstance(fileObj, IClosable), 'Invalid file object %s' % fileObj

    for bytes in generator: fileObj.write(bytes)
    fileObj.close()

def convertToBytes(iterable, charSet, encodingError):
    '''
    Provides a generator that converts from string to bytes based on string data from another Iterable.
    
    @param iterable: Iterable
        The iterable providing the strings to convert.
    @param charSet: string
        The character set to encode based on.
    @param encodingError: string
        The encoding error resolving.
    '''
    assert isinstance(iterable, Iterable), 'Invalid iterable %s' % iterable
    assert isinstance(charSet, str), 'Invalid character set %s' % charSet
    assert isinstance(encodingError, str), 'Invalid encoding error set %s' % encodingError
    for value in iterable:
        assert isinstance(value, str), 'Invalid value %s received' % value
        yield value.encode(encoding=charSet, errors=encodingError)

def openURI(path):
    '''
    Returns a read file object for the given path.
    
    @param path: string
        The path to a resource: a file system path, a ZIP path
    @return: byte file
        A file like object that delivers bytes.
    '''
    path = normOSPath(path)
    if isfile(path):
        return open(path, 'rb')
    zipFilePath, inZipPath = getZipFilePath(path)
    zipFile = ZipFile(zipFilePath)
    if inZipPath in zipFile.NameToInfo and not inZipPath.endswith(ZIPSEP) and inZipPath != '':
        return zipFile.open(inZipPath)
    raise IOError('Invalid file path %s' % path)

def timestampURI(path):
    '''
    Returns the last modified time stamp for the given path.
    
    @param path: string
        The path to a resource: a file system path, a ZIP path
    @return: datetime
        The last modified time stamp.
    '''
    path = normOSPath(path)
    if isfile(path):
        return datetime.fromtimestamp(stat(path).st_mtime)
    zipFilePath, _inZipPath = getZipFilePath(path)
    return datetime.fromtimestamp(stat(zipFilePath).st_mtime)

def synchronizeURIToDir(path, dirPath):
    '''
    Publishes the entire contents from the URI path to the provided directory path.
    
    @param path: string
        The path to a resource: a file system path, a ZIP path
    @param dirPath: string
        The directory path to synchronize with.
    '''
    assert isinstance(path, str) and path, 'Invalid content path %s' % path
    assert isinstance(dirPath, str), 'Invalid directory path value %s' % dirPath

    if not isdir(path):
        # not a directory, see if it's a entry in a zip file
        zipFilePath, inDirPath = getZipFilePath(path)
        zipFile = ZipFile(zipFilePath)
        if not inDirPath.endswith(ZIPSEP): inDirPath = inDirPath + ZIPSEP

        lenPath, zipTime = len(inDirPath), datetime.fromtimestamp(stat(zipFilePath).st_mtime)
        for zipInfo in zipFile.filelist:
            assert isinstance(zipInfo, ZipInfo), 'Invalid zip info %s' % zipInfo
            if zipInfo.filename.startswith(inDirPath):
                if zipInfo.filename[0] == '/': dest = zipInfo.filename[1:]
                else: dest = zipInfo.filename

                dest = normpath(join(dirPath, dest[lenPath:]))

                if exists(dest) and zipTime <= datetime.fromtimestamp(stat(dest).st_mtime): continue
                destDir = dirname(dest)
                if not exists(destDir): makedirs(destDir)

                with zipFile.open(zipInfo) as source:
                    with open(dest, 'wb') as target:
                        shutil.copyfileobj(source, target)
        return

    path = normpath(path)
    assert os.access(path, os.R_OK), 'Unable to read the directory path %s' % path
    lenPath = len(path) + 1
    for root, _dirs, files in os.walk(path):
        for file in files:
            src, dest = join(root, file), join(dirPath, root[lenPath:], file)

            if exists(dest) and \
            datetime.fromtimestamp(stat(src).st_mtime) <= datetime.fromtimestamp(stat(dest).st_mtime): continue

            destDir = dirname(dest)
            if not exists(destDir): makedirs(destDir)
            copy(src, dest)

class keepOpen:
    '''
    Keeps opened a file object, basically blocks the close calls.
    '''
    __slots__ = ['_fileObj']

    def __init__(self, fileObj):
        '''
        Construct the keep open file object proxy.
        
        @param fileObj: file
            A file type object to keep open.
        '''
        assert fileObj, 'A file object is required %s' % fileObj
        self._fileObj = fileObj

    def close(self):
        '''
        Block the close action.
        '''

    def __getattr__(self, name): return getattr(self._fileObj, name)

