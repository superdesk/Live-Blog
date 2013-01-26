'''
Created on Apr 19, 2012

@package: superdesk media archive
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

SQL Alchemy based implementation for the meta info API.
'''

from ..api.meta_data import QMetaData
from ..api.meta_info import IMetaInfoService, QMetaInfo
from ..core.impl.meta_service_base import MetaInfoServiceBaseAlchemy
from ..meta.meta_data import MetaDataMapped
from ..meta.meta_info import MetaInfoMapped
from ally.api.extension import IterPart
from ally.container import wire
from ally.container.ioc import injected
from ally.container.support import setup
from ally.support.sqlalchemy.session import SessionSupport
from ally.support.sqlalchemy.util_service import buildQuery, buildLimits
from cdm.spec import ICDM
from superdesk.media_archive.api.meta_info import IMetaDataInfoService, \
    MetaDataInfo
from superdesk.media_archive.core.spec import IThumbnailManager, QueryIndexer

# --------------------------------------------------------------------

@injected
@setup(IMetaInfoService)
class MetaInfoServiceAlchemy(MetaInfoServiceBaseAlchemy, IMetaInfoService):
    '''
    Implementation for @see: IMetaInfoService
    '''

    queryIndexer = QueryIndexer;wire.entity('queryIndexer')

    def __init__(self):
        '''
        Construct the meta info service.
        '''
        MetaInfoServiceBaseAlchemy.__init__(self, MetaInfoMapped, QMetaInfo, MetaDataMapped, QMetaData)
        
@injected
@setup(IMetaDataInfoService)
class MetaDataInfoService (SessionSupport, IMetaDataInfoService):
    '''
    Provides the service methods for the meta data & info.
    '''
    
    cdmArchive = ICDM; wire.entity('cdmArchive')
    thumbnailManager = IThumbnailManager; wire.entity('thumbnailManager')
    
    def __init__(self):
        '''
        Construct the meta data info service.
        '''

        assert isinstance(self.cdmArchive, ICDM), 'Invalid archive CDM %s' % self.cdmArchive
        assert isinstance(self.thumbnailManager, IThumbnailManager), 'Invalid thumbnail manager %s' % self.thumbnailManager

    def getAll(self, scheme, dataId=None, languageId=None, offset=None, limit=10, qi=None, qd=None, thumbSize=None):
        '''
        Provides the meta & info info.
        '''   
        
        sql = self.session().query(MetaDataMapped, MetaInfoMapped)
        sql = sql.outerjoin(MetaInfoMapped, MetaDataMapped.Id == MetaInfoMapped.MetaData)
        
        if dataId: sql = sql.filter(MetaInfoMapped.MetaData == dataId)
        if languageId: sql = sql.filter(MetaInfoMapped.Language == languageId)
        
        if qi:
            assert isinstance(qi, QMetaInfo), 'Invalid meta info query %s' % qi
            sql = buildQuery(sql, qi, MetaInfoMapped)
            
        if qd:
            assert isinstance(qd, QMetaData), 'Invalid meta data query %s' % qd
            sql = buildQuery(sql, qd, MetaDataMapped)
            
        sql = buildLimits(sql, offset, limit)
        
        count = 0
        metaDataInfos = list()
        for row in sql.all():
            metaDataInfo = MetaDataInfo()
            
            metaDataMapped = row[0]
            metaInfoMapped = row[1]
            
            assert isinstance(metaDataMapped, MetaDataMapped), 'Invalid meta data %s' % metaDataMapped
            metaDataMapped.Content = self.cdmArchive.getURI(metaDataMapped.content, scheme)
            self.thumbnailManager.populate(metaDataMapped, scheme, thumbSize)
            
            metaDataInfo.Id = metaDataMapped.Id
            metaDataInfo.Name = metaDataMapped.Name
            metaDataInfo.Type = metaDataMapped.Type
            metaDataInfo.Content = metaDataMapped.Content
            metaDataInfo.Thumbnail = metaDataMapped.Thumbnail
            metaDataInfo.SizeInBytes = metaDataMapped.SizeInBytes
            metaDataInfo.Creator = metaDataMapped.Creator
            metaDataInfo.CreatedOn = metaDataMapped.CreatedOn
            
            metaDataInfo.Language = metaInfoMapped.Language
            metaDataInfo.Title = metaInfoMapped.Title
            metaDataInfo.Keywords = metaInfoMapped.Keywords
            metaDataInfo.Description = metaInfoMapped.Description
            
            metaDataInfos.append(metaDataInfo)
            
            count = count + 1
            
        return IterPart(metaDataInfos, count, offset, limit)        
             
