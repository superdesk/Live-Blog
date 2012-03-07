'''
Created on Mar 5, 2012

@package: internationalization
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Contains the SQL alchemy meta for message API.
'''

from . import meta
from ..api.message import Message, QMessage
from .source import Source
from ally.support.sqlalchemy.mapper import mapperModel, mapperQuery
from sqlalchemy.schema import Table, Column, ForeignKey
from sqlalchemy.types import String
from sqlalchemy.dialects.mysql.base import INTEGER, VARCHAR

# --------------------------------------------------------------------

table = Table('inter_message', meta,
              Column('id', INTEGER(unsigned=True), primary_key=True, key='Id'),
              Column('fk_source_id', ForeignKey(Source.Id, ondelete='RESTRICT'), key='Source'),
              Column('locale', String(20), nullable=False, key='Locale'),
              Column('domain', String(100), nullable=False, key='Domain'),
              Column('singular', VARCHAR(255, charset='utf8'), nullable=False, key='Singular'),
              Column('plural_1', VARCHAR(255, charset='utf8'), key='plural1'),
              Column('plural_2', VARCHAR(255, charset='utf8'), key='plural2'),
              Column('plural_3', VARCHAR(255, charset='utf8'), key='plural3'),
              Column('plural_4', VARCHAR(255, charset='utf8'), key='plural4'),
              Column('context', VARCHAR(255, charset='utf8'), key='Context'),
              Column('line_number', INTEGER(unsigned=True), key='LineNumber'),
              Column('comments', String(255), key='Comments'),
              mysql_engine='InnoDB'
              )

Message = mapperModel(Message, table)
QMessage = mapperQuery(QMessage, Message)
