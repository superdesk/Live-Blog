'''
Created on Aug 23, 2011

@package superdesk
@copyright 2011 Sourcefabric o.p.s.
@license http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Contains the SQL alchemy meta for language API.
'''

from superdesk.language.api.language import LanguageEntity
from ally.support.sqlalchemy.mapper import mapperModel
from sqlalchemy.dialects.mysql.base import INTEGER
from sqlalchemy.schema import Table, Column
from sqlalchemy.types import String
from superdesk.meta.metadata_superdesk import meta

# --------------------------------------------------------------------

table = Table('language', meta,
              Column('id', INTEGER(unsigned=True), primary_key=True, key='Id'),
              Column('code', String(20), nullable=False, unique=True, key='Code'),
              mysql_engine='InnoDB', mysql_charset='utf8')

LanguageEntity = mapperModel(LanguageEntity, table)
