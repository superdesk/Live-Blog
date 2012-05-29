'''
Created on Apr 24, 2012
@package: ally core
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides utility methods for the server specifications.
'''

from ally.core.spec.server import ContentRequest

# --------------------------------------------------------------------

class ContentDelegate(ContentRequest):
    '''
    Provides a class that implements the @see: ContentRequest methods by extracting data from a content file like object.
    '''

    def __init__(self, content):
        '''
        Constructs the content instance.
        
        @param content: content file like object
            The object with the 'read(nbytes)' and 'close()' methods to provide the content bytes.
        '''
        ContentRequest.__init__(self)
        assert content is not None and hasattr(content, 'read') and hasattr(content, 'close'), \
        'Invalid content file object %s' % content
        self._content = content

    def read(self, nbytes=None):
        '''
        Reads nbytes from the content, attention the content can be read only once.
        
        @param nbytes: integer|None
            The number of bytes to read, or None to read all remaining available bytes from the content.
        '''
        return self._content.read(nbytes)

    def close(self):
        '''
        @see: ContentRequest.close
        '''
        self._content.close()

class ContentLengthLimited(ContentRequest):
    '''
    Provides a class that implements the @see: ContentRequest methods by extracting data from a content file like object 
    for the length bytes.
    '''

    def __init__(self, content):
        '''
        Constructs the content instance.
        
        @param content: content file like object
            The object with the 'read(nbytes)' method to provide the content bytes.
        '''
        ContentRequest.__init__(self)
        assert content is not None and hasattr(content, 'read'), 'Invalid content file object %s' % content
        self._content = content

        self._closed = False
        self._offset = 0

    def read(self, nbytes=None):
        '''
        Reads nbytes from the content, attention the content can be read only once.
        
        @param nbytes: integer|None
            The number of bytes to read, or None to read all remaining available bytes from the content.
        '''
        if self._closed: raise ValueError('I/O operation on a closed content file')
        count = nbytes
        if self.length is not None:
            if self._offset >= self.length:
                return b''
            delta = self.length - self._offset
            if count is None:
                count = delta
            elif count > delta:
                count = delta
        bytes = self._content.read(count)
        self._offset += len(bytes)
        return bytes

    def close(self):
        '''
        @see: ContentRequest.close
        '''
        self._closed = True
