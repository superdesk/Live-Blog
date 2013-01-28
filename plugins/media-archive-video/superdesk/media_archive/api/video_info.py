'''
Created on Aug 23, 2012

@package: superdesk media archive
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Ioan v. Pocol

API specifications for media archive video info.
'''

from ally.api.config import query, service, model
from superdesk.media_archive.api.criteria import AsLikeExpressionOrdered
from superdesk.media_archive.api.meta_data import MetaData, QMetaData
from superdesk.media_archive.api.meta_info import MetaInfo, QMetaInfo, \
    IMetaInfoService
from superdesk.media_archive.api.video_data import VideoData, QVideoData

# --------------------------------------------------------------------

@model
class VideoInfo(MetaInfo):
    '''
    Provides the meta info video.
    '''
    MetaData = VideoData
    Caption = str

# --------------------------------------------------------------------

@query(VideoInfo)
class QVideoInfo(QMetaInfo):
    '''
    The query for video info model.
    '''
    caption = AsLikeExpressionOrdered

# --------------------------------------------------------------------

@service((MetaInfo, VideoInfo), (QMetaInfo, QVideoInfo), (MetaData, VideoData), (QMetaData, QVideoData))
class IVideoInfoService(IMetaInfoService):
    '''
    Provides the service methods for the meta info video.
    '''
