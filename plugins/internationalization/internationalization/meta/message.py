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
from sqlalchemy.types import String, Integer

# --------------------------------------------------------------------

table = Table('inter_message', meta,
              Column('id', Integer(unsigned=True), primary_key=True, key='Id'),
              Column('fk_source_id', ForeignKey(Source.Id, ondelete='RESTRICT'), key='Source'),
              Column('locale', String(20), nullable=False, key='Locale'),
              Column('domain', String(100), nullable=False, key='Domain'),
              Column('singular', String(255), nullable=False, key='Singular'),
              Column('plural_1', String(255), key='plural1'),
              Column('plural_2', String(255), key='plural2'),
              Column('plural_3', String(255), key='plural3'),
              Column('plural_4', String(255), key='plural4'),
              Column('context', String(255), key='Context'),
              Column('line_number', Integer(unsigned=True), key='LineNumber'),
              Column('comments', String(255), key='Comments'),
              )

Message = mapperModel(Message, table)
QMessage = mapperQuery(QMessage, Message)
