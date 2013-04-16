'''
Created on Feb 29, 2012

@package: ally api
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides standard model objects.
'''

from ally.support.util_io import IInputStream
import abc

# --------------------------------------------------------------------

class Content(IInputStream):
    '''
    Class that provides a bytes content, usually the raw content provided in a request.
    '''
    __slots__ = ('name', 'type', 'charSet', 'length')

    def __init__(self, name=None, type=None, charSet=None, length=None):
        '''
        Construct the content.
        
        @param name: string|None
            The name of the content, usually a file name.
        @param type: string|None
            The type of the content.
        @param charSet: string|None
            The character set specified for the content.
        @param length: integer|None
            The length in bytes for the content.
        '''
        assert name is None or isinstance(name, str), 'Invalid name %s' % name
        assert type is None or isinstance(type, str), 'Invalid type %s' % type
        assert charSet is None or isinstance(charSet, str), 'Invalid char set %s' % charSet
        assert length is None or isinstance(length, int), 'Invalid length %s' % length

        self.name = name
        self.type = type
        self.charSet = charSet
        self.length = length

    @abc.abstractclassmethod
    def next(self):
        '''
        Only call this method after the content has been properly processed, it will act also as a close method. If
        there is additional content available this method will return the next Content object otherwise it will return
        None.
        
        @return: Content|None
            The next content or None, if there is no more available.
        '''
