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

        @param path: the path of the content item. This is a unique
                     identifier of the item.
        @param filePath: the path of the file on the file system
        '''

    @abc.abstractmethod
    def publishContent(self, path, content):
        '''
        Publish content from a string.

        @param path: the path of the content item. This is a unique
                     identifier of the item.
        @param content: the string containing the content
        '''

    @abc.abstractmethod
    def getURL(self, path):
        '''
        Returns the URL of a certain content identified by the unique path.

        @param path: the path of the content item. This is a unique
                     identifier of the item.
        @return: the URL of the content (string)
        @rtype: str
        '''
