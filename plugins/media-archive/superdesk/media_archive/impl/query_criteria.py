'''
Created on Aug 28, 2012

@package: superdesk media archive
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Ioan v. Pocol

The implementation for the query criteria API.
'''

from ..api.query_criteria import IQueryCriteriaService
from ally.container import wire
from ally.container.ioc import injected
from ally.container.support import setup
from ally.support.api.util_service import processQuery
from babel.core import Locale
from babel.localedata import locale_identifiers
from superdesk.media_archive.api.query_criteria import QueryCriteria
from superdesk.media_archive.core.spec import IQueryIndexer

# --------------------------------------------------------------------

@injected
@setup(IQueryCriteriaService, name='queryCriteriaService')
class QueryCriteriaService(IQueryCriteriaService):
    '''
    Implementation for @see: IQueryCriteriaService to get the list of multi-plugin query criteria.
    '''

    queryIndexer = IQueryIndexer;wire.entity('queryIndexer')

    def __init__(self):
        '''
        Construct the query criteria service.
        '''
        assert isinstance(self.queryIndexer, IQueryIndexer), 'Invalid IQueryIndexer %s' % self.queryIndexer
        self._locales = {code:Locale.parse(code) for code in locale_identifiers()}

    def getCriterias(self, locales, q=None):
        '''
        @see: QueryCriteriaService.getCriterias
        '''
        locales = self._localesOf(locales)

        queryCriterias = list()

        for key, metaInfos in self.queryIndexer.metaInfoByCriteria.items():
            types = ''.join([(self.queryIndexer.typesByMetaInfo[metaInfo.__name__] + '-') for metaInfo in metaInfos])
            criteria = self.queryIndexer.infoCriterias[key]
            queryCriterias.append(QueryCriteria('qi.' + key, criteria.__name__, types, key))

        for key, metaDatas in self.queryIndexer.metaDataByCriteria.items():
            types = ''.join([(self.queryIndexer.typesByMetaData[metaData.__name__] + '-') for metaData in metaDatas])
            criteria = self.queryIndexer.dataCriterias[key]
            queryCriterias.append(QueryCriteria('qd.' + key, criteria.__name__, types, key))

        if q:
            queryCriterias = processQuery(queryCriterias, QueryCriteria, q)

        return queryCriterias

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

    def _translate(self, key, default, locales):
        '''
        Helper method that provides the translated query name based on the babel locales list. The first
        locale will be used if not translation will be available.

        @param key: string
            The key to get the translated name for.
        @param locales: list[Locale]|tuple(Locale)
            The locales to translate the name for.
        @return: string
            The translated name.
        '''
        assert isinstance(key, str), 'Invalid key %s' % key
        assert isinstance(locales, (list, tuple)), 'Invalid locales %s' % locales
        for loc in locales:
            assert isinstance(loc, Locale), 'Invalid locale %s' % loc
            translated = loc.territories.get(key)
            if translated: return translated
        return default

