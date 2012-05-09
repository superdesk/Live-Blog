'''
Created on Jan 31, 2012

@package: ally core
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the configurations for the encoder text xml.
'''

from .converter import contentNormalizer, converterPath
from ally.container import ioc
from ally.core.spec.server import Processor, Processors
from ally.core.impl.processor.encoder_xml import EncodingXMLHandler
from .test_encoder_text import metaCreator

# --------------------------------------------------------------------

@ioc.entity
def encoderTextXML() -> Processor:
    b = EncodingXMLHandler()
    b.normalizer = contentNormalizer()
    b.converterId = converterPath()
    b.charSetDefault = 'UTF-8'
    b.contentTypes = {None:None}
    b.encodingError = 'xmlcharrefreplace'
    return b

@ioc.entity
def encoderXMLProcessors():
    return Processors(metaCreator(), encoderTextXML())

@ioc.entity
def encoderTextXMLProcessors():
    return Processors(encoderTextXML())

