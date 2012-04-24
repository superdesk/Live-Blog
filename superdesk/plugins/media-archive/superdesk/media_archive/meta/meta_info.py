'''
Created on Apr 18, 2012

@package: superdesk media archive
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Contains the SQL alchemy meta for media meta info API.
'''

from ..api.meta_info import MetaInfo
from .meta_data import MetaData
from ally.support.sqlalchemy.mapper import mapperModel
from sqlalchemy.dialects.mysql.base import INTEGER
from sqlalchemy.schema import Table, Column, ForeignKey
from sqlalchemy.types import String
from superdesk.language.meta.language import LanguageEntity
from superdesk.meta.metadata_superdesk import meta

# --------------------------------------------------------------------

table = Table('archive_meta_info', meta,
              Column('id', INTEGER(unsigned=True), primary_key=True, key='Id'),
              Column('fk_metadata_id', ForeignKey(MetaData.Id), nullable=False, key='MetaData'),
              Column('fk_language_id', ForeignKey(LanguageEntity.Id), nullable=False, key='Language'),
              Column('title', String(255), key='Title'),
              Column('keywords', String(255), key='Keywords'),
              Column('description', String(255), key='Description'),
              mysql_engine='InnoDB', mysql_charset='utf8')

MetaInfo = mapperModel(MetaInfo, table)
