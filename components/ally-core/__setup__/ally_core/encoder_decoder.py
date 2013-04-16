'''
Created on Nov 24, 2011

@package: ally core
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the configurations for the processors encoders and decoders.
'''

from ally.container import ioc
from ally.core.impl.processor.parser.text import ParseTextHandler
from ally.core.impl.processor.parser.xml import ParseXMLHandler
from ally.core.impl.processor.render.json import RenderJSONHandler
from ally.core.impl.processor.render.text import RenderTextHandler
from ally.core.impl.processor.render.xml import RenderXMLHandler
from ally.design.processor.assembly import Assembly
from ally.design.processor.handler import Handler
import codecs
import logging

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------
# Creating the encoding processors

@ioc.config
def content_types_json() -> dict:
    '''
    The JSON content types, a map that contains as a key the recognized mime type and as a value the normalize mime type,
    if none then the same key mimie type will be used for response
    '''
    return {
            'text/json':None,
            'application/json':None,
            'json':'text/json',
            None:'text/json'
            }

@ioc.config
def content_types_xml() -> dict:
    '''
    The XML content types, a map that contains as a key the recognized mime type and as a value the normalize mime type,
    if none then the same key mimie type will be used for response
    '''
    return {
            'text/xml':None,
            'text/plain':'text/xml',
            'application/xml':None,
            'xml':'text/xml'
            }

@ioc.config
def content_types_yaml() -> dict:
    '''
    The YAML content types, a map that contains as a key the recognized mime type and as a value the normalize mime type,
    if none then the same key mimie type will be used for response.
    '''
    return {
            'text/yaml':None,
            'application/yaml':None,
            'yaml':'text/yaml',
            }

# --------------------------------------------------------------------
# Create the renders

@ioc.entity
def renderingAssembly() -> Assembly:
    '''
    The assembly containing the response renders.
    '''
    return Assembly('Renderer selection')

@ioc.entity
def assemblyParsing() -> Assembly:
    '''
    The assembly containing the request parsers.
    '''
    return Assembly('Parsing request content')

@ioc.entity
def renderJSON() -> Handler:
    b = RenderJSONHandler(); yield b
    b.contentTypes = content_types_json()

# JSON encode by using the text renderer.
# @ioc.entity
# def renderJSON() -> Handler:
#    import json
#    def rendererJSON(obj, charSet, out): json.dump(obj, out)
#
#    b = RenderTextHandler(); yield b
#    b.contentTypes = content_types_json()
#    b.rendererTextObject = rendererJSON

@ioc.entity
def renderXML() -> Handler:
    b = RenderXMLHandler(); yield b
    b.contentTypes = content_types_xml()

# --------------------------------------------------------------------
# Creating the parsers

@ioc.entity
def parseJSON() -> Handler:
    import json
    def parserJSON(content, charSet): return json.load(codecs.getreader(charSet)(content))

    b = ParseTextHandler(); yield b
    b.contentTypes = set(content_types_json())
    b.parser = parserJSON
    b.parserName = 'json'

@ioc.entity
def parseXML() -> Handler:
    b = ParseXMLHandler(); yield b
    b.contentTypes = set(content_types_xml())

# --------------------------------------------------------------------

@ioc.before(assemblyParsing)
def updateAssemblyParsing():
    assemblyParsing().add(parseJSON())
    assemblyParsing().add(parseXML())

try: import yaml
except ImportError: log.info('No YAML library available, no yaml available for output or input')
else:
    
    # ----------------------------------------------------------------
    
    @ioc.entity
    def renderYAML() -> Handler:
        def rendererYAML(obj, charSet, out): yaml.dump(obj, out, default_flow_style=False)
    
        b = RenderTextHandler(); yield b
        b.contentTypes = content_types_yaml()
        b.rendererTextObject = rendererYAML
    
    @ioc.before(renderingAssembly)
    def updateRenderingAssembly():
        renderingAssembly().add(renderJSON())
        renderingAssembly().add(renderXML())
        renderingAssembly().add(renderYAML())


    @ioc.entity
    def parseYAML() -> Handler:
        def parserYAML(content, charSet): return yaml.load(codecs.getreader(charSet)(content))
    
        b = ParseTextHandler(); yield b
        b.contentTypes = set(content_types_yaml())
        b.parser = parserYAML
        b.parserName = 'yaml'
        
    @ioc.before(assemblyParsing)
    def updateAssemblyParsingWithYAML():
        assemblyParsing().add(parseYAML())
