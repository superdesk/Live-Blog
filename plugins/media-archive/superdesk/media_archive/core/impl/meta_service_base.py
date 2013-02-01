'''
Created on Apr 27, 2012

@package: superdesk media archive
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Base SQL Alchemy implementation to support meta type services.
'''

from ally.exception import InputError, Ref
from ally.internationalization import _
from ally.support.sqlalchemy.session import SessionSupport
from ally.support.sqlalchemy.util_service import buildQuery, buildLimits
from inspect import isclass
from sqlalchemy.orm.exc import NoResultFound
from superdesk.media_archive.api.meta_data import QMetaData, IMetaDataService
from superdesk.media_archive.api.meta_info import QMetaInfo
from superdesk.media_archive.core.spec import IMetaDataReferencer
from superdesk.media_archive.meta.meta_data import MetaDataMapped, ThumbnailFormat
from superdesk.media_archive.meta.meta_info import MetaInfo
from superdesk.media_archive.meta.meta_type import MetaTypeMapped
from sqlalchemy.orm.session import Session
from sql_alchemy.impl.entity import EntityGetCRUDServiceAlchemy
from superdesk.media_archive.core.impl.query_service_creator import ISearchProvider

# --------------------------------------------------------------------

class MetaDataServiceBaseAlchemy(SessionSupport, IMetaDataService):
    '''
    Base SQL alchemy implementation for meta data type services.
    '''

    def __init__(self, MetaDataClass, QMetaDataClass, referencer):
        '''
        Construct the meta data base service for the provided classes.

        @param MetaDataClass: class
            A class that extends MetaData meta class.
        @param QMetaDataClass: class
            A class that extends QMetaData API class.
        @param referencer: IMetaDataReferencer
            The referencer to provide the references in the meta data.
        @param searchProvider: ISearchProvider
            The provider that will be used for search related actions
        '''
        assert isclass(MetaDataClass) and issubclass(MetaDataClass, MetaDataMapped), \
        'Invalid meta data class %s' % MetaDataClass
        assert isclass(QMetaDataClass) and issubclass(QMetaDataClass, QMetaData), \
        'Invalid meta data query class %s' % QMetaDataClass
        assert isinstance(referencer, IMetaDataReferencer), 'Invalid referencer %s' % referencer

        self.MetaData = MetaDataClass
        self.QMetaData = QMetaDataClass
        self.referencer = referencer

    def getById(self, id, scheme, thumbSize=None):
        '''
        @see: IMetaDataService.getById
        '''
        metaData = self.session().query(self.MetaData).get(id)
        if metaData is None: raise InputError(Ref(_('Unknown meta data'), ref=self.MetaData.Id))
        return self.referencer.populate(metaData, scheme, thumbSize)

    def getMetaDatasCount(self, typeId=None, q=None):
        '''
        @see: IMetaDataService.getMetaDatasCount
        '''
        return self.buildSql(typeId, q).count()

    def getMetaDatas(self, scheme, typeId=None, offset=None, limit=None, q=None, thumbSize=None):
        '''
        @see: IMetaDataService.getMetaDatas
        '''
        sql = self.buildSql(typeId, q)
        sql = buildLimits(sql, offset, limit)
        return (self.referencer.populate(metaData, scheme, thumbSize) for metaData in sql.all())

    # --------------------------------------------------------------------

    def delete(self, id):
        '''
        needed to overwrite this because EntityCRUDServiceAlchemy.delete didn't work
        something to do with the join between the extended mapped tables
        '''
        self.session().delete(self.session().query(self.Entity).get(id))
        self.session().commit()

        return True

    # ----------------------------------------------------------------

    def buildSql(self, typeId, q):
        '''
        Build the sql alchemy based on the provided data.
        '''
        sql = self.session().query(self.MetaData)
        if typeId: sql = sql.filter(self.MetaData.typeId == typeId)
        if q:
            assert isinstance(q, self.QMetaData)
            sql = buildQuery(sql, q, self.MetaData)
        return sql

# --------------------------------------------------------------------

