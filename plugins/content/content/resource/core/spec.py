'''
Created on Nov 21, 2013

@package: content
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mugur Rus

API specifications for content converter and reader.
'''

from abc import ABCMeta  # @UnusedImport
from abc import abstractmethod

# --------------------------------------------------------------------

class IConverter(metaclass=ABCMeta):
    '''
    Interface of a converter of content to an unformatted content and it's format.
    E.g.: convert HTML content to plain text + HTML formatting (tags with indexes
    of their corresponding places in the text) 
    '''

    @abstractmethod
    def convert(self, token):
        '''
        Converts a given token to the target content type.
        
        @param token: str
            The string to be converted
        '''
    
    @abstractmethod
    def getContent(self):
        '''
        Return the converted content stream.
        '''
    
    @abstractmethod
    def getFormatting(self):
        '''
        Return the content formatting stream.
        '''

# --------------------------------------------------------------------

class IReader(metaclass=ABCMeta):
    '''
    Interface for content reader
    '''

    @abstractmethod
    def register(self, readers):
        '''
        Register itself in a dictionary of content-type:reader pairs
        
        @param readers: dict
            The content-type:readers dictionary
        '''

    @abstractmethod
    def parse(self, content):
        '''
        Parse the content and run it through the content converter.
        
        @param content: Content
            The content object
        '''
