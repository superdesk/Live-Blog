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
from ally.core.spec.resources import Normalizer, Converter
from ally.exception import DevelError
import logging
from ally.core.spec.data_meta import MetaModel, MetaCollection, MetaLink, MetaValue, \
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
    # A Callable(object, string) function used for creating the text generator object that takes as the first argument
    # the text object to be encoded, and on the last position the character set encoding to be used.
    namePath = 'href'
    # The name to use as the attribute in rendering the hyper link.
    nameResources = 'Resources'
    # The tag to be used as the main container for the resources.
    nameList = '%sList'
    # The name to use for rendering lists.
    nameTotal = 'total'
    # The name to use for rendering the attribute with the total count of elements in a part.

    def __init__(self):
        super().__init__()
        assert isinstance(self.normalizer, Normalizer), 'Invalid Normalizer object %s' % self.normalizer
        assert isinstance(self.converterId, Converter), 'Invalid Converter object %s' % self.converterId
        assert callable(self.encoder), 'Invalid callable encoder %s' % self.encoder
        assert isinstance(self.namePath, str), 'Invalid name path %s' % self.namePath
        assert isinstance(self.nameResources, str), 'Invalid name resources %s' % self.nameResources
        assert isinstance(self.nameList, str), 'Invalid name list %s' % self.nameList
        assert isinstance(self.nameTotal, str), 'Invalid name total %s' % self.nameTotal

    def encodeMeta(self, charSet, value, meta, asString, pathEncode):
        '''
        @see: EncodingTextBaseHandler.encodeMeta
        '''
        return self.encoder(self.convertMeta(value, meta, asString, pathEncode, self.normalizer.normalize, True),
                            charSet)

    def encodeObject(self, charSet, obj):
        '''
        @see: EncodingTextBaseHandler.encodeObject
        '''
        return self.encoder(obj, charSet)

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
            if meta.metaLink and (not first or len(meta.properties) < len(meta.model.properties)):
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

        elif isinstance(meta, MetaCollection):
            assert isinstance(meta, MetaCollection)
            assert log.debug('Encoding list of %s', meta.metaItem) or True
            items = meta.getItems(value)
            if items is None: return

            if isinstance(meta.metaItem, MetaValue):
                return [self.convertMeta(item, meta.metaItem, asString, pathEncode, normalize) for item in items]
            elif isinstance(meta.metaItem, MetaModel): name = normalize(self.nameList % meta.metaItem.model.name)
            elif isinstance(meta.metaItem, MetaLink): name = normalize(self.nameResources)
            else: raise DevelError('Illegal item meta %s for meta list %s' % (meta.metaItem, meta))

            obj = {name:[self.convertMeta(item, meta.metaItem, asString, pathEncode, normalize) for item in items]}
            if meta.getTotal: obj[normalize(self.nameTotal)] = str(meta.getTotal(value))
            return obj

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
            return {normalize(meta.getName(value)): {normalize(self.namePath): pathEncode(path)}}

        elif isinstance(meta, MetaFetch):
            assert isinstance(meta, MetaFetch)
            value = meta.getValue(value)
            if value is None: return
            return self.convertMeta(value, meta.meta, asString, pathEncode, normalize)

        else:
            raise DevelError('Unknown meta object %s' % meta)
