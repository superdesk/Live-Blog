'''
Created on Aug 23, 2012

@package: superdesk media archive
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Ioan v. Pocol

SQL Alchemy based implementation for the video data API. 
'''

from ally.cdm.spec import ICDM
from ally.container import wire
from ally.container.ioc import injected
from ally.container.support import setup
from superdesk.media_archive.api.video_data import IVideoDataService, QVideoData
from superdesk.media_archive.core.impl.meta_service_base import \
    MetaDataServiceBaseAlchemy
from superdesk.media_archive.core.spec import IMetaDataReferencer, \
    IThumbnailManager
from superdesk.media_archive.meta.video_data import VideoDataMapped
from ally.api.validate import validate

# --------------------------------------------------------------------

@injected
@setup(IVideoDataService, name='videoDataService')
@validate(VideoDataMapped)
class VideoDataServiceAlchemy(MetaDataServiceBaseAlchemy, IMetaDataReferencer, IVideoDataService):
    '''
    @see: IVideoDataService
    '''

    cdmArchiveVideo = ICDM; wire.entity('cdmArchiveVideo')
    thumbnailManager = IThumbnailManager; wire.entity('thumbnailManager')

    def __init__(self):
        assert isinstance(self.cdmArchiveVideo, ICDM), 'Invalid archive CDM %s' % self.cdmArchiveVideo
        assert isinstance(self.thumbnailManager, IThumbnailManager), 'Invalid thumbnail manager %s' % self.thumbnailManager
       
        MetaDataServiceBaseAlchemy.__init__(self, VideoDataMapped, QVideoData, self, self.cdmArchiveVideo, self.thumbnailManager)
    