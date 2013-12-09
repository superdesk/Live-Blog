'''
Created on Apr 27, 2012

@package: superdesk media archive
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Base SQL Alchemy implementation to support meta type services.
'''

from ally.cdm.spec import ICDM, PathNotFound
from ally.internationalization import _
from inspect import isclass
from sql_alchemy.impl.entity import EntityGetCRUDServiceAlchemy
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm.session import Session
from superdesk.media_archive.api.meta_data import QMetaData, IMetaDataService
from superdesk.media_archive.api.meta_info import QMetaInfo
from superdesk.media_archive.core.impl.query_service_creator import \
    ISearchProvider
from superdesk.media_archive.core.spec import IMetaDataReferencer, \
    IThumbnailManager
from superdesk.media_archive.meta.meta_data import MetaDataMapped, \
    ThumbnailFormat
from superdesk.media_archive.meta.meta_info import MetaInfo, MetaInfoMapped
from superdesk.media_archive.meta.meta_type import MetaTypeMapped
from sqlalchemy.exc import OperationalError, IntegrityError
from sql_alchemy.support.util_service import SessionSupport, buildQuery, \
    buildLimits, iterateCollection
from ally.api.error import InputError

# --------------------------------------------------------------------

class MetaDataServiceBaseAlchemy(SessionSupport, IMetaDataService):
    '''
    Base SQL alchemy implementation for meta data type services.
    '''

    def __init__(self, MetaDataClass, QMetaDataClass, referencer, cdmArchive, thumbnailManager):
        '''
        Construct the meta data base service for the provided classes.

        @param MetaDataClass: class
            A class that extends MetaData meta class.
        @param QMetaDataClass: class
            A class that extends QMetaData API class.
        @param referencer: IMetaDataReferencer
            The referencer to provide the references in the meta data.
        @param cdmArchive: ICDM
            The CDM used for current media archive type
        @param thumbnailManager: IThumbnailManager
            The thumbnail manager used to manage the current media archive type    
        '''
        assert isclass(MetaDataClass) and issubclass(MetaDataClass, MetaDataMapped), \
        'Invalid meta data class %s' % MetaDataClass
        assert isclass(QMetaDataClass) and issubclass(QMetaDataClass, QMetaData), \
        'Invalid meta data query class %s' % QMetaDataClass
        assert isinstance(referencer, IMetaDataReferencer), 'Invalid referencer %s' % referencer
        assert isinstance(cdmArchive, ICDM), 'Invalid CDM %s' % self.searchProvider
        assert isinstance(thumbnailManager, IThumbnailManager), 'Invalid video meta data service %s' % thumbnailManager

        self.MetaData = MetaDataClass
        self.QMetaData = QMetaDataClass
        self.referencer = referencer
        self.cdmArchive = cdmArchive
        self.thumbnailManager = thumbnailManager

    def getById(self, id, scheme, thumbSize=None):
        '''
        @see: IMetaDataService.getById
        '''
        metaData = self.session().query(self.MetaData).get(id)
        if metaData is None: raise InputError(_('Unknown meta data'), self.MetaData.Id)
        return self.referencer.populate(metaData, scheme, thumbSize)

    def getMetaDatas(self, scheme, typeId=None, q=None, **options):
        '''
        @see: IMetaDataService.getMetaDatas
        '''
        return iterateCollection(self.buildSql(typeId, q), **options)

    # --------------------------------------------------------------------

    def delete(self, id):
        '''
        deletes the metadata and the associated media file and generated thumbnails
        '''        
        metaData = self.session().query(self.MetaData).filter(self.MetaData.Id == id).one()
        
        #delete file from CDM
        try: self.cdmArchive.remove(metaData.content)
        except PathNotFound: pass
        #delete the thumbnails
        self.thumbnailManager.deleteThumbnail(metaData.thumbnailFormatId, metaData)
        
        self.session().delete(metaData)
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

    # ----------------------------------------------------------------

    def populate(self, metaData, scheme, thumbSize=None):
        '''
        @see: IMetaDataReferencer.populate
        '''
        assert isinstance(metaData, MetaDataMapped), 'Invalid meta data %s' % metaData
        metaData.Content = self.cdmArchive.getURI(metaData.content, scheme)
        self.thumbnailManager.populate(metaData, scheme, thumbSize)

        return metaData

# --------------------------------------------------------------------

class MetaInfoServiceBaseAlchemy(EntityGetCRUDServiceAlchemy):
    '''
    Base SQL alchemy implementation for meta info type services.
    '''

    def __init__(self, MetaInfoClass, QMetaInfoClass, MetaDataClass, QMetaDataClass, searchProvider, metaDataService, type):
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
        @param metaDataService: MetaDataServiceBaseAlchemy
            The current meta data for media archive
        @param type: str
            The media archive type        
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
        assert isinstance(metaDataService, MetaDataServiceBaseAlchemy), 'Invalid meta data service %s' % metaDataService
        assert isinstance(type, str), 'Invalid media type%s' % type

        EntityGetCRUDServiceAlchemy.__init__(self, MetaInfoClass)

        self.MetaInfo = MetaInfoClass
        self.QMetaInfo = QMetaInfoClass
        self.MetaData = MetaDataClass
        self.QMetaData = QMetaDataClass
        self.searchProvider = searchProvider
        self.metaDataService = metaDataService
        self.type = type

    def getMetaInfos(self, dataId=None, languageId=None, qi=None, qd=None, **options):
        '''
        @see: IMetaInfoService.getMetaInfos
        '''
        return iterateCollection(self.buildSql(dataId, languageId, qi, qd), **options)

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
        deletes the current metaInfo from both database and search index
        if there is no other meta info, delete also the related meta data 
        '''

        metaInfo = self.session().query(self.MetaInfo).filter(self.MetaInfo.Id == id).one()    
        metaDataId = metaInfo.MetaData

        self.session().delete(metaInfo)
        self.session().commit()

        self.searchProvider.delete(id, self.type)
        
        if self.session().query(MetaInfoMapped).filter(MetaInfoMapped.MetaData == metaDataId).count() == 0:
            return self.metaDataService.delete(metaDataId)

        return True

    # ----------------------------------------------------------------

    def buildSql(self, dataId, languageId, qi, qd):
        '''
        Build the sql alchemy based on the provided data.
        '''
        sql = self.session().query(self.MetaInfo.Id)
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
