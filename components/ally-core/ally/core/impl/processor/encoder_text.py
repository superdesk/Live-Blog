'''
Created on Jan 25, 2012

@package: ally core
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the text encoder processor handler that creates text objects to be encoded.
'''

from .encoder_text_base import EncodingTextBaseHandler
from ally.container.ioc import injected
from ally.core.spec.resources import Normalizer, Converter, Path
from ally.exception import DevelException
from ally.support.core.util_resources import nodeLongName
import logging
from ally.core.spec.data_meta import MetaModel, MetaList, MetaLink, MetaValue, \
    MetaFetch

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

@injected
class EncodingTextHandler(EncodingTextBaseHandler):
    '''
    Provides the text object encoding.
    @see: EncodingTextBaseHandler
    '''
    
    normalizer = Normalizer
    # The normalizer used by the encoding for the XML tag names.
    converterId = Converter
    # The converter to use on the id's of the models.
    encoder = None
    # A Callable(object, file writer, string)) function used for dumping the text object that takes as the first argument
    # the text object to be encoded, the second the text file writer to dump to the encoded text and on the last position
    # the character set encoding used.
    namePath = 'href'
    # The name to use as the attribute in rendering the hyper link.

    def __init__(self):
        super().__init__()
        assert isinstance(self.normalizer, Normalizer), 'Invalid Normalizer object %s' % self.normalizer
        assert isinstance(self.converterId, Converter), 'Invalid Converter object %s' % self.converterId
        assert callable(self.encoder), 'Invalid callable encoder %s' % self.encoder
        assert isinstance(self.namePath, str), 'Invalid name path %s' % self.namePath
    
    def encodeMeta(self, openTextWriter, charSet, value, meta, asString, pathEncode):
        '''
        @see: EncodingTextBaseHandler.encodeMeta
        '''
        assert callable(openTextWriter), 'Invalid open text %s' % openTextWriter
        self.encoder(self.convertMeta(value, meta, asString, pathEncode, self.normalizer.normalize, True),
                     openTextWriter(), charSet)
        
    def encodeObject(self, openTextWriter, charSet, obj):
        '''
        @see: EncodingTextBaseHandler.encodeObject
        '''
        assert callable(openTextWriter), 'Invalid open text %s' % openTextWriter
        self.encoder(obj, openTextWriter(), charSet)
    
    # ----------------------------------------------------------------
    
    def convertMeta(self, value, meta, asString, pathEncode, normalize, first=False):
        '''
        Convert the provided value to a text object based on the  meta data.
        
        @param value: object
            The value object to be converter to text object.
        @param meta: object meta
            The data meta of the object to convert.
        @param asString: Callable
            The call used converting values to string values.
        @param pathEncode: Callable
            The call used for encoding the path.
        @param normalize: Callable
            The call used for normalize the names.
        @param first: boolean
            Flag indicating that is the first rendered object, False otherwise.
        @return: dictionary(string, ...}
            The text object.
        '''
        assert callable(asString), 'Invalid as string converter %s' % asString
        assert callable(pathEncode), 'Invalid path encoder %s' % pathEncode
        assert callable(normalize), 'Invalid normalize %s' % normalize
        assert isinstance(first, bool), 'Invalid first flag %s' % first
        
        if isinstance(meta, MetaModel):
            assert isinstance(meta, MetaModel)
            
            model = meta.getModel(value)
            if model is None: return
            
            assert log.debug('Encoding instance %s of %s', model, meta.model) or True
            
            obj = {}
            if meta.metaLink and not first:
                path = meta.metaLink.getLink(value)
                if path: obj[normalize(self.namePath)] = pathEncode(path)
                elif not meta.properties: return
            elif not meta.properties: return
            
            for pname, pmeta in meta.properties.items():
                if isinstance(pmeta, MetaLink):
                    path = pmeta.getLink(value)
                    if path is not None: pobj = {normalize(self.namePath): pathEncode(path)}
                else: pobj = self.convertMeta(model, pmeta, asString, pathEncode, normalize)
                if pobj is not None: obj[pname] = pobj

            return obj
            
        elif isinstance(meta, MetaList):
            assert isinstance(meta, MetaList)
            assert log.debug('Encoding list of %s', meta.metaItem) or True
            items = meta.getItems(value)
            if items is None: return
            return [self.convertMeta(item, meta.metaItem, asString, pathEncode, normalize) for item in items]
        
        elif isinstance(meta, MetaValue):
            assert isinstance(meta, MetaValue)
            assert log.debug('Encoding meta value %s of instance %s', meta, value) or True
            value = meta.getValue(value)
            if value is None: return
            return asString(value, meta.type)
        
        elif isinstance(meta, MetaLink):
            assert isinstance(meta, MetaLink)
            assert log.debug('Encoding meta link %s of instance %s', meta, value) or True
            
            path = meta.getLink(value)
            if path is None: return
            assert isinstance(path, Path)
            return {normalize(nodeLongName(path.node)): {normalize(self.namePath): pathEncode(path)}}
        
        elif isinstance(meta, MetaFetch):
            assert isinstance(meta, MetaFetch)
            value = meta.getValue(value)
            if value is None: return
            return self.convertMeta(value, meta.meta, asString, pathEncode, normalize)
            
        else:
            raise DevelException('Unknown meta object %s' % meta)
