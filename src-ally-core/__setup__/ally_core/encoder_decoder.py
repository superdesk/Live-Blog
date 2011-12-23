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
from ally import ioc
from ally.core.impl.processor.decoder_none import DecodingNoneHandler
from ally.core.impl.processor.encdec_json import EncodingJSONHandler, \
    DecodingJSONHandler
from ally.core.impl.processor.encdec_xml import EncodingXMLHandler, \
    DecodingXMLHandler

# --------------------------------------------------------------------
# Creating the encoding processors

defaultCharacterSet = ioc.config(lambda:'ISO-8859-1', 
                                 'The default character set to use if none is provided in the request')

contentTypesXML = ioc.config(lambda:{
                                     'text/xml':None,
                                     'text/plain':'text/xml',
                                     'application/xml':None,
                                     'xml':'text/xml'
                                     }, 'The XML content types')

@ioc.entity
def encodingXML() -> EncodingXMLHandler:
    b = EncodingXMLHandler(); yield b
    b.resourcesManager = resourcesManager()
    b.normalizer = contentNormalizer()
    b.converterId = converterPath()
    b.charSetDefault = defaultCharacterSet()
    b.contentTypes = contentTypesXML()
    b.encodingError = 'xmlcharrefreplace'

contentTypesJSON = ioc.config(lambda:{
                                      'text/json':None,
                                      'application/json':None,
                                      'json':'text/json',
                                      None:'text/json'
                                      }, 'The JSON content types')

@ioc.entity
def encodingJSON() -> EncodingJSONHandler:
    b = EncodingJSONHandler(); yield b
    b.resourcesManager = resourcesManager()
    b.normalizer = contentNormalizer()
    b.converterId = converterPath()
    b.charSetDefault = defaultCharacterSet()
    b.contentTypes = contentTypesJSON()
    b.encodingError = 'backslashreplace'

# --------------------------------------------------------------------
# Creating the decoding processors

decodingNone = ioc.entity(lambda: DecodingNoneHandler(), DecodingNoneHandler)

@ioc.entity
def decodingXML() -> DecodingXMLHandler:
    b = DecodingXMLHandler(); yield b
    b.normalizer = contentNormalizer()
    b.converterId = converterPath()
    b.charSetDefault = defaultCharacterSet()
    b.contentTypes = list(contentTypesXML().keys())

@ioc.entity
def decodingJSON() -> DecodingJSONHandler:
    b = DecodingJSONHandler(); yield b
    b.normalizer = contentNormalizer()
    b.converterId = converterPath()
    b.charSetDefault = defaultCharacterSet()
    b.contentTypes = list(contentTypesJSON().keys())

# ---------------------------------

handlersEncoding = ioc.entity(lambda: [encodingXML(), encodingJSON()])
handlersDecoding = ioc.entity(lambda: [decodingXML(), decodingJSON(), decodingNone()])
