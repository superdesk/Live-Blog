'''
Created on Aug 23, 2012

@package: superdesk media archive
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Ioan v. Pocol

SQL Alchemy based implementation for the video data API. 
'''

from ally.container.ioc import injected
from ally.container.support import setup
from superdesk.media_archive.core.spec import IQueryIndexer
from ally.container import wire
from superdesk.media_archive.api.video_info import IVideoInfoService, QVideoInfo
from superdesk.media_archive.core.impl.meta_service_base import MetaInfoServiceBaseAlchemy
from superdesk.media_archive.api.video_data import QVideoData, IVideoDataService
from superdesk.media_archive.meta.video_data import VideoDataMapped,\
    VideoDataEntry, META_TYPE_KEY
from superdesk.media_archive.meta.video_info import VideoInfoMapped,\
    VideoInfoEntry
from superdesk.media_archive.core.impl.query_service_creator import ISearchProvider
from ally.api.validate import validate


# --------------------------------------------------------------------

@injected
@setup(IVideoInfoService, name='videoInfoService')
@validate(VideoInfoMapped)
class VideoInfoServiceAlchemy(MetaInfoServiceBaseAlchemy, IVideoInfoService):
    '''
    @see: IVideoInfoService
    '''
    
    queryIndexer = IQueryIndexer;wire.entity('queryIndexer')
    # The query indexer manages the query related information about plugins in order to be able to support the multi-plugin queries
    searchProvider = ISearchProvider; wire.entity('searchProvider')
    # The search provider that will be used to manage all search related activities
    videoDataService = IVideoDataService; wire.entity('videoDataService')
    #The correspondent meta data service for video

    def __init__(self):
        assert isinstance(self.queryIndexer, IQueryIndexer), 'Invalid IQueryIndexer %s' % self.queryIndexer
        assert isinstance(self.searchProvider, ISearchProvider), 'Invalid search provider %s' % self.searchProvider
        assert isinstance(self.videoDataService, IVideoDataService), 'Invalid video meta data service %s' % self.videoDataService

        MetaInfoServiceBaseAlchemy.__init__(self, VideoInfoMapped, QVideoInfo, VideoDataMapped, QVideoData, 
                                            self.searchProvider, self.videoDataService, META_TYPE_KEY)
        
        self.queryIndexer.register(VideoInfoEntry, QVideoInfo, VideoDataEntry, QVideoData, META_TYPE_KEY)
        
