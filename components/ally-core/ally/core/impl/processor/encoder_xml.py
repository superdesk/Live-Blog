'''
Created on Jan 30, 2012

@package: ally core
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the XML encoder processor handler.
'''

from .encoder_text_base import EncodingTextBaseHandler
from ally.container.ioc import injected
from ally.core.spec.data_meta import MetaModel, MetaValue, MetaLink, MetaList
from ally.core.spec.resources import Normalizer, Converter, Path
from ally.exception import DevelException
from ally.support.core.util_resources import nodeLongName
from xml.sax.saxutils import XMLGenerator
import logging
from numbers import Number

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

@injected
class EncodingXMLHandler(EncodingTextBaseHandler):
    '''
    Provides the text XML encoding.
    @see: EncodingTextBaseHandler
    '''
    
    normalizer = Normalizer
    # The normalizer used by the encoding for the XML tag names.
    converterId = Converter
    # The converter to use on the id's of the models.
    namePath = 'href'
    # The name to use as the attribute in rendering the hyper link.
    nameResources = 'Resources'
    # The tag to be used as the main container for the resources.
    nameList = '%sList'
    # The name to use for rendering lists.

    def __init__(self):
        super().__init__()
        assert isinstance(self.normalizer, Normalizer), 'Invalid Normalizer object %s' % self.normalizer
        assert isinstance(self.converterId, Converter), 'Invalid Converter object %s' % self.converterId
        assert isinstance(self.namePath, str), 'Invalid name path %s' % self.namePath
        assert isinstance(self.nameResources, str), 'Invalid name resources %s' % self.nameResources
        assert isinstance(self.nameList, str), 'Invalid name list %s' % self.nameList
    
    def encodeMeta(self, openTextWriter, charSet, value, meta, asString, pathEncode):
        '''
        @see: EncodingTextBaseHandler.encodeMeta
        '''
        assert callable(openTextWriter), 'Invalid open text %s' % openTextWriter
        xml = XMLGenerator(openTextWriter(), charSet, short_empty_elements=True)
        xml.startDocument()
        self.encodeMetaXML(xml, value, meta, asString, pathEncode, self.normalizer.normalize)
        xml.endDocument()
        
    def encodeObject(self, openTextWriter, charSet, obj):
        '''
        @see: EncodingTextBaseHandler.encodeObject
        '''
        assert callable(openTextWriter), 'Invalid open text %s' % openTextWriter
        xml = XMLGenerator(openTextWriter(), charSet, short_empty_elements=True)
        xml.startDocument()
        self.encodeDictXML(xml, obj, self.normalizer.normalize)
        xml.endDocument()
    
    # ----------------------------------------------------------------
    
    def encodeMetaXML(self, xml, value, meta, asString, pathEncode, normalize, name=None):
        '''
        Encodes the provided value into the xml based on the meta data.
        
        @param xml: XMLGenerator
            The XML to write to.
        @param value: object
            The value object to be encoded.
        @param meta: object meta
            The data meta of the object to encode.
        @param asString: Callable
            The call used converting values to string values.
        @param pathEncode: Callable
            The call used for encoding the path.
        @param normalize: Callable
            The call used for normalize the names.
        @param name: string
            The name for the current meta.
        @return: dictionary(string, ...}
            The text object.
        '''
        assert isinstance(xml, XMLGenerator), 'Invalid XML %s' % xml
        assert callable(asString), 'Invalid as string converter %s' % asString
        assert callable(pathEncode), 'Invalid path encoder %s' % pathEncode
        assert callable(normalize), 'Invalid normalize %s' % normalize
        
        if isinstance(meta, MetaModel):
            assert isinstance(meta, MetaModel)
            obj = meta.getModel(value)
            if len(meta) == 1:
                name_, m = next(iter(meta.items()))
                if isinstance(m, MetaLink):
                    self.encodeMetaXML(xml, obj, m, asString, pathEncode, normalize, name or meta.model.name)
                    return
                if isinstance(m, MetaValue):
                    self.encodeMetaXML(xml, obj, m, asString, pathEncode, normalize, name or name_)
                    return
                    
            tag = normalize(name) if name else normalize(meta.model.name)
            
            xml.startElement(tag, {})
            for name_, m in meta.items():
                self.encodeMetaXML(xml, obj, m, asString, pathEncode, normalize, name_)
            xml.endElement(tag)

        elif isinstance(meta, MetaList):
            assert isinstance(meta, MetaList)
            if name: tag = normalize(name)
            elif isinstance(meta.metaItem, MetaModel): tag = normalize(self.nameList % meta.metaItem.model.name)
            elif isinstance(meta.metaItem, MetaLink): tag = normalize(self.nameResources)
            else: tag = None 
            
            xml.startElement(tag, {})
            for item in meta.getItems(value):
                self.encodeMetaXML(xml, item, meta.metaItem, asString, pathEncode, normalize)
            xml.endElement(tag)
            
        elif isinstance(meta, MetaValue):
            assert isinstance(meta, MetaValue)
            assert isinstance(name, str), 'Expected a name for the meta value, got %s' % name
            tag = normalize(name)
            
            if meta.metaLink:
                assert isinstance(meta.metaLink, MetaLink), 'Invalid meta link %s' % meta.metaLink
                xml.startElement(tag, {normalize(self.namePath): pathEncode(meta.metaLink.getLink(value))})
            else: xml.startElement(tag, {})
            xml.characters(asString(meta.getValue(value), meta.type))
            xml.endElement(tag)

        elif isinstance(meta, MetaLink):
            assert isinstance(meta, MetaLink)
            path = meta.getLink(value)
            assert isinstance(path, Path), 'Invalid path %s' % path
            if name:
                tag = normalize(name)
                xml.startElement(tag, {normalize(self.namePath): pathEncode(path)})
            else:
                tag = normalize(nodeLongName(path.node))
                xml.startElement(tag, {normalize(self.namePath): pathEncode(path)})
            xml.endElement(tag)
        
        else:
            raise DevelException('Unknown meta object %s' % meta)

    def encodeDictXML(self, xml, value, normalize):
        '''
        Encodes a text object dictionary to XML.
        
        @param xml: XMLGenerator
            The XML to write to.
        @param value: dictionary
            The text value object to be encoded.
        @param normalize: Callable
            The call used for normalize the names.
        '''
        assert isinstance(xml, XMLGenerator), 'Invalid XML %s' % xml
        assert isinstance(value, dict), 'Invalid value %s' % value
        assert callable(normalize), 'Invalid normalize %s' % normalize
        
        for name, v in value.items():
            name = normalize(name)
            if isinstance(v, list):
                xml.startElement(name, {})
                self.encodeListXML(xml, v, normalize)
                xml.endElement(name)
            else:
                xml.startElement(name, {})
                if isinstance(v, dict):
                    self.encodeDictXML(xml, v, normalize)
                elif isinstance(v, (str, Number)):
                    xml.characters(v)
                else:
                    raise DevelException('Cannot encode value %r' % v)
                xml.endElement(name)

    def encodeListXML(self, xml, value, normalize):
        '''
        Encodes a text object dictionary to XML.
        
        @param xml: XMLGenerator
            The XML to write to.
        @param value: list|tuple
            The text value object to be encoded.
        @param normalize: Callable
            The call used for normalize the names.
        '''
        assert isinstance(xml, XMLGenerator), 'Invalid XML %s' % xml
        assert isinstance(value, (list, tuple)), 'Invalid value %s' % value
        assert callable(normalize), 'Invalid normalize %s' % normalize
        
        for v in value:
            if isinstance(v, dict):
                self.encodeDictXML(xml, v, normalize)
            elif isinstance(v, (str, Number)):
                xml.characters(v)
            else:
                raise DevelException('Cannot encode value %r' % value)
