'''
Created on Jun 22, 2012

@package: ally core
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the XML encoder processor handler.
'''

from .base import RenderBaseHandler
from ally.container.ioc import injected
from ally.core.spec.transform.render import IRender
from ally.support.util import immut
from ally.support.util_io import IOutputStream
from codecs import getwriter
from collections import deque
from xml.sax.saxutils import XMLGenerator

# --------------------------------------------------------------------

@injected
class RenderXMLHandler(RenderBaseHandler):
    '''
    Provides the XML encoding.
    @see: RenderBaseHandler
    '''

    encodingError = 'xmlcharrefreplace'
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

        outputb = getwriter(charSet)(output, self.encodingError)
        xml = XMLGenerator(outputb, charSet, short_empty_elements=True)
        return RenderXML(xml)

# --------------------------------------------------------------------

class RenderXML(IRender):
    '''
    Renderer for xml.
    '''
    __slots__ = ('xml', 'processing')

    def __init__(self, xml):
        '''
        Construct the XML object renderer.
        
        @param xml: XMLGenerator
            The xml generator used to render the xml.
        '''
        assert isinstance(xml, XMLGenerator), 'Invalid xml generator %s' % xml

        self.xml = xml
        self.processing = deque()

    def value(self, name, value):
        '''
        @see: IRender.value
        '''
        self.xml.startElement(name, immut())
        self.xml.characters(value)
        self.xml.endElement(name)

    def objectStart(self, name, attributes=None):
        '''
        @see: IRender.objectStart
        '''
        if not self.processing: self.xml.startDocument() # Start the document
        self.processing.append(name)
        self.xml.startElement(name, attributes or immut())

    def objectEnd(self):
        '''
        @see: IRender.objectEnd
        '''
        assert self.processing, 'No object to end'

        self.xml.endElement(self.processing.pop())
        if not self.processing: self.xml.endDocument() # Close the document if there are no other processes queued

    def collectionStart(self, name, attributes=None):
        '''
        @see: IRender.collectionStart
        '''
        if not self.processing: self.xml.startDocument() # Start the document
        self.processing.append(name)
        self.xml.startElement(name, attributes or immut())

    def collectionEnd(self):
        '''
        @see: IRender.collectionEnd
        '''
        assert self.processing, 'No collection to end'

        self.xml.endElement(self.processing.pop())
        if not self.processing: self.xml.endDocument() # Close the document if there are no other processes queued
