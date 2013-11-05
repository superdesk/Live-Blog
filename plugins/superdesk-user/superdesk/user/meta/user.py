'''
Created on Aug 23, 2011

@package: superdesk user
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mihai Balaceanu

Contains the SQL alchemy meta for user API.
'''

# TODO: cleanup
from ..api.user import User
from ..meta.user_type import UserTypeMapped
from sql_alchemy.support.util_meta import relationshipModel
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.sql.functions import current_timestamp
from sqlalchemy.types import String, DateTime, Boolean
from superdesk.person.meta.person import PersonMapped
from ally.api.validate import validate, ReadOnly, Mandatory

# --------------------------------------------------------------------

@validate(Mandatory(User.Password), ReadOnly(User.CreatedOn), ReadOnly(User.Active))
class UserMapped(PersonMapped, User):
    '''
    Provides the mapping for User entity.
    '''
    __tablename__ = 'user'
    __table_args__ = dict(mysql_engine='InnoDB', mysql_charset='utf8')

    Name = Column('name', String(150), nullable=False, unique=True)
    CreatedOn = Column('created_on', DateTime, nullable=False, default=current_timestamp())
    Active = Column('active', Boolean, nullable=False, default=True)
    Type = relationshipModel(UserTypeMapped.id)
    # Non REST model attribute --------------------------------------
    userId = Column('fk_person_id', ForeignKey(PersonMapped.Id, ondelete='CASCADE'), primary_key=True)
    password = Column('password', String(255), nullable=False)
