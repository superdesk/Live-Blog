'''
Created on Nov 24, 2011

@package: ally core babel
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the configurations for the processors used in handling the request.
'''

from ..ally_core.processor import conversion, normalizer, default_language, \
    resourcesAssembly, invoking
from ally.container import ioc
from ally.core.babel.processor.text_conversion import \
    BabelConversionDecodeHandler, BabelConversionEncodeHandler
from ally.design.processor import Handler

# --------------------------------------------------------------------

@ioc.config
def present_formatting():
    '''
    If true will place on the response header the used formatting for conversion of data.
    '''
    return True

# --------------------------------------------------------------------

@ioc.replace(conversion)
def babelConversion() -> Handler:
    from babel import localedata, core
    #TODO: check if is still a problem in the new Babel version
    # Babel FIX: We need to adjust the dir name for locales since they need to be outside the .egg file
    localedata._dirname = localedata._dirname.replace('.egg', '')
    core._filename = core._filename.replace('.egg', '')

    b = BabelConversionDecodeHandler()
    b.languageDefault = default_language()
    b.normalizer = normalizer()
    return b

@ioc.entity
def babelConversionEncode() -> Handler: return BabelConversionEncodeHandler()

# --------------------------------------------------------------------

@ioc.before(resourcesAssembly)
def updateResourcesAssembly():
    if present_formatting(): resourcesAssembly().add(babelConversionEncode(), after=invoking())

