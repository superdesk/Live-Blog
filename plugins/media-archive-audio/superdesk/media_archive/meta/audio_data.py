'''
Created on Aug 23, 2012

@package: superdesk media archive
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Ioan v. Pocol

Contains the SQL alchemy meta for media audio data API.
'''

from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Integer, String
from sqlalchemy.ext.declarative import declared_attr
from superdesk.meta.metadata_superdesk import Base
from ally.internationalization import N_
from superdesk.media_archive.meta.meta_data import MetaDataMapped
from superdesk.media_archive.api.audio_data import AudioData

# --------------------------------------------------------------------

META_TYPE_KEY = N_('audio')
# The key used for audio meta data

# --------------------------------------------------------------------

class AudioDataDefinition:
    '''
    Provides the mapping for AudioData definition.
    '''
    __tablename__ = 'archive_audio_data'
    __table_args__ = dict(mysql_engine='InnoDB', mysql_charset='utf8')

    Id = declared_attr(lambda cls: Column('fk_metadata_id', ForeignKey(MetaDataMapped.Id, ondelete='CASCADE'), primary_key=True))
    Length = declared_attr(lambda cls: Column('length', Integer))
    AudioEncoding = declared_attr(lambda cls: Column('audio_encoding', String(255)))
    SampleRate = declared_attr(lambda cls: Column('sample_rate', Integer))
    Channels = declared_attr(lambda cls: Column('channels', String(255)))
    AudioBitrate = declared_attr(lambda cls: Column('audio_bitrate', Integer))
    
    Title = declared_attr(lambda cls: Column('title', String(255)))
    Artist = declared_attr(lambda cls: Column('artist', String(255)))
    Track = declared_attr(lambda cls: Column('track', Integer))
    Album = declared_attr(lambda cls: Column('album', String(255)))
    Genre = declared_attr(lambda cls: Column('genre', String(255)))
    #Part of a compilation 1 - True, 0 - False
    Tcmp = declared_attr(lambda cls: Column('tcmp', Integer))
    AlbumArtist = declared_attr(lambda cls: Column('album_artist', String(255)))
    Year = declared_attr(lambda cls: Column('year', Integer))
    Disk = declared_attr(lambda cls: Column('disk', Integer))
    #Beats-per-minute
    Tbpm = declared_attr(lambda cls: Column('tbpm', Integer))
    Composer = declared_attr(lambda cls: Column('composer', String(255)))


# --------------------------------------------------------------------

class AudioDataEntry(Base, AudioDataDefinition):
    '''
    Provides the mapping for AudioData table.
    '''

# --------------------------------------------------------------------

class AudioDataMapped(AudioDataDefinition, MetaDataMapped, AudioData):
    '''
    Provides the mapping for AudioData when extending MetaData.
    '''
    __table_args__ = dict(AudioDataDefinition.__table_args__, extend_existing=True)
