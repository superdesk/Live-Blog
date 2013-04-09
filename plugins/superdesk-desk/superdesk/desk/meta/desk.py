'''
Created on April 2, 2013

@package: superdesk desk
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Martin Saturka

Contains the SQL alchemy meta for desk API.
'''

from ..api.desk import Desk
from sqlalchemy.dialects.mysql.base import INTEGER
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import String, Text
from superdesk.meta.metadata_superdesk import Base
from superdesk.user.meta.user import UserMapped
from ally.support.sqlalchemy.mapper import validate

# --------------------------------------------------------------------

@validate
class DeskMapped(Base, Desk):
    '''
    Provides the mapping for Desk.
    '''
    __tablename__ = 'desk_desk'
    __table_args__ = dict(mysql_engine='InnoDB', mysql_charset='utf8')

    Id = Column('id', INTEGER(unsigned=True), primary_key=True)
    Name = Column('name', String(255), unique=True, nullable=False)
    Description = Column('description', Text, nullable=True)

# --------------------------------------------------------------------

class DeskUserMapped(Base):
    '''
    Provides the connecting of User and Desk.
    '''
    __tablename__ = 'desk_user'
    __table_args__ = dict(mysql_engine='InnoDB', mysql_charset='utf8')

    id = Column('id', INTEGER(unsigned=True), primary_key=True)
    desk = Column('fk_desk_id', ForeignKey(DeskMapped.Id, ondelete='CASCADE'), nullable=False)
    user = Column('fk_user_id', ForeignKey(UserMapped.Id, ondelete='CASCADE'), nullable=False)


