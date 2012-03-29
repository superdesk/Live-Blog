'''
Created on Aug 23, 2011

@package superdesk
@copyright 2011 Sourcefabric o.p.s.
@license http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mihai Balaceanu

Contains the SQL alchemy meta for language API.
'''

from ally.support.sqlalchemy.mapper import mapperModel
from sqlalchemy.dialects.mysql.base import INTEGER
from sqlalchemy.schema import Table, Column
from sqlalchemy.types import String
from superdesk.meta import meta
from ..api.user import User

# --------------------------------------------------------------------

table = Table('user', meta,
               Column('id', INTEGER(unsigned=True), primary_key=True, key='Id'),
               Column('name', String(20), nullable=False, unique=True, key='Name'),
               mysql_engine='InnoDB', mysql_charset='utf8')

# map User entity to defined table (above)
User = mapperModel(User, table)
