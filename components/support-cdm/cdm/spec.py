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

class ICDM(metaclass=abc.ABCMeta):
    '''
    Content Delivery Manager (CDM) interface

    '''

    @abc.abstractmethod
    def publishFromFile(self, path, filePath):
        '''
        Publish content from a file.

        @param path: string
            The path of the content item. This is a unique identifier of the item.
        @param filePath: string or file object
            The path of the file on the file system or a readable file object
        '''

    @abc.abstractmethod
    def publishFromDir(self, path, dirPath):
        '''
        Publish content from a file.

        @param path: string
            The path of the content item. This is a unique identifier of the item.
        @param dirPath: string
            The path of the directory on the file system.
        '''

    @abc.abstractmethod
    def publishContent(self, path, content):
        '''
        Publish content from a string.

        @param path: string
            The path of the content item. This is a unique identifier of the item.
        @param content: input stream
            The content as input stream
        '''

    @abc.abstractmethod
    def republish(self, oldPath, newPath):
        '''
        Re-publish an existing path under a new path.

        @param oldPath: string
            The path of the existing item. This is a unique identifier of the item.
        @param newPath: string
            The new path under which the item will be published.
        '''

    @abc.abstractmethod
    def remove(self, path):
        '''
        Remove the given path from the repository.

        @param path: string
            The path of the content item. This is a unique identifier of the item.
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
        Returns the URI of a certain content identified by the unique path. Attention this method should not perform any
        checks to see if the content is valid or exists.

        @param path: string
            The path of the content item. This is a unique identifier of the item.
        @param protocol: string
            A string containing the name of the protocol
        @return: string
            The URI of the content
        '''

    @abc.abstractmethod
    def getTimestamp(self, path):
        '''
        Returns the time stamp of a certain content identified by the unique
        path.

        @param path: string
            The path of the content item. This is a unique identifier of the item.
        @return: datetime
            The last modification time for the content in path.
        @raise PathNotFound: in case the path does not exist in the CDM.
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
