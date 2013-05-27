'''
Created on Aug 23, 2011

@package: superdesk user
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mihai Balaceanu

Contains the SQL alchemy meta for user API.
'''

from ..api.user import User
from ally.container.binder_op import validateManaged, validateRequired
from ally.support.sqlalchemy.mapper import validate
from sqlalchemy.schema import Column, ForeignKey, UniqueConstraint
from sqlalchemy.types import String, DateTime
from superdesk.person.meta.person import PersonMapped

# --------------------------------------------------------------------

@validate(exclude=('Password', 'CreatedOn', 'DeletedOn'))
class UserMapped(PersonMapped, User):
    '''
    Provides the mapping for User entity.
    '''
    __tablename__ = 'user'
    __table_args__ = (UniqueConstraint('name', name='uix_user_name'),
                      dict(mysql_engine='InnoDB', mysql_charset='utf8'))

    Name = Column('name', String(150), nullable=False, unique=True)
    CreatedOn = Column('created_on', DateTime, nullable=False)
    DeletedOn = Column('deleted_on', DateTime)
    # Non REST model attribute --------------------------------------
    userId = Column('fk_person_id', ForeignKey(PersonMapped.Id, ondelete='CASCADE'), primary_key=True)
    password = Column('password', String(255), nullable=False)
    # Never map over the inherited id

validateRequired(UserMapped.Password)
validateManaged(UserMapped.CreatedOn)
validateManaged(UserMapped.DeletedOn)
