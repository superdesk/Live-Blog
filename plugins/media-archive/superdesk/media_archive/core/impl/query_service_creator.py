'''
Created on Aug 21, 2012

@package: superdesk media archive
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor, Ioan v. Pocol

Creates the service that will be used for multi-plugins queries.
'''

from ally.api.config import service, call, query
from ally.api.type import Iter, Scheme, Reference, typeFor
from ally.support.api.util_service import namesForQuery
from ally.support.sqlalchemy.session import SessionSupport
from ally.support.sqlalchemy.util_service import buildLimits, buildQuery
from inspect import isclass
from superdesk.media_archive.api.meta_data import QMetaData, MetaData
from superdesk.media_archive.api.meta_info import QMetaInfo, MetaInfo
from superdesk.media_archive.core.spec import IQueryIndexer, IThumbnailManager
from superdesk.media_archive.meta.meta_data import MetaDataMapped
from superdesk.media_archive.meta.meta_info import MetaInfoMapped
from ally.api.extension import IterPart
from superdesk.user.api.user import User
from superdesk.language.api.language import LanguageEntity
from datetime import datetime
from cdm.spec import ICDM
from superdesk.media_archive.api.domain_archive import modelArchive
from sqlalchemy.sql.expression import or_, and_, not_
from ally.support.sqlalchemy.mapper import mappingFor
from sqlalchemy.orm.mapper import Mapper
from sqlalchemy.orm.properties import ColumnProperty
from superdesk.media_archive.api.criteria import AsIn, \
    AsLikeExpressionOrdered, AsLikeExpression
from superdesk.media_archive.meta.meta_type import MetaTypeMapped


# --------------------------------------------------------------------

@modelArchive(id='Id')
class MetaDataInfo:
    '''
    (MetaDataBase, MetaInfoBase)
    Provides the meta data information that is provided by the user.
    '''
    Id = int

    #TODO: change to inherit from Base

    Name = str
    Type = str
    Content = Reference
    Thumbnail = Reference
    SizeInBytes = int
    Creator = User
    CreatedOn = datetime

    Language = LanguageEntity
    Title = str
    Keywords = str
    Description = str

# --------------------------------------------------------------------

@query(MetaDataInfo)
class QMetaDataInfo:
    '''
    The query for the meta data info models for all texts search.
    '''
    all = AsLikeExpressionOrdered
    type = AsIn

# --------------------------------------------------------------------

def createService(queryIndexer, cdmArchive, thumbnailManager):
    assert isinstance(queryIndexer, IQueryIndexer), 'Invalid query indexer %s' % queryIndexer
    assert isinstance(cdmArchive, ICDM), 'Invalid archive CDM %s' % cdmArchive
    assert isinstance(thumbnailManager, IThumbnailManager), 'Invalid thumbnail manager %s' % thumbnailManager

    qMetaInfoClass = type('Compund$QMetaInfo', (QMetaInfo,), queryIndexer.infoCriterias)
    qMetaInfoClass = query(MetaInfo)(qMetaInfoClass)

    qMetaDataClass = type('Compund$QMetaData', (QMetaData,), queryIndexer.dataCriterias)
    qMetaDataClass = query(MetaData)(qMetaDataClass)

    types = (Iter(MetaDataInfo), Scheme, int, int, QMetaDataInfo, qMetaInfoClass, qMetaDataClass, str)
    apiClass = type('Generated$IQueryService', (IQueryService,), {})
    apiClass.getMetaInfos = call(*types, webName='Query')(apiClass.getMetaInfos)
    apiClass = service(apiClass)

    return type('Generated$QueryServiceAlchemy', (QueryServiceAlchemy, apiClass), {}
                 )(queryIndexer, cdmArchive, thumbnailManager, qMetaInfoClass, qMetaDataClass)

# --------------------------------------------------------------------

