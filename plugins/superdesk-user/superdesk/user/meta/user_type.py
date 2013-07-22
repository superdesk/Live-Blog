'''
Created on May 27, 2013

@package: superdesk user
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Martin Saturka

Contains the SQL alchemy meta for user type API.
'''

from ..api.user_type import UserType
from sqlalchemy.dialects.mysql.base import INTEGER
from sqlalchemy.schema import Column
from sqlalchemy.types import String
from superdesk.meta.metadata_superdesk import Base

# --------------------------------------------------------------------

class UserTypeMapped(Base, UserType):
    '''
    Provides the mapping for UserType.
    '''
    __tablename__ = 'user_type'
    __table_args__ = dict(mysql_engine='InnoDB')

    Key = Column('key', String(255), nullable=False, unique=True)
    # None REST model attribute --------------------------------------
    id = Column('id', INTEGER(unsigned=True), primary_key=True)
