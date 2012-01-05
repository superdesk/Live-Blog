'''
Created on Nov 24, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the configurations for the converters and normalizers.
'''

from ally.container import ioc
from ally.core.spec.resources import ConverterPath, Normalizer, Converter

# --------------------------------------------------------------------
# Creating the converters

@ioc.entity
def converterPath() -> Converter: return ConverterPath()

@ioc.entity
def contentNormalizer() -> Normalizer: return Normalizer()

@ioc.entity
def defaultErrorContentConverter() -> Converter:
    '''The default converter to be used if none can be obtained based on the request.'''
    return Converter()