class IQueryService:
    '''
    Provides the service methods for the unified multi-plugin criteria query.
    '''

    def getMetaInfos(self, scheme, offset=None, limit=10, qa=None, qi=None, qd=None, thumbSize=None):
        '''
        Provides the meta data based on unified multi-plugin criteria.
        '''

# --------------------------------------------------------------------

class QueryServiceAlchemy(SessionSupport):
    '''
    Provides the service methods for the unified multi-plugin criteria query.
    '''

    cdmArchive = ICDM
    # The archive CDM.
    thumbnailManager = IThumbnailManager
    # Provides the thumbnail referencer
    queryIndexer = IQueryIndexer
    # Provides the query indexer reference

    def __init__(self, queryIndexer, cdmArchive, thumbnailManager, QMetaInfoClass, QMetaDataClass):
        '''
        '''

        assert isinstance(cdmArchive, ICDM), 'Invalid archive CDM %s' % cdmArchive
        assert isinstance(thumbnailManager, IThumbnailManager), 'Invalid thumbnail manager %s' % thumbnailManager

        assert isinstance(queryIndexer, IQueryIndexer), 'Invalid query indexer %s' % queryIndexer
        assert isclass(QMetaInfoClass), 'Invalid meta info class %s' % QMetaInfoClass
        assert isclass(QMetaDataClass), 'Invalid meta data class %s' % QMetaDataClass

        self.cdmArchive = cdmArchive
        self.thumbnailManager = thumbnailManager
        self.queryIndexer = queryIndexer
        self.QMetaInfo = QMetaInfoClass
        self.QMetaData = QMetaDataClass

    # --------------------------------------------------------------------

    def getMetaInfos(self, scheme, offset=None, limit=1000, qa=None, qi=None, qd=None, thumbSize=None):
        '''
        Provides the meta data based on unified multi-plugin criteria.
        '''

        metaInfos = set()
        metaDatas = set()

        sqlUnion = None
        sqlList = list()

        types = [self.queryIndexer.typesByMetaData[key] for key in self.queryIndexer.typesByMetaData.keys()]

        if qa is not None:
            assert isinstance(qa, QMetaDataInfo), 'Invalid query %s' % qa

            if QMetaDataInfo.type in qa:
                types = qa.type.values


            for name, criteria in self.queryIndexer.infoCriterias.items():
                if criteria is AsLikeExpression or criteria is AsLikeExpressionOrdered:
                    criteriaMetaInfos = self.queryIndexer.metaInfoByCriteria.get(name)
                    #if MetaInfo is present, add only MetaInfo
                    if MetaInfoMapped not in criteriaMetaInfos:
                        for metaInfo in criteriaMetaInfos:
                            if self.queryIndexer.typesByMetaInfo[metaInfo.__name__] in types: metaInfos.add(metaInfo)
                    elif self.queryIndexer.typesByMetaInfo[getattr(MetaInfoMapped, '__name__')] in types:
                        metaInfos.add(MetaInfoMapped)

            for name, criteria in self.queryIndexer.dataCriterias.items():
                if criteria is AsLikeExpression or criteria is AsLikeExpressionOrdered:
                    criteriaMetaDatas = self.queryIndexer.metaDataByCriteria.get(name)
                    #if MetaData is present, add only MetaData
                    if MetaDataMapped not in criteriaMetaDatas:
                        for metaData in criteriaMetaDatas:
                            if self.queryIndexer.typesByMetaData[metaData.__name__] in types: metaDatas.add(metaData)
                    elif self.queryIndexer.typesByMetaData[getattr(MetaDataMapped, '__name__')] in types:
                        metaDatas.add(MetaDataMapped)


        if qi is not None:
            assert isinstance(qi, self.QMetaInfo), 'Invalid query %s' % qi

            for name in namesForQuery(qi):
                if getattr(self.QMetaInfo, name) not in qi: continue
                criteriaMetaInfos = self.queryIndexer.metaInfoByCriteria.get(name)
                assert criteriaMetaInfos, 'No model class available for %s' % name
                #if MetaInfo is present, add only MetaInfo
                if MetaInfoMapped not in criteriaMetaInfos:
                    for metaInfo in criteriaMetaInfos:
                        if self.queryIndexer.typesByMetaInfo[metaInfo.__name__] in types: metaInfos.add(metaInfo)
                elif self.queryIndexer.typesByMetaInfo[getattr(MetaInfoMapped, '__name__')] in types:
                    metaInfos.add(MetaInfoMapped)

        if qd is not None:
            assert isinstance(qd, self.QMetaData), 'Invalid query %s' % qd

            for name in namesForQuery(qd):
                if getattr(self.QMetaData, name) not in qd: continue
                criteriaMetaDatas = self.queryIndexer.metaDataByCriteria.get(name)
                assert criteriaMetaDatas, 'No model class available for %s' % name
                #if MetaData is present, add only MetaData
                if MetaDataMapped not in criteriaMetaDatas:
                    for metaData in criteriaMetaDatas:
                        if self.queryIndexer.typesByMetaData[metaData.__name__] in types: metaDatas.add(metaData)
                elif self.queryIndexer.typesByMetaData[getattr(MetaDataMapped, '__name__')] in types:
                    metaDatas.add(MetaDataMapped)

        for metaData in self.queryIndexer.metaDatas:
            if metaData not in metaDatas and self.queryIndexer.typesByMetaData[metaData.__name__] not in types:
                types.append(self.queryIndexer.typesByMetaData[metaData.__name__])

        for metaInfo in self.queryIndexer.metaInfos:
            if metaInfo not in metaInfos and self.queryIndexer.typesByMetaInfo[metaInfo.__name__] not in types:
                types.append(self.queryIndexer.typesByMetaInfo[metaInfo.__name__])

        if not metaInfos and not metaDatas:
            pass;
        elif metaInfos and not metaDatas:
            for metaInfo in metaInfos:
                sql = buildSubquery(self, metaInfo, MetaDataMapped, qa, qi, qd, types)
                if sql: sqlList.append(sql)
        elif not metaInfos and metaDatas:
            for metaData in metaDatas:
                sql = buildSubquery(self, MetaInfoMapped, metaData, qa, qi, qd, types)
                if sql: sqlList.append(sql)
        else:
            for metaInfo in metaInfos:
                metaData = self.queryIndexer.metaDatasByInfo[metaInfo.__name__]
                if metaData in metaDatas:
                    sql = buildSubquery(self, metaInfo, metaData, qa, qi, qd, types)
                    if sql: sqlList.append(sql)
                else:
                    sql = buildSubquery(self, metaInfo, MetaDataMapped, qa, qi, qd, types)
                    if sql: sqlList.append(sql)
            for metaData in metaDatas:
                if metaData is MetaDataMapped: continue
                if self.queryIndexer.metaInfosByData[metaData.__name__] not in metaInfos:
                    sql = buildSubquery(self, MetaInfoMapped, metaData, qa, qi, qd, types)
                    if sql: sqlList.append(sql)

        sqlLength = len(sqlList)
        if sqlLength == 0:
            sqlUnion = buildSubquery(self, MetaInfoMapped, MetaDataMapped, qa, qi, qd, types)
        elif sqlLength == 1:
            sqlUnion = sqlList[0]
        else:
            sqlUnion = sqlList.pop()
            sqlUnion = sqlUnion.union(*sqlList)

        count = sqlUnion.count()
        sqlUnion = buildLimits(sqlUnion, offset, limit)

        metaDataInfos = list()
        for row in sqlUnion.all():
            metaDataInfo = MetaDataInfo()

            metaDataMapped = row[0]
            metaInfoMapped = row[1]

            assert isinstance(metaDataMapped, MetaDataMapped), 'Invalid meta data %s' % metaDataMapped
            metaDataMapped.Content = self.cdmArchive.getURI(metaDataMapped.content, scheme)
            self.thumbnailManager.populate(metaDataMapped, scheme, thumbSize)

            #TODO: change to use copy from ally-api, util_service.py
            #the current problem is that on the object returned by sqlalchemy the properties are not visible in copy
            metaDataInfo.Id = metaDataMapped.Id
            metaDataInfo.Name = metaDataMapped.Name
            metaDataInfo.Type = metaDataMapped.Type
            metaDataInfo.Content = metaDataMapped.Content
            metaDataInfo.Thumbnail = metaDataMapped.Thumbnail
            metaDataInfo.SizeInBytes = metaDataMapped.SizeInBytes
            metaDataInfo.Creator = metaDataMapped.Creator
            metaDataInfo.CreatedOn = metaDataMapped.CreatedOn

            if metaInfoMapped:
                metaDataInfo.Language = metaInfoMapped.Language
                metaDataInfo.Title = metaInfoMapped.Title
                metaDataInfo.Keywords = metaInfoMapped.Keywords
                metaDataInfo.Description = metaInfoMapped.Description

            metaDataInfos.append(metaDataInfo)

        return IterPart(metaDataInfos, count, offset, limit)


