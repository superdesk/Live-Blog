'''
Created on Nov 24, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the configurations for the converters and normalizers.
'''

from ally.core.spec.resources import ConverterPath, Normalizer, Converter

# --------------------------------------------------------------------
# Creating the converters

def converterPath() -> ConverterPath: return ConverterPath()

def contentNormalizer() -> Normalizer: return Normalizer()

def defaultErrorContentConverter() -> Converter:
    '''
    The default converter to be used if none can be obtained based on the request.
    '''
    return Converter()
