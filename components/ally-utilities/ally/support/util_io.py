'''
Created on Jan 17, 2012

@package: ally utilities
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides utility functions for handling I/O operations.
'''

from ally.zip.util_zip import normOSPath, getZipFilePath, ZIPSEP
from os.path import isfile
from os import stat
from zipfile import ZipFile
from datetime import datetime

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
        assert hasattr(fileObj, 'read'), 'Invalid file object %s does not have a read method' % fileObj
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
    assert hasattr(srcFileObj, 'read'), 'Invalid source file object %s does not have a read method' % srcFileObj
    assert hasattr(dstFileObj, 'write'), 'Invalid destination file object %s does not have a write method' % dstFileObj
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
    assert hasattr(fileObj, 'read'), 'Invalid file object %s does not have a read method' % fileObj
    assert isinstance(bufferSize, int), 'Invalid buffer size %s' % bufferSize
    with fileObj:
        while True:
            buffer = fileObj.read(bufferSize)
            if not buffer: break
            yield buffer

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

