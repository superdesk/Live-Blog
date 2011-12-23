'''
Created on Nov 24, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the configurations for the processors encoders and decoders.
'''

from ally.core.impl.processor.encdec_xml import EncodingXMLHandler, \
    DecodingXMLHandler
from ally.core.impl.processor.encdec_json import EncodingJSONHandler, \
    DecodingJSONHandler
from ally.core.impl.processor.decoder_none import DecodingNoneHandler

# --------------------------------------------------------------------
# Creating the encoding processors

def encodingXML(resourcesManager, contentNormalizer, converterPath,
        _defaultCharacterSet:'The default character set to use if none is provided in the request'='ISO-8859-1',
        _contentTypesXML:'The XML content types'={
                                                  'text/xml':None,
                                                  'text/plain':'text/xml',
                                                  'application/xml':None,
                                                  'xml':'text/xml'
                                                  }) -> EncodingXMLHandler:
    b = EncodingXMLHandler(); yield b
    b.resourcesManager = resourcesManager
    b.normalizer = contentNormalizer
    b.converterId = converterPath
    b.charSetDefault = _defaultCharacterSet
    b.contentTypes = _contentTypesXML
    b.encodingError = 'xmlcharrefreplace'

def encodingJSON(resourcesManager, contentNormalizer, converterPath, _defaultCharacterSet,
                 _contentTypesJSON:'The JSON content types'={
                                                             'text/json':None,
                                                             'application/json':None,
                                                             'json':'text/json',
                                                             None:'text/json'
                                                             }) -> EncodingJSONHandler:
    b = EncodingJSONHandler(); yield b
    b.resourcesManager = resourcesManager
    b.normalizer = contentNormalizer
    b.converterId = converterPath
    b.charSetDefault = _defaultCharacterSet
    b.contentTypes = _contentTypesJSON
    b.encodingError = 'backslashreplace'

# --------------------------------------------------------------------
# Creating the decoding processors

def decodingNone() -> DecodingNoneHandler: return DecodingNoneHandler()

def decodingXML(contentNormalizer, converterPath, _defaultCharacterSet, _contentTypesXML) -> DecodingXMLHandler:
    b = DecodingXMLHandler(); yield b
    b.normalizer = contentNormalizer
    b.converterId = converterPath
    b.charSetDefault = _defaultCharacterSet
    b.contentTypes = list(_contentTypesXML.keys())

def decodingJSON(contentNormalizer, converterPath, _defaultCharacterSet, _contentTypesJSON) -> DecodingJSONHandler:
    b = DecodingJSONHandler(); yield b
    b.normalizer = contentNormalizer
    b.converterId = converterPath
    b.charSetDefault = _defaultCharacterSet
    b.contentTypes = list(_contentTypesJSON.keys())

# ---------------------------------

handlersEncoding = lambda ctx: [ctx.encodingXML, ctx.encodingJSON]
handlersDecoding = lambda ctx: [ctx.decodingXML, ctx.decodingJSON, ctx.decodingNone]
