'''
Created on Nov 24, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the configurations for the converters and normalizers.
'''

from ally import ioc
from ally.core.spec.resources import ConverterPath, Normalizer, Converter

# --------------------------------------------------------------------
# Creating the converters

converterPath = ioc.entity(lambda: ConverterPath(), ConverterPath)

contentNormalizer = ioc.entity(lambda: Normalizer(), Normalizer)

defaultErrorContentConverter = ioc.entity(lambda: Converter(), Converter)
# The default converter to be used if none can be obtained based on the request.
