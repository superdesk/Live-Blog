'''
Created on Mar 5, 2012

@package: internationalization
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Contains the SQL alchemy meta for source API.
'''

from . import meta
from ..api.source import Source, QSource, TYPE_PYTHON, TYPE_JAVA_SCRIPT
from .file import File
from ally.support.sqlalchemy.mapper import mapperModel, mapperQuery
from sqlalchemy.schema import Table, Column, ForeignKey
from sqlalchemy.types import Enum

# --------------------------------------------------------------------

table = Table('inter_source', meta,
              Column('fk_file_id', ForeignKey(File.Id), primary_key=True, key='Id'),
              Column('type', Enum(TYPE_PYTHON, TYPE_JAVA_SCRIPT), nullable=False, key='Type'),
              mysql_engine='InnoDB'
              )

Source = mapperModel(Source, table, inherits=File)
QSource = mapperQuery(QSource, Source)