def buildSubquery(self, metaInfo, metaData, qa, qi, qd, types):
    sql = self.session().query(MetaDataMapped)

    if metaInfo == MetaInfoMapped and metaData == MetaDataMapped:
        if types:
            sql = sql.join(MetaTypeMapped, MetaTypeMapped.Id == MetaDataMapped.typeId)
            sql = sql.filter(MetaTypeMapped.Type.in_(types))
    elif metaInfo != MetaInfoMapped:
        sql = sql.join(MetaTypeMapped, and_(MetaTypeMapped.Id == MetaDataMapped.typeId, MetaTypeMapped.Type == self.queryIndexer.typesByMetaInfo[metaInfo.__name__]))
    elif metaData != MetaDataMapped:
        sql = sql.join(MetaTypeMapped, and_(MetaTypeMapped.Id == MetaDataMapped.typeId, MetaTypeMapped.Type == self.queryIndexer.typesByMetaData[metaData.__name__]))

    sql = sql.outerjoin(MetaInfoMapped, MetaDataMapped.Id == MetaInfoMapped.MetaData)
    sql = sql.add_entity(MetaInfoMapped)


    if qi: sql = buildQuery(sql, qi, metaInfo)
    if qd: sql = buildQuery(sql, qd, metaData)

    if qi and metaInfo != MetaInfoMapped:
        sql = buildQuery(sql, qi, MetaInfoMapped)
    if qd and metaData != MetaDataMapped:
        sql = buildQuery(sql, qd, MetaDataMapped)

    if qi: sql = buildExpressionQuery(sql, qi, metaInfo, qa)
    if qd: sql = buildExpressionQuery(sql, qd, metaData, qa)

    if qi and metaInfo != MetaInfoMapped:
        sql = buildExpressionQuery(sql, qi, MetaInfoMapped, qa)
    if qd and metaData != MetaDataMapped:
        sql = buildExpressionQuery(sql, qd, MetaDataMapped, qa)

    if qa and qa.all:
        assert isinstance(qa, QMetaDataInfo), 'Invalid query %s' % qa
        sql = buildAllQuery(sql, qa.all, self.queryIndexer.queryByInfo[metaInfo.__name__], metaInfo,
                            self.queryIndexer.queryByData[metaData.__name__], metaData)


    return sql

