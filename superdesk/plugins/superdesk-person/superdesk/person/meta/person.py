'''
Created on Aug 23, 2011

@package superdesk
@copyright 2011 Sourcefabric o.p.s.
@license http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mihai Balaceanu

Contains the SQL alchemy meta for language API.
'''

from ally.support.sqlalchemy.mapper import mapperModel, mapperQuery
from sqlalchemy.dialects.mysql.base import INTEGER
from sqlalchemy.schema import Table, Column, ForeignKey
from sqlalchemy.types import String
from superdesk.meta import meta
from ..api.person import Person, QPerson
from superdesk.user.meta.user import User

# --------------------------------------------------------------------

table = Table( 'person', meta,
               Column('id', INTEGER(unsigned=True), primary_key=True, key='Id'),
               Column('fk_user_id', ForeignKey(User.Id, onupdate='CASCADE', ondelete='SET_NULL'), nullable=True, key='User'),
               Column('firstname', String(20), nullable=True, unique=False, key='FirstName'),
               Column('lastname', String(20), nullable=True, unique=False, key='LastName'),
               Column('address', String(20), nullable=True, unique=False, key='Address'),
               mysql_engine='InnoDB', mysql_charset='utf8' )

# map User entity to defined table (above)
Person = mapperModel(Person, table)
# map QUser (user query) to mapped User (above)
QPerson = mapperQuery(QPerson, User)
