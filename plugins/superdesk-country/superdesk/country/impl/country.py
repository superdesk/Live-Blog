'''
Created on Jun 23, 2011

@package superdesk
@copyright 2011 Sourcefabric o.p.s.
@license http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

SQL alchemy implementation for language API.
'''

from ..api.country import Country, ICountryService
from ally.api.extension import IterPart
from ally.container import wire
from ally.container.ioc import injected
from ally.container.support import setup
from ally.exception import InputError, Ref
from ally.internationalization import _
from ally.support.api.util_service import trimIter, processQuery
from babel.core import Locale
from babel.localedata import locale_identifiers

# --------------------------------------------------------------------

class Countries(dict):
    '''
    A simple dictionary class used for marking the countries codes (as keys) and country default names (as values).
    '''

@injected
@setup(ICountryService, name='countryService')
class CountryServiceBabelAlchemy(ICountryService):
    '''
    Implementation for @see: ICountryService using Babel library for translating country names and for the country codes
    it uses an external source.
    '''

    countries = Countries; wire.entity('countries')

    def __init__(self):
        '''
        Construct the country service.
        '''
        assert isinstance(self.countries, Countries), 'Invalid countries %s' % self.countries
        self._locales = {code:Locale.parse(code) for code in locale_identifiers()}

    def getByCode(self, code, locales):
        '''
        @see: ICountryService.getByCode
        '''
        if code not in self.countries: raise InputError(Ref(_('Unknown country code'), ref=Country.Code))
        return Country(code, self._translate(code, self._localesOf(locales)))

    def getAllAvailable(self, locales, offset=None, limit=None, q=None):
        '''
        @see: ILanguageService.getAllAvailable
        '''
        locales = self._localesOf(locales)
        if q:
            countries = (Country(code, self._translate(code, locales)) for code in self.countries)
            countries = processQuery(countries, q, Country)
            length = len(countries)
            countries = trimIter(countries, length, offset, limit)
        else:
            length = len(self.countries)
            countries = trimIter(self.countries, length, offset, limit)
            countries = (Country(code, self._translate(code, locales)) for code in countries)
        return IterPart(countries, length, offset, limit)

    # ----------------------------------------------------------------

    def _localeOf(self, code):
        '''
        Helper that parses the code to a babel locale.
        
        @param code: string
            The language code to provide the locale for.
        @return: Locale|None
            The locale for the code or None if the code is not valid.
        '''
        assert isinstance(code, str), 'Invalid code %s' % code
        return self._locales.get(code.replace('-', '_'))

    def _localesOf(self, codes):
        '''
        Helper method that based on a language code list will provide a babel locales.
        
        @param codes: string|iter(string)
            The language code to provide the locale for.
        @return: Locale|None
            The locale for the code or None if the code is not valid.
        '''
        if isinstance(codes, str): codes = [codes]
        return list(filter(None, (self._localeOf(code) for code in codes)))

    def _translate(self, code, locales):
        '''
        Helper method that provides the translated country name for based on the babel locales list, the first
        locale will be used if not translation will be available for that than it will fall back to the next.
        
        @param code: string
            The country code to get the translated name for.
        @param locales: list[Locale]|tuple(Locale)
            The locales to translate the name for.
        @return: string
            The translated country name.
        '''
        assert isinstance(code, str), 'Invalid code %s' % code
        assert isinstance(locales, (list, tuple)), 'Invalid locales %s' % locales
        for loc in locales:
            assert isinstance(loc, Locale), 'Invalid locale %s' % loc
            translated = loc.territories.get(code)
            if translated: return translated
        return self.countries[code]
