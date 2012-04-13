'''
Created on Feb 29, 2012

@package: ally api
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides standard model objects.
'''

from ally.type_legacy import Iterable
import abc

# --------------------------------------------------------------------

class Content(metaclass=abc.ABCMeta):
    '''
    Class that provides a bytes content, usually the raw content provided in a request.
    '''

    @abc.abstractclassmethod
    def getCharSet(self):
        '''
        Provides the character set specified for the content.
        
        @return: string
            The specified character set for the content or None.
        '''

    @abc.abstractclassmethod
    def read(self, size=None):
        '''
        To read a file's contents, call f.read(size), which reads some quantity of data and returns it as a string.
        @param size: integer
            Is an optional numeric argument. When size is omitted or negative, the entire contents of the file will be
            read and returned; it's your problem if the file is twice as large as your machine's memory.
            Otherwise, at most size bytes are read and returned. If the end of the file has been reached, f.read()
            will return an empty string ("").
        @return: bytes
            The content.
        '''

class Part:
    '''
    Provides a wrapping for iterable objects that represent a part of a bigger collection. Basically beside the actual
    items this class objects also contain a total count of the big item collection that this iterable is part of.
    '''

    __slots__ = ('iter', 'total')

    def __init__(self, iter, total):
        '''
        Construct the partial iterable.
        
        @param iter: Iterable
            The iterable that provides the actual data.
        @param total: integer
            The total count of the elements from which this iterable is part of.
        '''
        assert isinstance(iter, Iterable), 'Invalid iterable %s' % iter
        assert isinstance(total, int), 'Invalid total count %s' % total
        assert total >= 0, 'Invalid total count %s, cannot be less then 0'
        self.iter = iter
        self.total = total

    __iter__ = lambda self: self.iter.__iter__()

    def __str__(self):
        return '%s[%s, %s]' % (self.__class__.__name__, self.total, self.iter)
