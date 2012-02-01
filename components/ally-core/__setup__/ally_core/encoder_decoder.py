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
from ally.core.impl.processor.encdec_json import DecodingJSONHandler, \
    EncodingJSONHandler
from ally.core.impl.processor.encdec_xml import DecodingXMLHandler
from ally.core.spec.server import Processor
from . import use_old_encdec
from ally.core.impl.processor.encoder_text import EncodingTextHandler

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

@ioc.config
def content_types_yaml() -> dict:
    '''The YAML content types'''
    return {
            'text/yaml':None,
            'application/yaml':None,
            'yaml':'text/yaml',
            }
    
@ioc.entity
def encodingXML() -> Processor:
    if use_old_encdec():
        #TODO: DEPRECATED: To be removed when the new meta encoders are finalized
        from ally.core.impl.processor.encdec_xml import EncodingXMLHandler
        b = EncodingXMLHandler(); yield b
        b.resourcesManager = resourcesManager()
        b.normalizer = contentNormalizer()
        b.converterId = converterPath()
        b.charSetDefault = default_characterset()
        b.contentTypes = content_types_xml()
        b.encodingError = 'xmlcharrefreplace'
    else:
        from ally.core.impl.processor.encoder_xml import EncodingXMLHandler
        b = EncodingXMLHandler(); yield b
        b.normalizer = contentNormalizer()
        b.converterId = converterPath()
        b.charSetDefault = default_characterset()
        b.contentTypes = content_types_xml()
        b.encodingError = 'xmlcharrefreplace'

@ioc.entity   
def encoderTextJSON():
    import json
    def encodeJSON(obj, fwrite, charSet): json.dump(obj, fwrite)
    return encodeJSON

@ioc.entity
def encodingJSON() -> Processor:
    if use_old_encdec():
        #TODO: DEPRECATED: To be removed when the new meta encoders are finalized
        b = EncodingJSONHandler(); yield b
        b.resourcesManager = resourcesManager()
        b.normalizer = contentNormalizer()
        b.converterId = converterPath()
        b.charSetDefault = default_characterset()
        b.contentTypes = content_types_json()
        b.encodingError = 'backslashreplace'
    else:
        b = EncodingTextHandler(); yield b
        b.normalizer = contentNormalizer()
        b.converterId = converterPath()
        b.charSetDefault = default_characterset()
        b.contentTypes = content_types_json()
        b.encodingError = 'backslashreplace'
        b.encoder = encoderTextJSON()

@ioc.entity   
def encoderTextYAML():
    try:
        import yaml
        def encodeYAML(obj, fwrite, charSet): yaml.dump(obj, fwrite, default_flow_style=False)
        return encodeYAML
    except ImportError: return None

@ioc.entity
def encodingYAML() -> Processor:
    b = EncodingTextHandler(); yield b
    b.normalizer = contentNormalizer()
    b.converterId = converterPath()
    b.charSetDefault = default_characterset()
    b.contentTypes = content_types_yaml()
    b.encodingError = 'backslashreplace'
    b.encoder = encoderTextYAML()

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
def handlersEncoding():
    if use_old_encdec():
        #TODO: DEPRECATED: To be removed when the new meta encoders are finalized
        return [encodingXML(), encodingJSON()]
    return [encodingXML(), encodingJSON(), encodingYAML()]

@ioc.entity
def handlersDecoding(): return [decodingXML(), decodingJSON(), decodingNone()]

