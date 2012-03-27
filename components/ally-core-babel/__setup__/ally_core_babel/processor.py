'''
Created on Nov 24, 2011

@package: ally core babel
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the configurations for the processors used in handling the request.
'''

from ..ally_core.processor import converter, default_language
from ally.container import ioc
from ally.core.babel.processor.converter import BabelConverterHandler
from ally.core.spec.server import Processor

# --------------------------------------------------------------------
# Creating the processors used in handling the request

@ioc.replace(converter)
def converterBabel() -> Processor:
    from babel import localedata, core
    # Babel FIX: We need to adjust the dir name for locales since they need to be outside the .egg file
    localedata._dirname = localedata._dirname.replace('.egg', '')
    core._filename = core._filename.replace('.egg', '')

    b = BabelConverterHandler()
    b.languageDefault = default_language()
    return b
