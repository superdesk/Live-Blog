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

        @param path: str
                The path of the content item. This is a unique
                     identifier of the item.
        @param filePath: str
                The path of the file on the file system
        '''

    @abc.abstractmethod
    def publishContent(self, path, content):
        '''
        Publish content from a string.

        @param path: str
                The path of the content item. This is a unique
                     identifier of the item.
        @param content: str
                The string containing the content
        '''

    @abc.abstractmethod
    def getURI(self, path, protocols):
        '''
        Returns the URI of a certain content identified by the unique path.

        @param path: str
                The path of the content item. This is a unique
                     identifier of the item.
        @param protocols: tuple
                A tuple of protocol names (strings)
        @return: The URI of the content
        @rtype: str
        '''
