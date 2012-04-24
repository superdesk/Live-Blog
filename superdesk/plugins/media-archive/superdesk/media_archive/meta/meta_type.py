'''
Created on Apr 19, 2012

@package: superdesk media archive
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Contains the SQL alchemy meta for meta type API.
'''

from ..api.meta_type import MetaType
from ally.support.sqlalchemy.mapper import mapperModel
from sqlalchemy.dialects.mysql.base import INTEGER
from sqlalchemy.schema import Table, Column
from sqlalchemy.types import String
from superdesk.meta.metadata_superdesk import meta

# --------------------------------------------------------------------

table = Table('archive_meta_type', meta,
              Column('id', INTEGER(unsigned=True), primary_key=True, key='Id'),
              Column('key', String(50), nullable=False, unique=True, key='Key'),
              mysql_engine='InnoDB', mysql_charset='utf8')

MetaType = mapperModel(MetaType, table)
