'''
Created on Apr 18, 2012

@package: superdesk media archive
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Contains the SQL alchemy meta for media image info API.
'''

from ..api.image_info import ImageInfo
from .meta_info import MetaInfo
from ally.container.binder_op import validateManaged
from ally.support.sqlalchemy.mapper import mapperModel
from sqlalchemy.schema import Table, Column, ForeignKey
from sqlalchemy.types import String
from superdesk.meta.metadata_superdesk import meta

# --------------------------------------------------------------------

table = Table('archive_image_info', meta,
              Column('fk_meta_info_id', ForeignKey(MetaInfo.Id), primary_key=True, key='Id'),
              Column('caption', String(255), nullable=False, key='Caption'),
              mysql_engine='InnoDB', mysql_charset='utf8')

ImageInfo = mapperModel(ImageInfo, table, exclude=['MetaData'], inherits=MetaInfo)
validateManaged(ImageInfo.MetaData)
