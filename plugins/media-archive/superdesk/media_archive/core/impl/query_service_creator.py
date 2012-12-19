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
from ally.support.sqlalchemy.util_service import buildLimits
from inspect import isclass
from itertools import chain
from superdesk.media_archive.api.meta_data import QMetaData, MetaData
from superdesk.media_archive.api.meta_info import QMetaInfo, MetaInfo
from superdesk.media_archive.core.spec import QueryIndexer, IThumbnailManager
from superdesk.media_archive.meta.meta_data import MetaDataMapped
from superdesk.media_archive.meta.meta_info import MetaInfoMapped
from ally.api.extension import IterPart
from superdesk.user.api.user import User
from superdesk.language.api.language import LanguageEntity
from datetime import datetime
from cdm.spec import ICDM
from superdesk.media_archive.api.domain_archive import modelArchive
from sqlalchemy.sql.expression import or_, and_, not_
from ally.api.criteria import AsBoolean, AsLike, AsEqual, AsDate, AsDateTime, \
    AsRange, AsTime, AsOrdered
from ally.support.sqlalchemy.mapper import mappingFor
from sqlalchemy.orm.mapper import Mapper
from sqlalchemy.orm.properties import ColumnProperty
from superdesk.media_archive.api.criteria import AsIn, \
    AsLikeExpressionOrdered, AsLikeExpression, AsInOrdered
from ally.api.operator.type import TypeQuery
from ally.api.operator.container import Query


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

# --------------------------------------------------------------------

def createService(queryIndexer, cdmArchive, thumbnailManager):
    assert isinstance(queryIndexer, QueryIndexer), 'Invalid query indexer %s' % queryIndexer
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

    def getMetaInfos(self, scheme, offset=None, limit=10, all=None, qi=None, qd=None, thumbSize=None):
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

    def __init__(self, queryIndexer, cdmArchive, thumbnailManager, QMetaInfoClass, QMetaDataClass):
        '''
        '''

        assert isinstance(cdmArchive, ICDM), 'Invalid archive CDM %s' % cdmArchive
        assert isinstance(thumbnailManager, IThumbnailManager), 'Invalid thumbnail manager %s' % thumbnailManager

        assert isinstance(queryIndexer, QueryIndexer), 'Invalid query indexer %s' % queryIndexer
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

        if qa is not None:
            assert isinstance(qa, QMetaDataInfo), 'Invalid query %s' % qa

            for name, criteria in self.queryIndexer.infoCriterias.items():
                if criteria is AsLikeExpression or criteria is AsLikeExpressionOrdered:
                    criteriaMetaInfos = self.queryIndexer.metaInfoByCriteria.get(name)
                    #if MetaInfo is present, add only MetaInfo
                    if MetaInfoMapped not in criteriaMetaInfos:
                        metaInfos = set.union(metaInfos, criteriaMetaInfos)
                    else: metaInfos.add(MetaInfoMapped)

            for name, criteria in self.queryIndexer.dataCriterias.items():
                if criteria is AsLikeExpression or criteria is AsLikeExpressionOrdered:
                    criteriaMetaDatas = self.queryIndexer.metaDataByCriteria.get(name)
                    #if MetaData is present, add only MetaData
                    if MetaDataMapped not in criteriaMetaDatas:
                        metaDatas = set.union(metaDatas, criteriaMetaDatas)
                    else: metaDatas.add(MetaDataMapped)


        if qi is not None:
            assert isinstance(qi, self.QMetaInfo), 'Invalid query %s' % qi

            for name in namesForQuery(qi):
                if getattr(self.QMetaInfo, name) not in qi: continue
                criteriaMetaInfos = self.queryIndexer.metaInfoByCriteria.get(name)
                assert criteriaMetaInfos, 'No model class available for %s' % name
                #if MetaInfo is present, add only MetaInfo
                if MetaInfoMapped not in criteriaMetaInfos:
                    metaInfos = set.union(metaInfos, criteriaMetaInfos)
                else: metaInfos.add(MetaInfoMapped)

        if qd is not None:
            assert isinstance(qd, self.QMetaData), 'Invalid query %s' % qd

            for name in namesForQuery(qd):
                if getattr(self.QMetaData, name) not in qd: continue
                criteriaMetaDatas = self.queryIndexer.metaDataByCriteria.get(name)
                assert criteriaMetaDatas, 'No model class available for %s' % name
                #if MetaData is present, add only MetaData
                if MetaDataMapped not in criteriaMetaDatas:
                    metaDatas = set.union(metaDatas, criteriaMetaDatas)
                else: metaDatas.add(MetaDataMapped)


        if not metaInfos and not metaDatas:
            pass;
        elif metaInfos and not metaDatas:
            for metaInfo in metaInfos:
                sql = buildSubquery(self, metaInfo, None, qa, qi, qd)

                if sqlUnion: sqlUnion = sqlUnion.union(sql)
                else: sqlUnion = sql

        elif not metaInfos and metaDatas:
            for metaData in metaDatas:
                sql = buildSubquery(self, None, MetaData, qa, qi, qd)

                if sqlUnion: sqlUnion = sqlUnion.union(sql)
                else: sqlUnion = sql

        else:
            for metaInfo in metaInfos:
                metaData = self.queryIndexer.metaDatasByInfo[metaInfo.__name__]
                if metaData in metaDatas:
                    sql = buildSubquery(self, metaInfo, metaData, qa, qi, qd)

                    if sqlUnion: sqlUnion = sqlUnion.union(sql)
                    else: sqlUnion = sql
                else:
                    sql = buildSubquery(self, metaInfo, None, qa, qi, qd)

                    if sqlUnion: sqlUnion = sqlUnion.union(sql)
                    else: sqlUnion = sql

            for metaData in metaDatas:
                if metaData is MetaDataMapped: continue
                if self.queryIndexer.metaInfosByData[metaData.__name__] not in metaInfos:
                    sql = buildSubquery(self, None, MetaData, qa, qi, qd)

                    if sqlUnion: sqlUnion = sqlUnion.union(sql)
                    else: sqlUnion = sql

        if sqlUnion is None:
            sqlUnion = buildSubquery(self, MetaInfoMapped, MetaDataMapped, qa, qi, qd)
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


