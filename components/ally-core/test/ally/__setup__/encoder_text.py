'''
Created on Jan 25, 2012

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the configurations for the encoder text.
'''

from .converter import contentNormalizer, converterPath
from .resource_manager import resourcesManager
from ally.container import ioc
from ally.core.impl.processor.encdec_text import EncodingTextHandler
from ally.core.spec.server import Processor

# --------------------------------------------------------------------

@ioc.entity
def encoderText() -> Processor:
    encoder = EncodingTextHandler()
    encoder.resourcesManager = resourcesManager()
    encoder.normalizer = contentNormalizer()
    encoder.converterId = converterPath()
    return encoder
