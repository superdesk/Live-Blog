'''
Created on Jun 23, 2011

@package superdesk
@copyright 2011 Sourcefabric o.p.s.
@license http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

SQL alchemy implementation for language API.
'''

from ..api.language import Language, ILanguageService
from ..meta.language import LanguageAvailable
from ally.api.error import IdError
from ally.container.ioc import injected
from ally.container.support import setup
from ally.support.api.util_service import processCollection
from babel.core import Locale
from babel.localedata import locale_identifiers
from collections import OrderedDict
from sql_alchemy.support.util_service import SessionSupport
from sqlalchemy.orm.exc import NoResultFound

# --------------------------------------------------------------------

@injected
@setup(ILanguageService, name='languageService')
class LanguageServiceBabelAlchemy(SessionSupport, ILanguageService):
    '''
    Implementation for @see: ILanguageService using Babel library.
    '''

    def __init__(self):
        '''Construct the language service.
        '''
        self._languages = None
        
    def getById(self, code):
        '''
        @see: ILanguageService.getById
        '''
        lang = self.languages().get(code)
        if lang is None: raise IdError()
        return lang
    
    def getAll(self, q=None, **options):
        '''
        @see: ILanguageService.getAll
        '''
        return processCollection(self.languages().keys(), Language, q, lambda code: self.languages()[code], **options)
    
    def getAllAvailable(self, q=None, **options):
        '''
        @see: ILanguageService.getAllAvailable
        '''
        codes = [code for code, in self.session().query(LanguageAvailable.code).all()]
        return processCollection(codes, Language, q, lambda code: self.languages()[code], **options)
    
    def add(self, code):
        '''
        @see: ILanguageService.add
        '''
        if not code in self.languages(): raise IdError(Language)
        if self.session().query(LanguageAvailable).filter(LanguageAvailable.code == code).count(): return
        lang = LanguageAvailable(code=code)
        self.session().add(lang)
        self.session().flush((lang,))
    
    def remove(self, code):
        '''
        @see: ILanguageService.remove
        '''
        try: lang = self.session().query(LanguageAvailable).filter(LanguageAvailable.code == code).one()
        except NoResultFound: return False
        self.session().delete(lang)
        return True

    # ----------------------------------------------------------------
    
    def languages(self):
        '''
        Provides all the languages available.
        
        @return: dictionary{string: Language}
            The languages indexed by code.
        '''
        translator = Locale.parse('en')
        if self._languages is None:
            self._languages = OrderedDict()
            for code in sorted(locale_identifiers()):
                locale = Locale.parse(code)
                lang = Language(code, translator.languages.get(code))
                lang.Territory = locale.territory
                lang.Script = locale.script
                lang.Variant = locale.variant
                
                self._languages[lang.Code] = lang
                
        return self._languages