def buildExpressionQuery(sql, query, mapped, qa):
    '''
    Builds the query on the SQL alchemy query.

    @param sqlQuery: SQL alchemy
        The sql alchemy query to use.
    @param query: query
        The REST query object to provide filtering on.
    @param mapped: class
        The mapped model class to use the query on.
    '''

    assert query is not None, 'A query object is required'
    clazz = query.__class__
    mapper = mappingFor(mapped)
    assert isinstance(mapper, Mapper)

    all = None
    if qa: all = qa.all

    columns = {cp.key.lower(): getattr(mapper.c, cp.key)
                  for cp in mapper.iterate_properties if isinstance(cp, ColumnProperty)}
    columns = {criteria:columns.get(criteria.lower()) for criteria in namesForQuery(clazz)}

    for criteria, column in columns.items():
        if column is None or getattr(clazz, criteria) not in query: continue
        crt = getattr(query, criteria)

        if isinstance(crt, AsLikeExpression) or isinstance(crt, AsLikeExpressionOrdered):
            #include
            if AsLikeExpression.inc in crt:
                for value in crt.inc:
                    sql = sql.filter(column.like(processLike(value)))

            if all and AsLikeExpression.inc in all:
                for value in all.inc:
                    sql = sql.filter(column.like(processLike(value)))

            #extend
            clauses = list()
            if AsLikeExpression.ext in crt:
                for value in crt.ext:
                    clauses.append(column.like(processLike(value)))

            if all and AsLikeExpression.ext in all:
                for value in all.ext:
                    clauses.append(column.like(processLike(value)))

            length = len(clauses)
            if length == 1: sql = sql.filter(clauses[0])
            elif length > 1: sql = sql.filter(or_(*clauses))

            #exclude
            if AsLikeExpression.exc in crt:
                for value in crt.exc:
                    sql = sql.filter(not_(column.like(processLike(value))))

            if all and AsLikeExpression.exc in all:
                for value in all.exc:
                    sql = sql.filter(not_(column.like(processLike(value))))

    return sql