def buildPartialQuery(sqlQuery, query, queryLike, mapped, pQuery, andClauses=None, orClauses=None, append=True):
    '''
    Builds the query on the SQL alchemy query.

    @param sqlQuery: SQL alchemy
        The sql alchemy query to use.
    @param query: query
        The REST query object to provide filtering on.
    @param mapped: class
        The mapped model class to use the query on.
    '''

    if queryLike:
        assert isinstance(queryLike, QMetaDataInfo), 'Invalid query %s' % queryLike

    ordered, unordered = [], []
    mapper = mappingFor(mapped)
    assert isinstance(mapper, Mapper)

    properties = {cp.key.lower(): getattr(mapper.c, cp.key)
                  for cp in mapper.iterate_properties if isinstance(cp, ColumnProperty)}

    if andClauses is None: andClauses = list()
    if orClauses is None: orClauses = list()

    if pQuery:
        queryType = typeFor(pQuery)
        assert isinstance(queryType, TypeQuery)
        assert isinstance(queryType.query, Query)

    if query:
        clazz = query.__class__
        for criteria in namesForQuery(clazz):
            column = properties.get(criteria.lower())

            if column is None: continue

            if getattr(clazz, criteria) in query:
                crt = getattr(query, criteria)

                if isinstance(crt, AsBoolean):
                    if AsBoolean.value in crt: andClauses.append(column == crt.value)
                elif isinstance(crt, AsLike):
                    if AsLike.like in crt: andClauses.append(column.like(crt.like))
                    elif AsLike.ilike in crt: andClauses.append(column.ilike(crt.ilike))
                elif isinstance(crt, AsLikeExpression) or isinstance(crt, AsLikeExpressionOrdered):
                        if AsLikeExpression.inc in crt:
                            for value in crt.inc:
                                andClauses.append(column.like(value))
                        if AsLikeExpression.ext in crt:
                            for value in crt.ext:
                                orClauses.append(column.like(value))
                        if AsLikeExpression.exc in crt:
                            for value in crt.exc:
                                andClauses.append(not_(column.like(value)))

                        if queryLike:
                            if AsLikeExpression.inc in queryLike:
                                for value in queryLike.inc:
                                    andClauses.append(column.like(value))
                            if AsLikeExpression.ext in queryLike:
                                for value in queryLike.ext:
                                    orClauses.append(column.like(value))
                            if AsLikeExpression.exc in queryLike:
                                for value in queryLike.exc:
                                    andClauses.append(not_(column.like(value)))

                elif isinstance(crt, AsIn) or isinstance(crt, AsInOrdered):
                    andClauses.append(column.in_(crt.values))
                elif isinstance(crt, AsEqual):
                    if AsEqual.equal in crt: andClauses.append(column.ilike(column == crt.equal))
                elif isinstance(crt, (AsDate, AsTime, AsDateTime, AsRange)):
                    if crt.__class__.start in crt: andClauses.append(column.ilike(column >= crt.start))
                    elif crt.__class__.until in crt: andClauses.append(column.ilike(column < crt.until))
                    if crt.__class__.end in crt:andClauses.append(column.ilike(column <= crt.end))
                    elif crt.__class__.since in crt: andClauses.append(column.ilike(column > crt.since))

                if isinstance(crt, AsOrdered):
                    assert isinstance(crt, AsOrdered)
                    if AsOrdered.ascending in crt:
                        if AsOrdered.priority in crt and crt.priority:
                            ordered.append((column, crt.ascending, crt.priority))
                        else:
                            unordered.append((column, crt.ascending, None))

                ordered.sort(key=lambda pack: pack[2])
                for column, asc, __ in chain(ordered, unordered):
                    if asc: sqlQuery = sqlQuery.order_by(column)
                    else: sqlQuery = sqlQuery.order_by(column.desc())

            elif queryLike and queryType and criteria in queryType.query.criterias:
                crtClass = queryType.query.criterias[criteria]

                if crtClass == AsLikeExpression or crtClass == AsLikeExpressionOrdered:
                    if AsLikeExpression.inc in queryLike.all or AsLikeExpressionOrdered.inc in queryLike.all:
                        for value in queryLike.all.inc:
                            andClauses.append(column.like(value))
                    if AsLikeExpression.ext in queryLike.all or AsLikeExpressionOrdered.ext in queryLike.all:
                        for value in queryLike.all.ext:
                            orClauses.append(column.like(value))
                    if AsLikeExpression.exc in queryLike.all or AsLikeExpressionOrdered.exc in queryLike.all:
                        for value in queryLike.all.exc:
                            andClauses.append(not_(column.like(value)))

    elif queryLike and queryType:

        for criteria, crtClass in queryType.query.criterias.items():
            column = properties.get(criteria.lower())

            if column is None: continue

            if crtClass == AsLikeExpression or crtClass == AsLikeExpressionOrdered:
                if AsLikeExpression.inc in queryLike.all or AsLikeExpressionOrdered.inc in queryLike.all:
                    for value in queryLike.all.inc:
                        andClauses.append(column.like(value))
                if AsLikeExpression.ext in queryLike.all or AsLikeExpressionOrdered.ext in queryLike.all:
                    for value in queryLike.all.ext:
                        orClauses.append(column.like(value))
                if AsLikeExpression.exc in queryLike.all or AsLikeExpressionOrdered.exc in queryLike.all:
                    for value in queryLike.all.exc:
                        andClauses.append(not_(column.like(value)))


    if not append:
        return sqlQuery

    lengthAnd = len(andClauses)
    lengthOr = len(orClauses)

    if lengthAnd == 0:
        if lengthOr == 0:
            #do nothing 
            pass
        elif lengthOr == 1:
            sqlQuery = sqlQuery.filter(orClauses[0])
        elif lengthOr > 1:
            sqlQuery = sqlQuery.filter(or_(*orClauses))
    elif lengthAnd == 1:
        if lengthOr == 0:
            sqlQuery = sqlQuery.filter(andClauses[0])
        elif lengthOr == 1:
            sqlQuery = sqlQuery.filter(andClauses[0]).filter(orClauses[0])
        elif lengthOr > 1:
            sqlQuery = sqlQuery.filter(andClauses[0]).filter(or_(*orClauses))
    elif lengthAnd > 1:
        if lengthOr == 0:
            sqlQuery = sqlQuery.filter(and_(*andClauses))
        elif lengthOr == 1:
            sqlQuery = sqlQuery.filter(and_(*andClauses)).filter(orClauses[0])
        elif lengthOr > 1:
            sqlQuery = sqlQuery.filter(and_(*andClauses)).filter(or_(*orClauses))

    return sqlQuery



