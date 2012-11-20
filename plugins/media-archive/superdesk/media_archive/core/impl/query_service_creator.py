'''
Created on Aug 21, 2012

@package: superdesk media archive
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor, Ioan v. Pocol

Creates the service that will be used for multi-plugins queries. 
'''

from ally.api.config import service, call, query
from ally.api.type import Iter, Scheme
from ally.support.api.util_service import namesForQuery
from ally.support.sqlalchemy.session import SessionSupport
from ally.support.sqlalchemy.util_service import buildQuery, buildLimits
from inspect import isclass
from superdesk.media_archive.api.meta_data import QMetaData, MetaData
from superdesk.media_archive.api.meta_info import QMetaInfo, MetaInfo
from superdesk.media_archive.core.spec import QueryIndexer
from superdesk.media_archive.meta.meta_data import MetaDataMapped
from superdesk.media_archive.meta.meta_info import MetaInfoMapped

# --------------------------------------------------------------------

def createService(queryIndexer):
    assert isinstance(queryIndexer, QueryIndexer), 'Invalid query indexer %s' % queryIndexer

    qMetaInfoClass = type('Compund$QMetaInfo', (QMetaInfo,), queryIndexer.infoCriterias)
    qMetaInfoClass = query(MetaInfo)(qMetaInfoClass)

    qMetaDataClass = type('Compund$QMetaData', (QMetaData,), queryIndexer.dataCriterias)
    qMetaDataClass = query(MetaData)(qMetaDataClass)

    types = (Iter(MetaInfo), Scheme, int, int, qMetaInfoClass, qMetaDataClass, str)
    apiClass = type('Generated$IQueryService', (IQueryService,), {})
    apiClass.getMetaInfos = call(*types, webName='Query')(apiClass.getMetaInfos)
    apiClass = service(apiClass)

    return type('Generated$QueryServiceAlchemy', (QueryServiceAlchemy, apiClass), {})(queryIndexer, qMetaInfoClass, qMetaDataClass)

# --------------------------------------------------------------------

class IQueryService:
    '''
    Provides the service methods for the unified multi-plugin criteria query.
    '''

    def getMetaInfos(self, scheme, offset=None, limit=10, qi=None, qd=None, thumbSize=None):
        '''
        Provides the meta data based on unified multi-plugin criteria.
        '''

# --------------------------------------------------------------------

class QueryServiceAlchemy(SessionSupport):
    '''
    Provides the service methods for the unified multi-plugin criteria query.
    '''

    def __init__(self, queryIndexer, QMetaInfoClass, QMetaDataClass):
        '''
        '''
        assert isinstance(queryIndexer, QueryIndexer), 'Invalid query indexer %s' % queryIndexer
        assert isclass(QMetaInfoClass), 'Invalid meta info class %s' % QMetaInfoClass
        assert isclass(QMetaDataClass), 'Invalid meta data class %s' % QMetaDataClass

        self.queryIndexer = queryIndexer
        self.QMetaInfo = QMetaInfoClass
        self.QMetaData = QMetaDataClass

    # --------------------------------------------------------------------

    def getMetaInfos(self, scheme, offset=None, limit=None, qi=None, qd=None, thumbSize=None):
        '''
        Provides the meta data based on unified multi-plugin criteria.
        '''
        sql = self.session().query(MetaInfoMapped)

        if qi is not None:
            assert isinstance(qi, self.QMetaInfo), 'Invalid query %s' % qi
            metaInfos = self.queryIndexer.metaInfos.copy()
            assert isinstance(metaInfos, set)

            for name in namesForQuery(qi):
                if getattr(self.QMetaInfo, name) not in qi: continue
                criteriaMetaInfos = self.queryIndexer.metaInfoByCriteria.get(name)
                assert criteriaMetaInfos, 'No model class available for %s' % name
                metaInfos.intersection(criteriaMetaInfos)

            sql = buildQuery(sql, qi, MetaInfoMapped)
            for metaInfo in metaInfos:
                sql = sql.join(metaInfo)
                try:
                    sql = buildQuery(sql, qi, metaInfo)
                except :
                    raise Exception('Cannot build query for meta info %s' % metaInfo)


        if qd is not None:
            assert isinstance(qd, self.QMetaData), 'Invalid query %s' % qd
            metaDatas = self.queryIndexer.metaDatas.copy()
            assert isinstance(metaDatas, set)

            for name in namesForQuery(qd):
                if getattr(self.QMetaData, name) not in qd: continue
                criteriaMetaDatas = self.queryIndexer.metaDataByCriteria.get(name)
                assert criteriaMetaDatas, 'No model class available for %s' % name
                metaDatas.intersection(criteriaMetaDatas)

            sql = sql.join(MetaDataMapped)
            sql = buildQuery(sql, qd, MetaDataMapped)
            for metaData in metaDatas:
                sql = sql.join(metaData)
                sql = buildQuery(sql, qd, metaData)


        sql = buildLimits(sql, offset, limit)

        return sql.all()

