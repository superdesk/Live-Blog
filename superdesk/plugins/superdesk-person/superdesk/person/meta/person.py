'''
Created on Aug 23, 2011

@package: superdesk person
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mihai Balaceanu

Contains the SQL alchemy meta for person API.
'''

from ..api.person import Person
from ally.support.sqlalchemy.mapper import mapperModel
from sqlalchemy.dialects.mysql.base import INTEGER
from sqlalchemy.schema import Table, Column
from sqlalchemy.types import String
from superdesk.meta.metadata_superdesk import meta

# --------------------------------------------------------------------

table = Table('person', meta,
               Column('id', INTEGER(unsigned=True), primary_key=True, key='Id'),
               Column('first_name', String(255), key='FirstName'),
               Column('last_name', String(255), key='LastName'),
               Column('address', String(255), key='Address'),
               mysql_engine='InnoDB', mysql_charset='utf8')

Person = mapperModel(Person, table)
