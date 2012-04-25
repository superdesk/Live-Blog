'''
Created on Apr 19, 2012

@package: superdesk media archive
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Contains the SQL alchemy meta for media meta data API.
'''

from ..api.meta_data import MetaData
from .meta_type import MetaType
from ally.support.sqlalchemy.mapper import mapperModel
from sqlalchemy.dialects.mysql.base import INTEGER
from sqlalchemy.schema import Table, Column, ForeignKey
from sqlalchemy.types import String, DateTime, Integer
from superdesk.meta.metadata_superdesk import meta

# --------------------------------------------------------------------

table = Table('archive_meta_data', meta,
              Column('id', INTEGER(unsigned=True), primary_key=True, key='Id'),
              Column('type', ForeignKey(MetaType.Id, ondelete='RESTRICT'), nullable=False, key='Type'),
              Column('reference', String(255), nullable=False, key='reference'),
              Column('size_in_bytes', Integer, nullable=False, key='SizeInBytes'),
              Column('created_on', DateTime, nullable=False, key='CreatedOn'),
              mysql_engine='InnoDB', mysql_charset='utf8')

MetaData = mapperModel(MetaData, table)
