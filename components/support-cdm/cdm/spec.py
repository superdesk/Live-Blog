'''
Created on Jan 5, 2012

@package support - cdm
@copyright 2012 Sourcefabric o.p.s.
@license http: // www.gnu.org / licenses / gpl - 3.0.txt
@author: Mugur Rus

Contains the Content Delivery Manager (CDM) interface
'''

import abc

# --------------------------------------------------------------------

class ICDM(metaclass = abc.ABCMeta):
    '''
    Content Delivery Manager (CDM) interface

    '''

    @abc.abstractmethod
    def publishFromFile(self, path, filePath):
        '''
        Publish content from a file.

        @param path: string
                The path of the content item. This is a unique
                     identifier of the item.
        @param filePath: string
                The path of the file on the file system
        '''

    @abc.abstractmethod
    def publishFromDir(self, path, dirPath):
        '''
        Publish content from a file.

        @param path: string
                The path of the content item. This is a unique
                     identifier of the item.
        @param dirPath: string
                The path of the directory on the file system
        '''

    @abc.abstractmethod
    def publishFromStream(self, path, ioStream):
        '''
        Publish content from an IO stream

        @param path: string
                The path of the content item. This is a unique
                     identifier of the item.
        @param ioStream: io.IOBase
                The IO stream object
        '''

    @abc.abstractmethod
    def publishContent(self, path, content):
        '''
        Publish content from a string.

        @param path: string
                The path of the content item. This is a unique
                     identifier of the item.
        @param content: string
                The string containing the content
        '''

    @abc.abstractmethod
    def removePath(self, path):
        '''
        Remove the given path from the repository.

        @param path: string
                The path of the content item. This is a unique
                     identifier of the item.
        '''

    @abc.abstractmethod
    def getSupportedProtocols(self):
        '''
        @return: Returns a tuple of supported protocol names.
        @rtype: tuple
        '''

    @abc.abstractmethod
    def getURI(self, path, protocol):
        '''
        Returns the URI of a certain content identified by the unique path.

        @param path: string
                The path of the content item. This is a unique
                     identifier of the item.
        @param protocol: string
                A string containing the name of the protocol
        @return: The URI of the content
        @rtype: string
        '''

class PathNotFound(Exception):
    '''
    Exception thrown when a path was not found in the repository
    '''

    path = str
    # The path identifier

    def __init__(self, path):
        assert isinstance(path, str), 'Invalid protocol %s' % path
        self.path = path
        Exception.__init__(self, 'Path not found: %s' % path)

class UnsupportedProtocol(Exception):
    '''
    Exception thrown when an URI was requested for an unsupported protocol.
    '''

    protocol = str
    # The protocol identifier

    def __init__(self, protocol):
        assert isinstance(protocol, str), 'Invalid protocol %s' % protocol
        self.protocol = protocol
        Exception.__init__(self, 'Unsupported protocol %r' % protocol)
