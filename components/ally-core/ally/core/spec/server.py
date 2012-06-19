'''
Created on Jun 28, 2011

@package: ally core
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Module containing specifications for the server processing.
'''

import abc
import logging

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

class IStream(metaclass=abc.ABCMeta):
    '''
    The specification for a linked stream.
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

    @abc.abstractclassmethod
    def close(self):
        '''
        Closes the stream.
        '''

    @classmethod
    def __subclasshook__(cls, C):
        if cls is IStream:
            if (any('read' in B.__dict__ for B in C.__mro__) and
                any('close' in B.__dict__ for B in C.__mro__)):
                return True
        return NotImplemented