def buildSubquery(self, metaInfo, metaData, qa, qi, qd):
    if metaData is None:
        sql = self.session().query(MetaDataMapped)
        sql = sql.outerjoin(MetaInfoMapped, MetaDataMapped.Id == MetaInfoMapped.MetaData)
        sql = sql.add_entity(MetaInfoMapped)

        if metaInfo is MetaInfoMapped:
            sql = buildPartialQuery(sql, qi, qa, MetaInfoMapped, QMetaInfo)
        else:
            andClauses = list()
            orClauses = list()
            sql = sql.outerjoin(metaInfo)
            sql = buildPartialQuery(sql, qi, qa, MetaInfoMapped, QMetaInfo, andClauses, orClauses, append=False)
            sql = buildPartialQuery(sql, qi, qa, metaInfo, self.queryIndexer.queryByInfo[metaInfo.__name__], andClauses, orClauses)

    elif metaInfo is None:
        sql = self.session().query(MetaDataMapped)
        sql = sql.outerjoin(MetaInfoMapped, MetaDataMapped.Id == MetaInfoMapped.MetaData)
        sql = sql.add_entity(MetaInfoMapped)

        if metaData is MetaDataMapped:
            sql = buildPartialQuery(sql, qd, qa, MetaDataMapped, QMetaData)
        else:
            andClauses = list()
            orClauses = list()
            sql = sql.outerjoin(metaData)
            sql = buildPartialQuery(sql, qd, qa, MetaDataMapped, QMetaData, andClauses, orClauses, append=False)
            sql = buildPartialQuery(sql, qd, qa, metaData, self.queryIndexer.queryByData[metaData.__name__], andClauses, orClauses)

    else:
            sql = self.session().query(MetaDataMapped)
            sql = sql.outerjoin(MetaInfoMapped, MetaDataMapped.Id == MetaInfoMapped.MetaData)
            sql = sql.add_entity(MetaInfoMapped)

            andClauses = list()
            orClauses = list()

            if metaInfo is MetaInfoMapped:
                sql = buildPartialQuery(sql, qi, qa, MetaInfoMapped, QMetaInfo, andClauses, orClauses, append=False)
            else:
                sql = sql.outerjoin(metaInfo)
                sql = buildPartialQuery(sql, qi, qa, MetaInfoMapped, QMetaInfo, andClauses, orClauses, append=False)
                sql = buildPartialQuery(sql, qi, qa, metaInfo, self.queryIndexer.queryByInfo[metaInfo.__name__], andClauses, orClauses, append=False)

            if metaData is MetaDataMapped:
                sql = buildPartialQuery(sql, qd, qa, MetaDataMapped, QMetaData, andClauses, orClauses)
            else:
                sql = sql.outerjoin(metaData)
                sql = buildPartialQuery(sql, qd, qa, MetaDataMapped, QMetaData, andClauses, orClauses, append=False)
                sql = buildPartialQuery(sql, qd, qa, metaData, self.queryIndexer.queryByData[metaData.__name__], andClauses, orClauses)

    return sql

