'''
Created on Aug 23, 2011

@package: superdesk user
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mihai Balaceanu

Contains the SQL alchemy meta for language API.
'''

from ..api.user import User
from ally.support.sqlalchemy.mapper import mapperModel
from sqlalchemy.schema import Table, Column, ForeignKey
from sqlalchemy.types import String
from superdesk.meta import meta
from superdesk.person.meta.person import Person

# --------------------------------------------------------------------

table = Table('user', meta,
               Column('fk_person_id', ForeignKey(Person.Id), nullable=False, primary_key=True, key='Id'),
               Column('name', String(20), nullable=False, unique=True, key='Name'),
               mysql_engine='InnoDB', mysql_charset='utf8')

# map User entity to defined table (above)
User = mapperModel(User, table, inherits=Person)
