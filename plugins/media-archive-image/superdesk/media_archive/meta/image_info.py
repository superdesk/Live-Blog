'''
Created on Apr 18, 2012

@package: superdesk media archive
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Contains the SQL alchemy meta for media image info API.
'''

from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import String
from superdesk.media_archive.meta.meta_info import MetaInfoMapped
from sqlalchemy.ext.declarative import declared_attr
from superdesk.meta.metadata_superdesk import Base
from superdesk.media_archive.api.image_info import ImageInfo

# --------------------------------------------------------------------

class ImageInfoDefinition:
    '''
    Provides the mapping for ImageInfo.
    '''
    __tablename__ = 'archive_image_info'
    __table_args__ = dict(mysql_engine='InnoDB', mysql_charset='utf8')

    Id = declared_attr(lambda cls: Column('fk_metainfo_id', ForeignKey(MetaInfoMapped.Id, ondelete='CASCADE'), primary_key=True))
    Caption = declared_attr(lambda cls: Column('caption', String(255), nullable=True, key='Caption'))

# --------------------------------------------------------------------

class ImageInfoEntry(Base, ImageInfoDefinition):
    '''
    Provides the mapping for ImageInfo table.
    '''

# --------------------------------------------------------------------

class ImageInfoMapped(ImageInfoDefinition, MetaInfoMapped, ImageInfo):
    '''
    Provides the mapping for ImageInfo when extending MetaInfo.
    '''
    __table_args__ = dict(ImageInfoDefinition.__table_args__, extend_existing=True)
