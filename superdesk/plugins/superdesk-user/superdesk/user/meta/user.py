'''
Created on Aug 23, 2011

@package: superdesk user
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mihai Balaceanu

Contains the SQL alchemy meta for language API.
'''

from ..api.user import User
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import String
from superdesk.person.meta.person import PersonMapped
from ally.support.sqlalchemy.mapper import validate

# --------------------------------------------------------------------

@validate
class UserMapped(PersonMapped, User):
    '''
    Provides the mapping for User entity.
    '''
    __tablename__ = 'user'
    __table_args__ = dict(mysql_engine='InnoDB', mysql_charset='utf8')

    Name = Column('name', String(20), nullable=False, unique=True)

    # Non REST model attribute --------------------------------------
    userId = Column('fk_person_id', ForeignKey(PersonMapped.Id), primary_key=True)
    # Never map over the inherited id
