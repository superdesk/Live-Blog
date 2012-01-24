'''
Created on Jan 17, 2012

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides utility functions for handling I/O operations.
'''

# --------------------------------------------------------------------

class FileReplace:
    '''
    Provides the file read replacing.
    Used by the @see: replaceInFile method.
    '''

    def __init__(self, fileObj, replacements):
        '''
        Construct the file replacer.
        
        @param fileObj: file reader
            A file reader type object from which the data is read and replaced.
        @param replacements: dictionary{string|bytes, string|bytes}
            The replacements map, as a key the string to be replaced and as a value the replacement.
        '''
        assert fileObj, 'A file object is required %s' % fileObj
        assert hasattr(fileObj, 'read'), 'Invalid file object %s has no read method' % fileObj
        assert isinstance(replacements, dict), 'Invalid replacements %s' % replacements
        if __debug__:
            for key, value in replacements.items():
                assert isinstance(key, (str, bytes)), 'Invalid key %s' % key
                assert isinstance(value, (str, bytes)), 'Invalid value %s' % value
        self.__fileObj = fileObj
        self.__replacements = replacements

        self.__maxKey = max(replacements.keys(), key = lambda v: len(v))
        self.__leftOver = None

    def read(self, count = None):
        '''
        Perform the data read. 
        '''
        data = self.__fileObj.read(count)

        if not data:
            if self.__leftOver:
                data = self.__leftOver
                self.__leftOver = None
            else: return data

        toIndex = None
        if self.__leftOver:
            toIndex = len(data)
            data = self.__leftOver + data
        else:
            extra = self.__fileObj.read(self.__maxKey - 1)
            if extra:
                toIndex = len(data)
                data = data + extra

        for key, value in self.__replacements.items(): data = data.replace(key, value)

        if toIndex:
            self.__leftOver = data[toIndex:]
            data = data[:toIndex]

        return data

    def __getattr__(self, name): return getattr(self.__fileObj, name)

def replaceInFile(fileObj, replacements):
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
    assert hasattr(fileObj, 'read'), 'Invalid file object %s does not have a read method' % fileObj
    assert isinstance(replacements, dict), 'Invalid replacements dictionary %s' % replacements
    return FileReplace(fileObj, replacements)

BUFFER_SIZE = 1024

def pipe(srcFileObj, dstFileObj):
    '''
    Copy the content from a source file to a destination file

    @param srcFileObj: a file like object with a 'read' method
        The file object to copy from
    @param dstFileObj: a file like object with a 'write' method
        The file object to copy to
    '''
    assert hasattr(srcFileObj, 'read'), \
        'Invalid source file object %s does not have a read method' % srcFileObj
    assert hasattr(dstFileObj, 'write'), \
        'Invalid destination file object %s does not have a write method' % dstFileObj
    while True:
        buffer = srcFileObj.read(BUFFER_SIZE)
        if not buffer: break
        dstFileObj.write(buffer)
