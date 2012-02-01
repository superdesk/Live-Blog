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
from ally.core.spec.data_meta import MetaModel, MetaValue, MetaLink, MetaList, \
    MetaFetch
from ally.core.spec.resources import Normalizer, Converter, Path
from ally.exception import DevelException
from ally.support.core.util_resources import nodeLongName
from numbers import Number
from xml.sax.saxutils import XMLGenerator
import logging

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
        self.encodeMetaXML(xml, value, meta, asString, pathEncode, self.normalizer.normalize, None, True)
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
    
    def encodeMetaXML(self, xml, value, meta, asString, pathEncode, normalize, name=None, first=False):
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
            The name of the encoded meta.
        @param first: boolean
            Flag indicating that is the first rendered object, False otherwise.
        @return: dictionary(string, ...}
            The text object.
        '''
        assert isinstance(xml, XMLGenerator), 'Invalid XML %s' % xml
        assert callable(asString), 'Invalid as string converter %s' % asString
        assert callable(pathEncode), 'Invalid path encoder %s' % pathEncode
        assert callable(normalize), 'Invalid normalize %s' % normalize
        assert name is None or isinstance(name, str), 'Invalid name %s' % name
        assert isinstance(first, bool), 'Invalid first flag %s' % first
        
        if isinstance(meta, MetaModel):
            assert isinstance(meta, MetaModel)
            
            model = meta.getModel(value)
            if model is None: return
            
            assert log.debug('Encoding instance %s of %s', model, meta.model) or True
            
            attrs = {}
            if meta.metaLink and not first:
                path = meta.metaLink.getLink(value)
                if path: attrs[normalize(self.namePath)] = pathEncode(path)
                elif not meta.properties: return
            elif not meta.properties: return

            tag = normalize(name) if name else  normalize(meta.model.name)
            xml.startElement(tag, attrs)
            for pname, pmeta in meta.properties.items():
                self.encodeMetaXML(xml, model, pmeta, asString, pathEncode, normalize, pname)
            xml.endElement(tag)

        elif isinstance(meta, MetaList):
            assert isinstance(meta, MetaList)
            assert log.debug('Encoding list of %s', meta.metaItem) or True
            
            if name: tag = normalize(name)
            elif isinstance(meta.metaItem, MetaModel): tag = normalize(self.nameList % meta.metaItem.model.name)
            elif isinstance(meta.metaItem, MetaLink): tag = normalize(self.nameResources)
            else: raise DevelException('Illegal item meta %s for meta list %s' % (meta.metaItem, meta)) 
            
            items = meta.getItems(value)
            if items is None: return
            xml.startElement(tag, {})
            for item in items:
                self.encodeMetaXML(xml, item, meta.metaItem, asString, pathEncode, normalize)
            xml.endElement(tag)
            
        elif isinstance(meta, MetaValue):
            assert isinstance(meta, MetaValue)
            assert isinstance(name, str), 'Expected a name for meta value'
            assert log.debug('Encoding meta value %s of instance %s', meta, value) or True
            
            value = meta.getValue(value)
            if value is None: return
            tag = normalize(name)
            xml.startElement(tag, {})
            xml.characters(asString(value, meta.type))
            xml.endElement(tag)

        elif isinstance(meta, MetaLink):
            assert isinstance(meta, MetaLink)
            assert log.debug('Encoding meta link %s of instance %s', meta, value) or True
            
            path = meta.getLink(value)
            if path is None: return
            assert isinstance(path, Path)
            if name: tag = normalize(name)
            else: tag = normalize(nodeLongName(path.node))
            xml.startElement(tag, {normalize(self.namePath): pathEncode(path)})
            xml.endElement(tag)
            
        elif isinstance(meta, MetaFetch):
            assert isinstance(meta, MetaFetch)
            value = meta.getValue(value)
            if value is None: return
            return self.encodeMetaXML(xml, value, meta.meta, asString, pathEncode, normalize, name)
        
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
