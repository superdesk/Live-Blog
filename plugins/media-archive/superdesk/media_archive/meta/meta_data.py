'''
Created on Apr 19, 2012

@package: superdesk media archive
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Contains the SQL alchemy meta for media meta data API.
'''

from ..api.meta_data import MetaData
from .meta_type import MetaTypeMapped
from sqlalchemy.dialects.mysql.base import INTEGER
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import String, DateTime, Integer, TIMESTAMP
from superdesk.meta.metadata_superdesk import Base
from superdesk.user.meta.user import UserMapped
from ally.internationalization import N_
from sql_alchemy.support.util_meta import UtcNow, relationshipModel

# --------------------------------------------------------------------

META_TYPE_KEY = N_('other')
# The key used for simple meta data objects

# --------------------------------------------------------------------

class ThumbnailFormat(Base):
    '''
    Provides the mapping for thumbnails.
    This is not a REST model.
    '''
    __tablename__ = 'archive_thumbnail'
    __table_args__ = dict(mysql_engine='InnoDB')

    id = Column('id', INTEGER(unsigned=True), primary_key=True)
    format = Column('format', String(190), unique=True, nullable=False, doc='''
    The format for the reference of the thumbnail images in the media archive
    id = the meta data database id; name = the name of the content file; size = the key of the thumbnail size
    ''')

class MetaDataMapped(Base, MetaData):
    '''Provides the mapping for MetaData.'''
    __tablename__ = 'archive_meta_data'
    __table_args__ = dict(mysql_engine='InnoDB', mysql_charset='utf8')

    Id = Column('id', INTEGER(unsigned=True), primary_key=True)
    Name = Column('name', String(255), nullable=False)
    Type = relationshipModel(MetaTypeMapped.id)
    SizeInBytes = Column('size_in_bytes', Integer)
    CreatedOn = Column('created_on', TIMESTAMP, server_default=UtcNow(), nullable=False)
    Creator = Column('fk_creator_id', ForeignKey(UserMapped.Id), nullable=False)
    
    # None REST model attribute --------------------------------------
    thumbnailFormatId = Column('fk_thumbnail_format_id', ForeignKey(ThumbnailFormat.id, ondelete='RESTRICT'), nullable=False)
    content = Column('content', String(255))
