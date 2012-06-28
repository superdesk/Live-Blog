'''
Created on Jun 22, 2012

@package: ally core
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the XML encoder processor handler.
'''

from .text_base import EncoderTextBaseHandler
from ally.container.ioc import injected
from ally.core.spec.meta import Meta, Object, Value, Collection
from ally.support.util import immut
from io import StringIO
from xml.sax.saxutils import XMLGenerator

# --------------------------------------------------------------------

@injected
class EncoderXMLHandler(EncoderTextBaseHandler):
    '''
    Provides the text object encoding.
    @see: EncodingTextBaseHandler
    '''

    def renderMeta(self, meta, charSet):
        '''
        @see: EncoderTextBaseHandler.renderMeta
        '''
        assert isinstance(meta, Meta), 'Invalid meta %s' % meta

        out = StringIO()
        xml = XMLGenerator(out, charSet, short_empty_elements=True)
        xml.startDocument()
        self.render(xml, meta)
        xml.endDocument()
        text = out.getvalue()
        out.close()
        return text

    def render(self, xml, meta):
        '''
        Render the provided meta.
        '''
        assert isinstance(xml, XMLGenerator), 'Invalid XML generator %s' % xml
        assert isinstance(meta, Meta), 'Invalid meta %s' % meta
        xml.startElement(meta.identifier, immut())

        if isinstance(meta, Object):
            assert isinstance(meta, Object)
            for prop in meta.properties: self.render(xml, prop)

        elif isinstance(meta, Collection):
            assert isinstance(meta, Collection)
            for item in meta.items: self.render(xml, item)

        else:
            assert isinstance(meta, Value), 'Unknown meta %s' % meta
            xml.characters(meta.value)

        xml.endElement(meta.identifier)
