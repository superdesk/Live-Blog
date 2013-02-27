'''
Created on Aug 23, 2012

@package: superdesk media archive
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Ioan v. Pocol

Contains the SQL alchemy meta for media video data API.
'''

from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Integer, String
from sqlalchemy.ext.declarative import declared_attr
from superdesk.meta.metadata_superdesk import Base
from ally.internationalization import N_
from superdesk.media_archive.meta.meta_data import MetaDataMapped
from superdesk.media_archive.api.video_data import VideoData

# --------------------------------------------------------------------

META_TYPE_KEY = N_('video')
# The key used for video meta data

# --------------------------------------------------------------------

class VideoDataDefinition:
    '''
    Provides the mapping for VideoData definition.
    '''
    __tablename__ = 'archive_video_data'
    __table_args__ = dict(mysql_engine='InnoDB', mysql_charset='utf8')

    Id = declared_attr(lambda cls: Column('fk_metadata_id', ForeignKey(MetaDataMapped.Id), primary_key=True))
    Length = declared_attr(lambda cls: Column('length', Integer))
    VideoEncoding = declared_attr(lambda cls: Column('video_encoding', String(255)))
    Width = declared_attr(lambda cls: Column('width', Integer))
    Height = declared_attr(lambda cls: Column('height', Integer))
    VideoBitrate = declared_attr(lambda cls: Column('video_bitrate', Integer))
    Fps = declared_attr(lambda cls: Column('fps', Integer))
    AudioEncoding = declared_attr(lambda cls: Column('audio_encoding', String(255)))
    SampleRate = declared_attr(lambda cls: Column('sample_rate', Integer))
    Channels = declared_attr(lambda cls: Column('channels', String(255)))
    AudioBitrate = declared_attr(lambda cls: Column('audio_bitrate', Integer))

# --------------------------------------------------------------------

class VideoDataEntry(Base, VideoDataDefinition):
    '''
    Provides the mapping for VideoData table.
    '''

# --------------------------------------------------------------------

class VideoDataMapped(VideoDataDefinition, MetaDataMapped, VideoData):
    '''
    Provides the mapping for VideoData when extending MetaData.
    '''
    __table_args__ = dict(VideoDataDefinition.__table_args__, extend_existing=True)
