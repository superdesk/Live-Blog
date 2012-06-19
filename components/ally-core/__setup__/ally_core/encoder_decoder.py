'''
Created on Nov 24, 2011

@package: ally core
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the configurations for the processors encoders and decoders.
'''

from ally.container import ioc
from ally.design.processor import Handler, Assembly
from ally.core.impl.processor.encoder.text import EncoderTextHandler
from ..ally_core.meta_service import modelMetaService

# --------------------------------------------------------------------
# Creating the encoding processors

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

# --------------------------------------------------------------------

@ioc.entity
def encodingAssembly() -> Assembly:
    '''
    The assembly containing the response encoders.
    '''
    return Assembly()

# --------------------------------------------------------------------

@ioc.entity
def encoderTextJSON():
    from json.encoder import JSONEncoder
    def encodeJSON(obj, charSet): return JSONEncoder().iterencode(obj)
    return encodeJSON

@ioc.entity
def encodingJSON() -> Handler:
    b = EncoderTextHandler(); yield b
    b.contentTypes = content_types_json()
    b.encodingError = 'backslashreplace'
    b.encoder = encoderTextJSON()
    b.modelMetaService = modelMetaService()

@ioc.entity
def encoderTextYAML():
    import yaml
    def encodeYAML(obj, charSet): yield yaml.dump(obj, default_flow_style=False)
    return encodeYAML

@ioc.entity
def encodingYAML() -> Handler:
    b = EncoderTextHandler(); yield b
    b.contentTypes = content_types_yaml()
    b.encodingError = 'backslashreplace'
    b.encoder = encoderTextYAML()
    b.modelMetaService = modelMetaService()

# --------------------------------------------------------------------
# Creating the decoding processors

# --------------------------------------------------------------------

@ioc.before(encodingAssembly)
def updateEncodingAssembly():
    encodingAssembly().add(encodingJSON())
    try: encodingAssembly().add(encodingYAML())
    except ImportError: pass