class MetaInfoServiceBaseAlchemy(EntityGetCRUDServiceAlchemy):
    '''
    Base SQL alchemy implementation for meta info type services.
    '''

    def __init__(self, MetaInfoClass, QMetaInfoClass, MetaDataClass, QMetaDataClass, searchProvider):
        '''
        Construct the meta info base service for the provided classes.

        @param MetaInfoClass: class
            A class that extends MetaInfo meta class.
        @param QMetaInfoClass: class
            A class that extends QMetaInfo API class.
        @param MetaDataClass: class
            A class that extends MetaData meta class.
        @param QMetaDataClass: class
            A class that extends QMetaData API class.
        @param searchProvider: ISearchProvider
            The provider that will be used for search related actions
        '''

        assert isclass(MetaInfoClass) and issubclass(MetaInfoClass, MetaInfo), \
        'Invalid meta info class %s' % MetaInfoClass
        assert isclass(QMetaInfoClass) and issubclass(QMetaInfoClass, QMetaInfo), \
        'Invalid meta info query class %s' % QMetaInfoClass
        assert isclass(MetaDataClass) and issubclass(MetaDataClass, MetaDataMapped), \
        'Invalid meta data class %s' % MetaDataClass
        assert isclass(QMetaDataClass) and issubclass(QMetaDataClass, QMetaData), \
        'Invalid meta data query class %s' % QMetaDataClass
        assert isinstance(searchProvider, ISearchProvider), 'Invalid search provider %s' % searchProvider

        EntityGetCRUDServiceAlchemy.__init__(self, MetaInfoClass)

        self.MetaInfo = MetaInfoClass
        self.QMetaInfo = QMetaInfoClass
        self.MetaData = MetaDataClass
        self.QMetaData = QMetaDataClass
        self.searchProvider = searchProvider

    def getMetaInfosCount(self, dataId=None, languageId=None, qi=None, qd=None):
        '''
        @see: IMetaInfoService.getMetaInfosCount
        '''
        return self.buildSql(dataId, languageId, qi, qd).count()

    def getMetaInfos(self, dataId=None, languageId=None, offset=None, limit=10, qi=None, qd=None):
        '''
        @see: IMetaInfoService.getMetaInfos
        '''
        sql = self.buildSql(dataId, languageId, qi, qd)
        sql = buildLimits(sql, offset, limit)
        return sql.all()

    # --------------------------------------------------------------------

    def insert(self, metaInfo):
        id = EntityGetCRUDServiceAlchemy.insert(self, metaInfo)

        metaData = self.session().query(self.MetaData).filter(self.MetaData.Id == metaInfo.MetaData).one()
        self.searchProvider.update(metaInfo, metaData)
        return id

    # --------------------------------------------------------------------

    def update(self, metaInfo):
        EntityGetCRUDServiceAlchemy.update(self, metaInfo)

        metaInfo = self.session().query(self.MetaInfo).filter(self.MetaInfo.Id == metaInfo.Id).one()
        metaData = self.session().query(self.MetaData).filter(self.MetaData.Id == metaInfo.MetaData).one()

        self.searchProvider.update(metaInfo, metaData)

    # --------------------------------------------------------------------

    def delete(self, id):
        '''
        needed to overwrite this because EntityCRUDServiceAlchemy.delete didn't work
        something to do with the join between the extended mapped tables
        '''
        self.session().delete(self.session().query(self.Entity).get(id))
        self.session().commit()

        self.searchProvider.delete(id)

        return True

    # ----------------------------------------------------------------

    def buildSql(self, dataId, languageId, qi, qd):
        '''
        Build the sql alchemy based on the provided data.
        '''
        sql = self.session().query(self.MetaInfo)
        if dataId: sql = sql.filter(self.MetaInfo.MetaData == dataId)
        if languageId: sql = sql.filter(self.MetaInfo.Language == languageId)
        if qi:
            assert isinstance(qi, self.QMetaInfo), 'Invalid meta info query %s' % qi
            sql = buildQuery(sql, qi, self.MetaInfo)
        if qd:
            assert isinstance(qd, self.QMetaData), 'Invalid meta data query %s' % qd
            sql = buildQuery(sql.join(self.MetaData), qd, self.MetaData)
        return sql

# --------------------------------------------------------------------

def metaTypeFor(session, type):
    '''
    Provides the meta type id for the type, if there is no such meta type then one will be created.

    @param session: Session
        The session used for getting the meta type.
    @param type: string
        The meta type type.
    '''
    assert isinstance(session, Session), 'Invalid session %s' % session
    assert isinstance(type, str), 'Invalid type %s' % type
    try: metaType = session.query(MetaTypeMapped).filter(MetaTypeMapped.Type == type).one()
    except NoResultFound:
        metaType = MetaTypeMapped()
        metaType.Type = type
        session.add(metaType)
        session.flush((metaType,))
    return metaType

# --------------------------------------------------------------------

def thumbnailFormatFor(session, format):
    '''
    Provides the thumbnail id for the format, if there is no such thumbnail format than one will be created.

    @param session: Session
        The session used for getting the thumbnail.
    @param format: string
        The thumbnail format.
    '''

    assert isinstance(session, Session), 'Invalid session %s' % session
    assert isinstance(format, str), 'Invalid format %s' % format
    try: thumbnail = session.query(ThumbnailFormat).filter(ThumbnailFormat.format == format).one()
    except NoResultFound:
        thumbnail = ThumbnailFormat()
        thumbnail.format = format
        session.add(thumbnail)
        session.flush((thumbnail,))
    return thumbnail
