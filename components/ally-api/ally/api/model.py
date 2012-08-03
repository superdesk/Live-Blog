'''
Created on Feb 29, 2012

@package: ally api
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides standard model objects.
'''

import abc

# --------------------------------------------------------------------

class Content(metaclass=abc.ABCMeta):
    '''
    Class that provides a bytes content, usually the raw content provided in a request.
    '''

    @abc.abstractclassmethod
    def getName(self):
        '''
        Provides the name of the content, usually a file name.
        
        @return: string|None
            The content name or None if not available.
        '''

    @abc.abstractclassmethod
    def getCharSet(self):
        '''
        Provides the character set specified for the content.
        
        @return: string|None
            The specified character set for the content or None, if no such information is available.
        '''

    @abc.abstractclassmethod
    def getLength(self):
        '''
        Provides the length in bytes for the content.
        
        @return: integer|None
            The length for the content or None, if no such information is available.
        '''

    @abc.abstractclassmethod
    def read(self, nbytes=None):
        '''
        To read a file's contents, call f.read(size), which reads some quantity of data and returns it as a string.
        @param nbytes: integer
            Is an optional numeric argument. When size is omitted or negative, the entire contents of the file will be
            read and returned; it's your problem if the file is twice as large as your machine's memory.
            Otherwise, at most size bytes are read and returned. If the end of the file has been reached, f.read()
            will return an empty string ("").
        @return: bytes
            The content.
        '''

    @abc.abstractclassmethod
    def next(self):
        '''
        Only call this method after the content has been properly processed, it will act also as a close method but if
        there is additional content available this method will return the next Content object otherwise it will return
        None.
        
        @return: Content|None
            The next content or None, if there is no more available.
        '''
