'''
Created on Dec 21, 2012

@package: security
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Ioan v. Pocol

Contains the SQL alchemy meta for right API.
'''

from ..api.right import Right
from .metadata_security import Base
from .right_type import RightTypeMapped
from ally.support.sqlalchemy.mapper import validate
from sqlalchemy.dialects.mysql.base import INTEGER
from sqlalchemy.schema import Column, ForeignKey, UniqueConstraint
from sqlalchemy.types import String

# --------------------------------------------------------------------

@validate
class RightMapped(Base, Right):
    '''
    Provides the mapping for Right.
    '''
    __tablename__ = 'security_right'
    __table_args__ = (UniqueConstraint('fk_right_type_id', 'name', name='uix_type_name'),
                      dict(mysql_engine='InnoDB', mysql_charset='utf8'))

    Id = Column('id', INTEGER(unsigned=True), primary_key=True)
    Type = Column('fk_right_type_id', ForeignKey(RightTypeMapped.Id), nullable=False)
    Name = Column('name', String(150), nullable=False)
    Description = Column('description', String(255))

