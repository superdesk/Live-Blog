'''
Created on Nov 24, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the configurations for the processors encoders and decoders.
'''

from .converter import contentNormalizer, converterPath
from .resource_manager import resourcesManager
from ally.container import ioc
from ally.core.impl.processor.decoder_none import DecodingNoneHandler
from ally.core.impl.processor.encdec_json import EncodingJSONHandler, \
    DecodingJSONHandler
from ally.core.impl.processor.encdec_xml import EncodingXMLHandler, \
    DecodingXMLHandler
from ally.core.spec.server import Processor
from ally.core.impl.processor.encdec_text import EncodingTextHandler
from ally.core.impl.processor.encdec_text_support.encoder_xml import XMLEncoder

# --------------------------------------------------------------------
# Creating the encoding processors

@ioc.config
def default_characterset() -> str:
    '''The default character set to use if none is provided in the request'''
    return 'ISO-8859-1'

@ioc.config
def content_types_xml() -> dict:
    '''The XML content types'''
    return {
            'text/xml':None,
            'text/plain':'text/xml',
            'application/xml':None,
            'xml':'text/xml'
            }

@ioc.config
def content_types_json() -> dict:
    '''The JSON content types'''
    return {
            'text/json':None,
            'application/json':None,
            'json':'text/json',
            None:'text/json'
            }

@ioc.entity
def encodingXML() -> Processor:
    b = EncodingXMLHandler(); yield b
    b.resourcesManager = resourcesManager()
    b.normalizer = contentNormalizer()
    b.converterId = converterPath()
    b.charSetDefault = default_characterset()
    b.contentTypes = content_types_xml()
    b.encodingError = 'xmlcharrefreplace'

@ioc.entity
def encodingJSON() -> Processor:
    b = EncodingJSONHandler(); yield b
    b.resourcesManager = resourcesManager()
    b.normalizer = contentNormalizer()
    b.converterId = converterPath()
    b.charSetDefault = default_characterset()
    b.contentTypes = content_types_json()
    b.encodingError = 'backslashreplace'

# --------------------------------------------------------------------
# Creating the decoding processors

@ioc.entity
def decodingNone() -> Processor: return DecodingNoneHandler()

@ioc.entity
def decodingXML() -> Processor:
    b = DecodingXMLHandler(); yield b
    b.normalizer = contentNormalizer()
    b.converterId = converterPath()
    b.charSetDefault = default_characterset()
    b.contentTypes = list(content_types_xml().keys())

@ioc.entity
def decodingJSON() -> Processor:
    b = DecodingJSONHandler(); yield b
    b.normalizer = contentNormalizer()
    b.converterId = converterPath()
    b.charSetDefault = default_characterset()
    b.contentTypes = list(content_types_json().keys())

# ---------------------------------

@ioc.entity
def handlersEncoding(): return [encodingXML(), encodingJSON()]

@ioc.entity
def handlersDecoding(): return [decodingXML(), decodingJSON(), decodingNone()]

# --------------------------------------------------------------------
# Creating the text encoder

@ioc.entity   
def encoderTextXML():
    b = XMLEncoder()
    ioc.initialize(b)
    return b.encode

@ioc.entity   
def encoderTextJSON():
    import json
    def encodeJSON(obj, fwrite, charSet): json.dump(obj, fwrite)
    return encodeJSON

@ioc.entity
def encodersText():
    return [(content_types_xml(), encoderTextXML()), (content_types_json(), encoderTextJSON())]

@ioc.entity   
def encodingText() -> Processor:
    b = EncodingTextHandler()
    b.resourcesManager = resourcesManager()
    b.normalizer = contentNormalizer()
    b.converterId = converterPath()
    b.encoders = encodersText()
    b.charSetDefault = default_characterset()
    return b
