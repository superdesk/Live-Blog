'''
Created on Aug 23, 2012

@package: superdesk media archive
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Ioan v. Pocol

Contains the SQL alchemy meta for media audio info API.
'''

from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import String
from superdesk.media_archive.meta.meta_info import MetaInfoMapped
from sqlalchemy.ext.declarative import declared_attr
from superdesk.meta.metadata_superdesk import Base
from superdesk.media_archive.api.audio_info import AudioInfo


# --------------------------------------------------------------------

class AudioInfoDefinition:
    '''
    Provides the mapping for AudioInfo.
    '''
    __tablename__ = 'archive_audio_info'
    __table_args__ = dict(mysql_engine='InnoDB', mysql_charset='utf8')

    Id = declared_attr(lambda cls: Column('fk_metainfo_id', ForeignKey(MetaInfoMapped.Id), primary_key=True))
    Caption = declared_attr(lambda cls: Column('caption', String(255), nullable=True, key='Caption'))

# --------------------------------------------------------------------

class AudioInfoEntry(Base, AudioInfoDefinition):
    '''
    Provides the mapping for AudioInfo table.
    '''

# --------------------------------------------------------------------

class AudioInfoMapped(AudioInfoDefinition, MetaInfoMapped, AudioInfo):
    '''
    Provides the mapping for AudioInfo when extending MetaInfo.
    '''
    __table_args__ = dict(AudioInfoDefinition.__table_args__, extend_existing=True)
