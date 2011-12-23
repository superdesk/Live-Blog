'''
Created on Nov 24, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the configurations for the processors used in handling the request.
'''

from ally.core.babel.processor.converter import BabelConverterHandler
from ally import ioc
from ..ally_core.processor import defaultLanguage
from ..ally_core.processor import converter

# --------------------------------------------------------------------
# Creating the processors used in handling the request

@ioc.replace(converter)
def converterBabel() -> BabelConverterHandler:
    from babel import localedata, core
    # Babel FIX: We need to adjust the dir name for locales since they need to be outside the .egg file
    localedata._dirname = localedata._dirname.replace('.egg', '')
    core._filename = core._filename.replace('.egg', '')
    
    b = BabelConverterHandler()
    b.languageDefault = defaultLanguage()
    return b
