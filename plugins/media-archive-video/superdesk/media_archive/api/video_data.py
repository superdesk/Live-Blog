'''
Created on Aug 23, 2012

@package: superdesk media archive
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Ioan v. Pocol

API specifications for media meta data video archive.
'''

from ally.api.config import query, service, model
from superdesk.media_archive.api.meta_data import MetaData, QMetaData, \
    IMetaDataService
from ally.api.criteria import AsRangeOrdered, AsLikeOrdered

# --------------------------------------------------------------------

@model
class VideoData(MetaData):
    '''
    Provides the meta data that is extracted based on the content.
    '''

    Length = int
    VideoEncoding = str
    Width = int
    Height = int
    VideoBitrate = int
    Fps = int
    AudioEncoding = str
    SampleRate = int
    Channels = str
    AudioBitrate = int

# --------------------------------------------------------------------

@query(VideoData)
class QVideoData(QMetaData):
    '''
    The query for video model.
    '''
    length = AsRangeOrdered
    videoEncoding = AsLikeOrdered
    width = AsRangeOrdered
    height = AsRangeOrdered
    videoBitrate = AsRangeOrdered
    fps = AsRangeOrdered
    audioEncoding = AsLikeOrdered
    sampleRate = AsRangeOrdered
    channels = AsLikeOrdered
    audioBitrate = AsRangeOrdered

# --------------------------------------------------------------------

@service((MetaData, VideoData), (QMetaData, QVideoData))
class IVideoDataService(IMetaDataService):
    '''
    Provides the service methods for the meta data video.
    '''
