'''
Created on Apr 19, 2012

@package: superdesk media archive
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Contains the SQL alchemy meta for media image data API.
'''

from ..api.image_data import ImageData
from .meta_data import MetaDataMapped
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Integer, String
from superdesk.meta.metadata_superdesk import Base
from ally.internationalization import N_

# --------------------------------------------------------------------

META_TYPE_KEY = N_('image')
# The key used for image meta data

# --------------------------------------------------------------------

#table = Table('archive_image_data', meta,
#              Column('fk_meta_data_id', ForeignKey(MetaDataMapped.Id), primary_key=True, key='Id'),
#              Column('width', Integer, key='Width'),
#              Column('height', Integer, key='Height'),
#              Column('creation_date', String, key='CreationDate'),
#              Column('camera_make', String, key='CameraMake'),
#              Column('camera_model', String, key='CameraModel'),
#              mysql_engine='InnoDB', mysql_charset='utf8')
#
#ImageData = mapperModel(ImageData, table, inherits=MetaDataMapped)

# --------------------------------------------------------------------

class ImageData(Base, ImageData):
    '''
    Provides the mapping for MetaData.
    '''
    __tablename__ = 'archive_image_data'
    __table_args__ = dict(mysql_engine='InnoDB', mysql_charset='utf8')

    Id = Column('fk_meta_data_id', ForeignKey(MetaDataMapped.Id), primary_key=True)
    Width = Column('width', Integer)
    Height = Column('height', Integer)
    CreationDate = Column('creation_date', String)
    CameraMake = Column('camera_make', String)
    CameraModel = Column('camera_model', String)
