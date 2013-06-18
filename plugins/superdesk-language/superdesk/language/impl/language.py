'''
Created on Jun 23, 2011

@package superdesk
@copyright 2011 Sourcefabric o.p.s.
@license http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

SQL alchemy implementation for language API.
'''

from ally.container.binder_op import validateProperty
from ally.container.ioc import injected
from ally.container.support import setup
from ally.exception import InputError, DevelError, Ref
from ally.internationalization import _
from ally.support.api.util_service import trimIter, processQuery
from babel.core import Locale
from babel.localedata import locale_identifiers
from collections import OrderedDict
from sql_alchemy.impl.entity import EntityNQServiceAlchemy
from superdesk.language.api.language import Language, ILanguageService
from superdesk.language.meta.language import LanguageEntity
from ally.api.extension import IterPart

# --------------------------------------------------------------------

@injected
@setup(ILanguageService, name='languageService')
class LanguageServiceBabelAlchemy(EntityNQServiceAlchemy, ILanguageService):
    '''
    Implementation for @see: ILanguageService using Babel library.
    '''

    def __init__(self):
        '''
        Construct the language service.
        '''
        EntityNQServiceAlchemy.__init__(self, LanguageEntity)
        locales = [(code, Locale.parse(code)) for code in locale_identifiers()]
        locales.sort(key=lambda pack: pack[0])
        self._locales = OrderedDict(locales)
        validateProperty(LanguageEntity.Code, self._validateCode)

    def getByCode(self, code, locales):
        '''
        @see: ILanguageService.getByCode
        '''
        locale = self._localeOf(code)
        if not locale: raise InputError(Ref(_('Unknown language code'), ref=Language.Code))
        return self._populate(Language(code), self._translator(locale, self._localesOf(locales)))

    def getAllAvailable(self, locales, offset=None, limit=None, q=None):
        '''
        @see: ILanguageService.getAllAvailable
        '''
        locales = self._localesOf(locales)
        if q:
            languages = (self._populate(Language(code), self._translator(locale, locales))
                         for code, locale in self._locales.items())
            languages = processQuery(languages, q, Language)
            length = len(languages)
            languages = trimIter(languages, length, offset, limit)
        else:
            length = len(self._locales)
            languages = trimIter(self._locales.items(), length, offset, limit)
            languages = (self._populate(Language(code), self._translator(locale, locales))
                         for code, locale in languages)
        return IterPart(languages, length, offset, limit)

    def getById(self, id, locales):
        '''
        @see: ILanguageService.getById
        '''
        locales = self._localesOf(locales)
        language = self.session().query(LanguageEntity).get(id)
        if not language: raise InputError(Ref(_('Unknown language id'), ref=LanguageEntity.Id))
        return self._populate(language, self._translator(self._localeOf(language.Code), locales))

    def getAll(self, locales=(), offset=None, limit=None, detailed=False):
        '''
        @see: ILanguageService.getAll
        '''
        locales = self._localesOf(locales)
        if detailed: languages, total = self._getAllWithCount(offset=offset, limit=limit)
        else: languages = self._getAll(offset=offset, limit=limit)
        languages = (self._populate(language, self._translator(self._localeOf(language.Code), locales))
                for language in languages)
        if detailed: return IterPart(languages, total, offset, limit)
        return languages

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

    def _translator(self, locale, locales):
        '''
        Helper method that provides the translated language name for locale based on the locales list, the first
        locale will be used if not translation will be available for that than it will fall back to the next.

        @param locale: Locale
            The locale to get the translator for.
        @param locales: list[Locale]|tuple(Locale)
            The locales to translate the name for.
        @return: Locale
            The translating locale.
        '''
        assert isinstance(locale, Locale), 'Invalid locale %s' % locale
        assert isinstance(locales, (list, tuple)), 'Invalid locales %s' % locales
        for loc in locales:
            assert isinstance(loc, Locale), 'Invalid locale %s' % loc
            if locale.language in loc.languages: return loc
        return locale

    def _populate(self, language, translator):
        '''
        Helper method that populates directly the language with the translation name.

        @param language: Language
            The language to be populated with info from the locale.
        @param translator: Locale
            The translating locale to populate from.
        '''
        assert isinstance(language, Language), 'Invalid language %s' % language
        assert isinstance(translator, Locale), 'Invalid translator locale %s' % translator

        locale = self._localeOf(language.Code)
        if not locale: raise DevelError('Invalid language code %r' % language.Code)

        language.Name = translator.languages.get(locale.language)
        if locale.territory: language.Territory = translator.territories.get(locale.territory)
        if locale.script: language.Script = translator.scripts.get(locale.script)
        if locale.variant: language.Variant = translator.variants.get(locale.variant)
        return language

    def _validateCode(self, prop, language, errors):
        '''
        Validates the language code on a language instance, this is based on the operator listeners.
        '''
        assert isinstance(language, Language), 'Invalid language %s' % language
        locale = self._localeOf(language.Code)
        if not locale:
            errors.append(Ref(_('Invalid language code'), ref=Language.Code))
            return False
        else: language.Code = str(locale)
