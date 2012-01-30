'''
Created on Jan 30, 2012

@package: ally core
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the configurations setup for the meta processors.
'''

from __setup__.ally_core.encoder_decoder import content_types_xml, \
    content_types_json
from ally.container import ioc

# --------------------------------------------------------------------
# Creating the text encoder

@ioc.config
def content_types_yaml() -> dict:
    '''The YAML content types'''
    return {
            'text/yaml':None,
            'application/yaml':None,
            'yaml':'text/yaml',
            }

@ioc.entity   
def encoderTextJSON():
    import json
    def encodeJSON(obj, fwrite, charSet): json.dump(obj, fwrite)
    return encodeJSON

@ioc.entity   
def encoderTextYAML():
    try:
        import yaml
        def encodeYAML(obj, fwrite, charSet): yaml.dump(obj, fwrite, encoding=charSet, default_flow_style=False)
        return encodeYAML
    except ImportError: return None

@ioc.entity
def encodersText():
    encoders = [(content_types_xml(), None), (content_types_json(), encoderTextJSON())]
    if encoderTextYAML(): encoders.append((content_types_yaml(), encoderTextYAML()))
    return encoders

