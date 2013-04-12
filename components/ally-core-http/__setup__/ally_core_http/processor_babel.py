'''
Created on Sep 14, 2012

@package: ally core http
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the configurations for the Babel conversion processor.
'''

from ..ally_core.processor import conversion, default_language, normalizer
from ..ally_core_http.processor import assemblyResources, \
    updateAssemblyResources
from ..ally_http.processor import contentTypeResponseEncode
from ally.container import ioc
from ally.design.processor.handler import Handler
import logging

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

try: import babel
except ImportError: log.info('No Babel library available, no Babel conversion')
else:
    babel = babel  # Just to avoid import warning
    # ----------------------------------------------------------------

    from ally.core.http.impl.processor.text_conversion import \
        BabelConversionDecodeHandler, BabelConversionEncodeHandler
    
    # --------------------------------------------------------------------
    
    @ioc.config
    def present_formatting():
        '''
        If true will place on the response header the used formatting for conversion of data.
        '''
        return True
    
    # --------------------------------------------------------------------
    
    @ioc.replace(conversion)
    def conversionBabel() -> Handler:
        b = BabelConversionDecodeHandler()
        b.languageDefault = default_language()
        b.normalizer = normalizer()
        return b
    
    @ioc.entity
    def babelConversionEncode() -> Handler: return BabelConversionEncodeHandler()
    
    # --------------------------------------------------------------------
    
    @ioc.after(updateAssemblyResources)
    def updateAssemblyResourcesForBabel():
        if present_formatting(): assemblyResources().add(babelConversionEncode(), after=contentTypeResponseEncode())
