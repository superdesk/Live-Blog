'''
Created on Jan 25, 2012

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the text encoding/decoding processor handler.
'''

from ally.api.type import TypeProperty
from ally.container.ioc import injected
from ally.core.spec.data_meta import Object, List, ValueLink, Value, Link
from ally.core.spec.resources import Normalizer, Converter, ResourcesManager
from ally.core.spec.server import Processor, Request, Response, ProcessorsChain, \
    EncoderPath
from ally.exception import DevelException
from io import TextIOWrapper
from numbers import Number
import codecs
import logging

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

@injected
class EncodingTextHandler(Processor):
    '''
    Provides the text base encoding.
    
    Provides on request: NA
    Provides on response: the content response
    
    Requires on request: NA
    Requires on response: contentType, encoderPath, contentConverter, obj, [objType], [objMeta]
    '''
    
    resourcesManager = ResourcesManager
    # The resources manager used in locating the resource nodes for the id's presented.
    normalizer = Normalizer
    # The normalizer used by the encoding for the XML tag names.
    converterId = Converter
    # The converter to use on the id's of the models.
    encoder = None
    # A Callable(object, file writer, string)) function used for dumping the text object that takes as the first argument
    # the text object to be encoded, the second the text file writer to dump to the encoded text and on the last position
    # the character set encoding used.
    charSetDefault = str
    # The default character set to be used if none provided for the content.
    contentTypes = dict
    # The dictionary{string:string} containing as a key the content types specific for this encoder and as a value
    # the content type to set on the response, if None will use the key for the content type response. 
    encodingError = str
    # The encoding error resolving.
    namePath = 'href'
    # The name to use as the attribute in rendering the hyper link.

    def __init__(self):
        assert isinstance(self.resourcesManager, ResourcesManager), \
        'Invalid resources manager %s' % self.resourcesManager
        assert isinstance(self.normalizer, Normalizer), 'Invalid Normalizer object %s' % self.normalizer
        assert isinstance(self.converterId, Converter), 'Invalid Converter object %s' % self.converterId
        assert callable(self.encoder), 'Invalid callable encoder %s' % self.encoder
        assert isinstance(self.charSetDefault, str), 'Invalid default character set %s' % self.charSetDefault
        assert isinstance(self.contentTypes, dict), 'Invalid content types %s' % self.contentTypes
        assert isinstance(self.encodingError, str), 'Invalid string %s' % self.encodingError
        assert isinstance(self.namePath, str), 'Invalid name path %s' % self.namePath
    
    def process(self, req, rsp, chain):
        '''
        @see: Processor.process
        '''
        assert isinstance(req, Request), 'Invalid request %s' % req
        assert isinstance(rsp, Response), 'Invalid response %s' % rsp
        assert isinstance(chain, ProcessorsChain), 'Invalid processors chain %s' % chain
        # Check if the response is for this encoder
        if rsp.contentType not in self.contentTypes:
            assert log.debug('The content type %r is not for this %s encoder', rsp.contentType, self) or True
        elif not rsp.contentConverter:
            assert log.debug('The response has no content converter, not for this %s encoder', self) or True
        elif not rsp.encoderPath:
            assert log.debug('There is no path encoder on the response, not for this %s encoder', self) or True
        else:
            contentType = self.contentTypes[rsp.contentType]
            if contentType:
                assert log.debug('Normalized content type %r to %r', rsp.contentType, contentType) or True
                rsp.contentType = contentType
            
            # Handling the encoder and converter
            assert isinstance(rsp.contentConverter, Converter), 'Invalid content converter %s' % rsp.contentConverter
            asString = rsp.contentConverter.asString
            assert isinstance(rsp.encoderPath, EncoderPath), 'Invalid encoder path %s' % rsp.encoderPath
            pathEncode = rsp.encoderPath.encode
            
            if not rsp.objMeta:
                if isValid(rsp.obj):
                    # Expecting a plain dictionary dictionary or list for rendering
                    obj = rsp.obj
                else:
                    obj = None
                    assert log.debug('There is no meta object or valid object on the response, not for this %s encoder',
                                     self) or True
            else:
                # Processing conversion
                obj = self.convertMeta(rsp.obj, rsp.objMeta, asString, pathEncode)
            
            if obj is not None:
                # Resolving the character set
                if rsp.charSet:
                    try: codecs.lookup(rsp.charSet)
                    except LookupError: rsp.charSet = None
                if not rsp.charSet:
                    for charSet in req.accCharSets:
                        try: codecs.lookup(charSet)
                        except LookupError: continue
                        rsp.charSet = charSet
                        break
                    else: rsp.charSet = self.charSetDefault
                    
                self.encoder(obj, TextIOWrapper(rsp.dispatch(), rsp.charSet, self.encodingError), rsp.charSet)
                return
        
        chain.process(req, rsp)
    
    # ----------------------------------------------------------------
        
    def convertMeta(self, value, meta, asString, pathEncode, level=0):
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
        @param level: integer
            Used for recursive purpose to find out the meta child level.
        @return: dictionary(string, ...}
            The text object.
        '''
        assert callable(asString), 'Invalid as string converter %s' % asString
        assert callable(pathEncode), 'Invalid path encoder %s' % pathEncode
        
        if isinstance(meta, Object):
            assert isinstance(meta, Object)
            obj = meta.getObject(value)
            if level == 0 and len(meta.properties) == 1:
                m = next(iter(meta.properties.values()))
                if isinstance(m, Link):
                    return self.convertMeta(obj, m, asString, pathEncode, level + 1)
            return {
                    self.normalizer.normalize(name): self.convertMeta(obj, m, asString, pathEncode, level + 1)
                    for name, m in meta.properties.items()
                    }
        elif isinstance(meta, List):
            assert isinstance(meta, List)
            items, m = meta.getItems(value), meta.itemMeta
            return [self.convertMeta(item, m, asString, pathEncode, level) for item in items]
        elif isinstance(meta, ValueLink):
            assert isinstance(meta, ValueLink)
            normalize, typ = self.normalizer.normalize, meta.type
            assert isinstance(typ, TypeProperty), 'Expected a type property for a value link, got %s' % typ
            return {
                    normalize(self.namePath): pathEncode(meta.getLink(value)),
                    normalize(typ.property.name): asString(meta.getValue(value), typ)
                    }
        elif isinstance(meta, Link):
            return {self.normalizer.normalize(self.namePath): pathEncode(meta.getLink(value))}
        elif isinstance(meta, Value):
            return asString(meta.getValue(value), meta.type)
        else:
            raise DevelException('Unknown meta object %s' % meta)
        
# --------------------------------------------------------------------

def isValid(obj):
    '''
    Checks if the provided object is valid as a text object.
    
    @param obj: dictionary(string, string|list[string]|dictionary{string, ...}}
        The object to be checked.
    @return: boolean
        true if the object is valid, False otherwise.
    '''
    if not isinstance(obj, dict): return False
    for key, value in obj.items():
        if not isinstance(key, (str, Number)): return False
        if isinstance(value, list):
            for ele in value:
                if not isinstance(ele, (str, Number)) and not isValid(ele): return False
        elif not isinstance(value, (str, Number)) and not isValid(value) :return False
    return True

