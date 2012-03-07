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
from ally.support.sqlalchemy.mapper import mapperModel, mapperQuery
from sqlalchemy.schema import Table, Column
from sqlalchemy.types import String, Integer, Enum, DateTime

# --------------------------------------------------------------------

table = Table('inter_source', meta,
              Column('id', Integer(unsigned=True), primary_key=True, key='Id'),
              Column('fk_component_id', String(255), nullable=True, key='Component'),
              Column('fk_plugin_id', String(255), nullable=True, key='Plugin'),
              Column('path', String(255), nullable=False, unique=True, key='Path'),
              Column('type', Enum(TYPE_PYTHON, TYPE_JAVA_SCRIPT), nullable=False, key='Type'),
              Column('last_modified', DateTime, nullable=False, key='LastModified'),
              )

Source = mapperModel(Source, table)
QSource = mapperQuery(QSource, Source)
