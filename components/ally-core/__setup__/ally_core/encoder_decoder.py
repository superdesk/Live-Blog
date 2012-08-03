'''
Created on Nov 24, 2011

@package: ally core
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the configurations for the processors encoders and decoders.
'''

from ally.container import ioc
from ally.core.impl.processor.render.text import RenderTextHandler
from ally.core.impl.processor.render.xml import RenderXMLHandler
from ally.design.processor import Handler, Assembly
from ally.core.impl.processor.render.json import RenderJSONHandler

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
# Create the renders

@ioc.entity
def renderAssembly() -> Assembly:
    '''
    The assembly containing the response renders.
    '''
    return Assembly()

# JSON encode by using the text renderer.
#@ioc.entity
#def renderTextJSON():
#    import json
#    def renderJSON(obj, charSet, out): json.dump(obj, out)
#    return renderJSON
#
#@ioc.entity
#def renderJSON() -> Handler:
#    b = RenderTextHandler(); yield b
#    b.contentTypes = content_types_json()
#    b.rendererTextObject = renderTextJSON()

@ioc.entity
def renderTextYAML():
    import yaml
    def renderYAML(obj, charSet, out): yaml.dump(obj, out, default_flow_style=False)
    return renderYAML

@ioc.entity
def renderYAML() -> Handler:
    b = RenderTextHandler(); yield b
    b.contentTypes = content_types_yaml()
    b.rendererTextObject = renderTextYAML()

@ioc.entity
def renderJSON() -> Handler:
    b = RenderJSONHandler(); yield b
    b.contentTypes = content_types_json()

@ioc.entity
def renderXML() -> Handler:
    b = RenderXMLHandler(); yield b
    b.contentTypes = content_types_xml()

# --------------------------------------------------------------------
# Creating the decoding processors

# --------------------------------------------------------------------

@ioc.before(renderAssembly)
def updateRenderAssembly():
    renderAssembly().add(renderJSON())
    renderAssembly().add(renderXML())
    try: renderAssembly().add(renderYAML())
    except ImportError: pass
