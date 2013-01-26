'''
Created on Aug 23, 2011

@package: superdesk security
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Nistor Gabriel

Contains the SQL alchemy meta for authentication API.
'''

from ..api.authentication import Token, Login
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import String, DateTime
from superdesk.meta.metadata_superdesk import Base
from superdesk.user.meta.user import UserMapped

# --------------------------------------------------------------------

class TokenMapped(Base, Token):
    '''
    Provides the mapping for Token authentication entity.
    '''
    __tablename__ = 'authentication_token'
    __table_args__ = dict(mysql_engine='InnoDB', mysql_charset='utf8')

    Token = Column('token', String(255), primary_key=True)

    # Non REST model attributes --------------------------------------
    requestedOn = Column('requested_on', DateTime, nullable=False)

class LoginMapped(Base, Login):
    '''
    Provides the mapping for Login entity.
    '''
    __tablename__ = 'authentication_login'
    __table_args__ = dict(mysql_engine='InnoDB', mysql_charset='utf8')

    Session = Column('session', String(255), primary_key=True)
    User = Column('fk_user_id', ForeignKey(UserMapped.userId), nullable=False)
    CreatedOn = Column('created_on', DateTime, nullable=False)
    AccessedOn = Column('accessed_on', DateTime, nullable=False)