def buildAllQuery(sql, all, qMetaInfo, metaInfo, qMetaData, metaData):
    '''
    Builds the query for all criteria.

    @param sql: SQL alchemy
        The sql alchemy query to use.
    @param qMetaInfo: query
        The REST query object to provide filtering on for meta info.
    @param metaInfo: class
        The meta info mapped model class to use the query on.
    @param qMetaData: query
        The REST query object to provide filtering on for meta data
    @param metaData: class
        The meta data mapped model class to use the query on.
    '''

    infoMapper = mappingFor(metaInfo)
    assert isinstance(infoMapper, Mapper)

    dataMapper = mappingFor(metaData)
    assert isinstance(dataMapper, Mapper)

    baseInfoMapper = mappingFor(MetaInfoMapped)
    assert isinstance(infoMapper, Mapper)

    baseDataMapper = mappingFor(MetaDataMapped)
    assert isinstance(dataMapper, Mapper)

    infoProperties = {cp.key.lower(): getattr(infoMapper.c, cp.key)
                  for cp in infoMapper.iterate_properties if isinstance(cp, ColumnProperty)}

    dataProperties = {cp.key.lower(): getattr(dataMapper.c, cp.key)
                  for cp in dataMapper.iterate_properties if isinstance(cp, ColumnProperty)}

    baseInfoProperties = {cp.key.lower(): getattr(baseInfoMapper.c, cp.key)
                  for cp in baseInfoMapper.iterate_properties if isinstance(cp, ColumnProperty)}

    baseDataProperties = {cp.key.lower(): getattr(baseDataMapper.c, cp.key)
                  for cp in baseDataMapper.iterate_properties if isinstance(cp, ColumnProperty)}

    infoQueryType = typeFor(qMetaInfo)
    dataQueryType = typeFor(qMetaData)

    baseInfoQueryType = typeFor(QMetaInfo)
    baseDataQueryType = typeFor(QMetaData)

    if all.inc:
        for value in all.inc:
            clauses = list()

            for criteria, crtClass in infoQueryType.query.criterias.items():
                column = infoProperties.get(criteria.lower())
                if column is None: continue
                if crtClass == AsLikeExpression or crtClass == AsLikeExpressionOrdered:
                    clauses.append(column.like(processLike(value)))

            for criteria, crtClass in dataQueryType.query.criterias.items():
                column = dataProperties.get(criteria.lower())
                if column is None: continue
                if crtClass == AsLikeExpression or crtClass == AsLikeExpressionOrdered:
                    clauses.append(column.like(processLike(value)))

            if metaInfo != MetaInfoMapped:
                for criteria, crtClass in baseInfoQueryType.query.criterias.items():
                    column = baseInfoProperties.get(criteria.lower())
                    if column is None: continue
                    if crtClass == AsLikeExpression or crtClass == AsLikeExpressionOrdered:
                        clauses.append(column.like(processLike(value)))

            if metaData != MetaDataMapped:
                for criteria, crtClass in baseDataQueryType.query.criterias.items():
                    column = baseDataProperties.get(criteria.lower())
                    if column is None: continue
                    if crtClass == AsLikeExpression or crtClass == AsLikeExpressionOrdered:
                        clauses.append(column.like(processLike(value)))

            length = len(clauses)
            if length == 1: sql = sql.filter(clauses[0])
            elif length > 1: sql = sql.filter(or_(*clauses))

    if all.ext:
        clauses = list()
        for value in all.ext:
            for criteria, crtClass in infoQueryType.query.criterias.items():
                column = infoProperties.get(criteria.lower())
                if column is None: continue
                if crtClass == AsLikeExpression or crtClass == AsLikeExpressionOrdered:
                    clauses.append(column.like(processLike(value)))

            for criteria, crtClass in dataQueryType.query.criterias.items():
                column = dataProperties.get(criteria.lower())
                if column is None: continue
                if crtClass == AsLikeExpression or crtClass == AsLikeExpressionOrdered:
                    clauses.append(column.like(processLike(value)))

            if metaInfo != MetaInfoMapped:
                for criteria, crtClass in baseInfoQueryType.query.criterias.items():
                    column = baseInfoProperties.get(criteria.lower())
                    if column is None: continue
                    if crtClass == AsLikeExpression or crtClass == AsLikeExpressionOrdered:
                        clauses.append(column.like(processLike(value)))

            if metaData != MetaDataMapped:
                for criteria, crtClass in baseDataQueryType.query.criterias.items():
                    column = baseDataProperties.get(criteria.lower())
                    if column is None: continue
                    if crtClass == AsLikeExpression or crtClass == AsLikeExpressionOrdered:
                        clauses.append(column.like(processLike(value)))

        length = len(clauses)
        if length == 1: sql = sql.filter(clauses[0])
        elif length > 1: sql = sql.filter(or_(*clauses))

    if all.exc:
        clauses = list()
        for value in all.exc:
            for criteria, crtClass in infoQueryType.query.criterias.items():
                column = infoProperties.get(criteria.lower())
                if column is None: continue
                if crtClass == AsLikeExpression or crtClass == AsLikeExpressionOrdered:
                    clauses.append(not_(column.like(processLike(value))))

            for criteria, crtClass in dataQueryType.query.criterias.items():
                column = dataProperties.get(criteria.lower())
                if column is None: continue
                if crtClass == AsLikeExpression or crtClass == AsLikeExpressionOrdered:
                    clauses.append(not_(column.like(processLike(value))))

            if metaInfo != MetaInfoMapped:
                for criteria, crtClass in baseInfoQueryType.query.criterias.items():
                    column = baseInfoProperties.get(criteria.lower())
                    if column is None: continue
                    if crtClass == AsLikeExpression or crtClass == AsLikeExpressionOrdered:
                        clauses.append(not_(column.like(processLike(value))))

            if metaData != MetaDataMapped:
                for criteria, crtClass in baseDataQueryType.query.criterias.items():
                    column = baseDataProperties.get(criteria.lower())
                    if column is None: continue
                    if crtClass == AsLikeExpression or crtClass == AsLikeExpressionOrdered:
                        clauses.append(not_(column.like(processLike(value))))

        length = len(clauses)
        if length == 1: sql = sql.filter(clauses[0])
        elif length > 1: sql = sql.filter(and_(*clauses))

    return sql

def processLike(value):
    assert isinstance(value, str), 'Invalid like value %s' % value

    if not value:
        return '%'

    if not value.endswith('%'):
        value = value + '%'

    if not value.startswith('%'):
        value = '%' + value

    return value
