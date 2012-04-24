'''
Created on Apr 19, 2012

@package: superdesk media archive
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Contains the SQL alchemy meta for media image data API.
'''

from ..api.image_data import ImageData
from .meta_data import MetaData
from ally.support.sqlalchemy.mapper import mapperModel
from sqlalchemy.schema import Table, Column, ForeignKey
from sqlalchemy.types import Integer
from superdesk.meta.metadata_superdesk import meta

# --------------------------------------------------------------------

table = Table('archive_image_data', meta,
              Column('fk_meta_data_id', ForeignKey(MetaData.Id), primary_key=True, key='Id'),
              Column('width', Integer, nullable=False, key='Width'),
              Column('height', Integer, key='Height'),
              mysql_engine='InnoDB', mysql_charset='utf8')

ImageData = mapperModel(ImageData, table, inherits=MetaData)
