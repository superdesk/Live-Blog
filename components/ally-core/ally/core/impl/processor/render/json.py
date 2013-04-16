'''
Created on Aug 3, 2012

@package: ally core
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the JSON encoder processor handler.
'''

from .base import RenderBaseHandler
from ally.container.ioc import injected
from ally.core.spec.transform.render import IRender
from ally.support.util_io import IOutputStream
from codecs import getwriter
from collections import deque
from json.encoder import encode_basestring

# --------------------------------------------------------------------

@injected
class RenderJSONHandler(RenderBaseHandler):
    '''
    Provides the JSON encoding.
    @see: RenderBaseHandler
    '''

    encodingError = 'backslashreplace'
    # The encoding error resolving.

    def __init__(self):
        assert isinstance(self.encodingError, str), 'Invalid string %s' % self.encodingError
        super().__init__()

    def renderFactory(self, charSet, output):
        '''
        @see: RenderBaseHandler.renderFactory
        '''
        assert isinstance(charSet, str), 'Invalid char set %s' % charSet
        assert isinstance(output, IOutputStream), 'Invalid content output stream %s' % output

        return RenderJSON(getwriter(charSet)(output, self.encodingError))

# --------------------------------------------------------------------

class RenderJSON(IRender):
    '''
    Renderer for JSON.
    '''
    __slots__ = ('out', 'isObject', 'isFirst')

    def __init__(self, out):
        '''
        Construct the text object renderer.
        
        @param out: file writer
            The writer to place the JSON.
        '''
        assert out, 'Invalid JSON output stream %s' % out

        self.out = out
        self.isObject = deque()
        self.isFirst = True

    def value(self, name, value):
        '''
        @see: IRender.value
        '''
        assert self.isObject, 'No container for value'
        assert isinstance(name, str), 'Invalid name %s' % name
        assert isinstance(value, str), 'Invalid value %s' % value
        out = self.out

        if self.isFirst: self.isFirst = False
        else: out.write(',')
        if self.isObject[0]:
            out.write(encode_basestring(name))
            out.write(':')
            out.write(encode_basestring(value))
        else: out.write(encode_basestring(value))

    def objectStart(self, name, attributes=None):
        '''
        @see: IRender.objectStart
        '''
        self.openObject(name, attributes)
        self.isObject.appendleft(True)

    def objectEnd(self):
        '''
        @see: IRender.objectEnd
        '''
        assert self.isObject, 'No object to end'
        isObject = self.isObject.popleft()
        assert isObject, 'No object to end'

        self.out.write('}')

    def collectionStart(self, name, attributes=None):
        '''
        @see: IRender.collectionStart
        '''
        assert isinstance(name, str), 'Invalid name %s' % name
        out = self.out

        self.openObject(name, attributes)
        if not self.isFirst: out.write(',')
        out.write(encode_basestring(name))
        out.write(':[')
        self.isFirst = True
        self.isObject.appendleft(False)

    def collectionEnd(self):
        '''
        @see: IRender.collectionEnd
        '''
        assert self.isObject, 'No collection to end'
        isObject = self.isObject.popleft()
        assert not isObject, 'No collection to end'

        self.out.write(']}')

    # ----------------------------------------------------------------

    def openObject(self, name, attributes=None):
        '''
        Used to open a JSON object.
        '''
        assert isinstance(name, str), 'Invalid name %s' % name
        assert attributes is None or isinstance(attributes, dict), 'Invalid attributes %s' % attributes
        out = self.out

        if not self.isFirst: out.write(',')

        if self.isObject and self.isObject[0]:
            out.write(encode_basestring(name))
            out.write(':')

        out.write('{')
        self.isFirst = True
        if attributes:
            for attrName, attrValue in attributes.items():
                assert isinstance(attrName, str), 'Invalid attribute name %s' % attrName
                assert isinstance(attrValue, str), 'Invalid attribute value %s' % attrValue

                if self.isFirst: self.isFirst = False
                else: out.write(',')
                out.write(encode_basestring(attrName))
                out.write(':')
                out.write(encode_basestring(attrValue))
